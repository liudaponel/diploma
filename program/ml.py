import numpy as np
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.layers import LSTM, Dense, Dropout
from keras._tf_keras.keras.optimizers import Adam

# Подключение к базе данных
def load_data(station_code=None):
    conn = psycopg2.connect(
        host="localhost",    # Адрес сервера
        database="ionosphere_db",  # Название базы данных
        user="postgres",    # Имя пользователя
        password="123"  # Пароль пользователя
    )
    query = """
        SELECT year_, month_, day_, hour_, foEs, hhEs, fmin, station
        FROM data
    """
    if station_code:
        query += f" WHERE station = '{station_code}'"

    df = pd.read_sql(query, conn)
    conn.close()
    
    return df

# Преобразование временных данных (месяцы и часы в циклический вид)
def preprocess_data(df):
    # Проверяем, что нужные столбцы присутствуют
    required_columns = ["year_", "month_", "day_", "hour_"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Отсутствуют необходимые столбцы: {required_columns}")

    # Убираем пропущенные значения
    df = df.dropna(subset=required_columns)

    # Преобразуем столбцы в числовой формат
    df[required_columns] = df[required_columns].apply(pd.to_numeric, errors='coerce')

    # Проверяем, что данные корректны
    if df[required_columns].isnull().any().any():
        raise ValueError("Некорректные данные в столбцах year_, month_, day_ или hour_")

    # Создаем timestamp
    try:
        df["timestamp"] = pd.to_datetime(df[["year_", "month_", "day_", "hour_"]])
    except Exception as e:
        raise ValueError(f"Ошибка при создании timestamp: {e}")

    # Сортируем по времени
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    print("hello")

    # Добавляем синусоиду для цикличных признаков
    df["month_sin"] = np.sin(2 * np.pi * df["month_"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month_"] / 12)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour_"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour_"] / 24)

    # Убираем ненужные колонки
    df = df.drop(columns=["year_", "month_", "day_", "hour_", "station", "timestamp"])

    return df

# Создание последовательностей для LSTM
def create_sequences(data, seq_length=48):
    sequences, targets = [], []
    for i in range(len(data) - seq_length):
        sequences.append(data[i : i + seq_length])
        targets.append(data.iloc[i + seq_length])  # Предсказание следующего шага
    return np.array(sequences), np.array(targets)

# Определение модели
def build_lstm_model(input_shape):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25, activation="relu"),
        Dense(input_shape[1], activation="linear")  # Выходные параметры
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
    return model

# Функция анализа SHAP (интерпретация модели)
def interpret_model(model, X_train):
    explainer = shap.Explainer(model, X_train[:100])  # Выбираем небольшой подмножество для анализа
    shap_values = explainer(X_train[:100])

    # Отображаем график важности признаков
    shap.summary_plot(shap_values, X_train[:100], feature_names=list(df.columns))

# Основной процесс обучения
def train_and_analyze(station_code=None):
    df = load_data(station_code)
    df = preprocess_data(df)

    # Нормализация данных
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    # Создание данных для LSTM
    seq_length = 48  # Используем 48 часов истории для следующего слоя
    X, y = create_sequences(df_scaled, seq_length)
    
    # Разделяем на обучающую и тестовую выборки
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Создаем и обучаем модель
    model = build_lstm_model(input_shape=(seq_length, X.shape[2]))
    model.fit(X_train, y_train, epochs=20, batch_size=16, validation_data=(X_test, y_test))

    # Анализ важности признаков
    interpret_model(model, X_train)

    return model, scaler, df

# Запуск обучения (можно указать конкретную станцию)
model, scaler, df = train_and_analyze(station_code="NS355")
