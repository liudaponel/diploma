import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

# Подключение к базе данных через SQLAlchemy
def load_data(station_code=None):
    engine = create_engine("postgresql://postgres:123@localhost/ionosphere_db")

    query = """
        SELECT year_, month_, day_, hour_, foes, hhes, fmin, station
        FROM data
    """
    if station_code:
        query += f" WHERE station = '{station_code}'"

    df = pd.read_sql(query, engine)
    return df

# Преобразование временных данных (месяцы и часы в циклический вид)
def preprocess_data(df):
    required_columns = ["year_", "month_", "day_", "hour_"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Отсутствуют необходимые столбцы: {required_columns}")

    df = df.dropna(subset=required_columns)
    df[required_columns] = df[required_columns].astype(int)

    # Преобразование времени в циклический формат
    df["month_sin"] = np.sin(2 * np.pi * df["month_"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month_"] / 12)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour_"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour_"] / 24)

    df = df.drop(columns=["year_", "month_", "day_", "hour_", "station"])

    return df

def interpret_model(model, X_train, X_train_flatten):
    # Создаём объект объяснителя SHAP
    explainer = shap.KernelExplainer(model.predict, X_train)
    
    # Получаем SHAP-значения
    shap_values = explainer.shap_values(X_train[:100])
    
    # Усредняем SHAP-значения по времени
    shap_values_mean = np.mean(shap_values, axis=1)
    
    # Создаём график summary_plot
    shap.summary_plot(shap_values_mean, X_train_flatten, plot_type="dot")

    # Получаем текущий объект оси для дальнейших изменений
    ax = plt.gca()

    # Добавляем подписи осей
    ax.set_xlabel('SHAP значение', fontsize=12)
    ax.set_ylabel('Признаки', fontsize=12)

    # Добавляем легенду (если используется цвет для отображения значений признаков)
    sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(vmin=X_train_flatten.min().min(), vmax=X_train_flatten.max().max()))
    sm.set_array([])  # Нужен пустой массив для маппера
    plt.colorbar(sm, label="Значение признаков")

    # Показываем график
    plt.show()

def train_and_analyze(station_code=None):
    df = load_data(station_code)
    df_raw = df.copy()  # Сохраняем исходные данные для целевых переменных

    df = preprocess_data(df)  # Преобразуем данные для нейронной сети

    # Удаление строк с NaN значениями в обеих таблицах (признаки и целевые переменные)
    df_raw = df_raw.dropna(subset=["foes", "hhes", "fmin"])  # Убираем строки с NaN в целевых переменных
    df = df.loc[df_raw.index]  # Убираем строки из признаков, которые не входят в df_raw

    # Масштабирование данных
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    # Разделение на признаки и целевые переменные
    X = df_scaled  # Все признаки
    y = df_raw[["foes", "hhes", "fmin"]]  # Целевые переменные (не масштабируемые)

    # Разделение на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Обучаем MLP
    model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=1000, early_stopping=True)
    model.fit(X_train, y_train)

    # Интерпретация модели (SHAP)
    interpret_model(model, X_train.values, X_train.values)

    # Выводим корреляцию между признаками и целевыми переменными
    correlation_matrix = df_raw.corr()  # Используем исходные данные для корреляции
    print("Correlation matrix:")
    print(correlation_matrix)

    # Визуализация корреляционной матрицы
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation matrix")
    plt.show()

    return model, scaler, df_raw

# Запуск
model, scaler, df = train_and_analyze(station_code="NS355")

