import psycopg2
from tkinter import messagebox
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from datetime import datetime

class DataAnalyzer:
    def __init__(self, check_values, station_code):
        self.check_values = check_values
        self.station_code = station_code
    
    def start(self):
        self.connect_to_db()
        self.analyze_data()
        self.close_connection()
    
    def connect_to_db(self):
        try:
            # Подключение к базе данных PostgreSQL
            self.conn = psycopg2.connect(
                host="localhost",    # Адрес сервера
                database="ionosphere_db",  # Название базы данных
                user="postgres",    # Имя пользователя
                password="123"  # Пароль пользователя
            )
            self.cursor = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            messagebox.showerror("Ошибка", f"Ошибка подключения к базе данных: {error}")
    
    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def analyze_data(self):
        # Выполняем действия в зависимости от состояния чекбоксов
        if self.check_values[0] == 1:
            if self.check_values[5] == 0:
                self.calculate_pes_from_year_and_cycle()
            else:
                self.high_foEs_calculate_pes_from_year_and_cycle()
        if self.check_values[1] == 1:
            if self.check_values[6] == 0:
                self.calculate_pes_from_season()
            else:
                self.high_foEs_calculate_pes_from_season()
        if self.check_values[2] == 1:
            self.calculate_foesav_from_year_and_cycle()
        if self.check_values[3] == 1:
            self.calculate_foesav_from_season()
        if self.check_values[4] == 1:
            self.calculate_pes_by_hes()
        if self.check_values[7] == 1:
            self.calculate_pes_from_hours()
        if self.check_values[8] == 1:
            self.calculate_PEs_avg_all_months()

    def calculate_pes_from_year_and_cycle(self):
        query = """
        WITH solar_avg AS (
            SELECT 
                year_, 
                AVG(f30) AS avg_f30  -- Среднегодовой индекс солнечной активности
            FROM solar_activity
            GROUP BY year_
        )
        SELECT 
            d.year_,
            AVG(CASE WHEN d.foes IS NOT NULL THEN 1.0 ELSE 0 END) AS avg_pes, -- Среднегодовая вероятность PEs
            sa.avg_f30  -- Среднегодовой индекс солнечной активности
        FROM data d
        LEFT JOIN solar_avg sa ON d.year_ = sa.year_
        WHERE station = %s AND d.fmin IS NOT NULL
        GROUP BY d.year_, sa.avg_f30
        ORDER BY d.year_;"""

        self.cursor.execute(query, (self.station_code,))
        data = self.cursor.fetchall()

        # Выгрузка данных в Excel
        df = pd.DataFrame(data, columns=['Год', 'Среднегодовые PEs', 'Индекс солнечной активности'])
        self.uploadData(df, "PEs_year_cycle")

        years = [row[0] for row in data]
        avg_pes = [row[1] for row in data]
        avg_solar_index = [row[2] for row in data]

        fig, ax1 = plt.subplots()

        # Первая линия - PEs
        color = 'tab:blue'
        ax1.set_xlabel('Годы')
        ax1.set_ylabel('Среднегодовые PEs', color=color)
        ax1.plot(years, avg_pes, color=color, marker='o', label="Среднегодовые PEs")
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.legend(loc="upper left")

        # Вторая линия - Индекс солнечной активности
        ax2 = ax1.twinx()  # Создаём вторую ось y
        color = 'tab:orange'
        ax2.set_ylabel('Индекс солнечной активности', color=color)
        ax2.plot(years, avg_solar_index, color=color, marker='s', linestyle='--', label="Индекс СА")
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.legend(loc="upper right")

        fig.tight_layout()
        plt.title("Зависимость PEs от года и индекса солнечной активности")
        plt.grid(True)
        plt.show()

    def high_foEs_calculate_pes_from_year_and_cycle(self):
        query = """
        WITH solar_avg AS (
            SELECT 
                year_, 
                AVG(f30) AS avg_f30  -- Среднегодовой индекс солнечной активности
            FROM solar_activity
            GROUP BY year_
        )
        SELECT 
            d.year_,
            AVG(CASE WHEN d.foes IS NOT NULL AND foes > 3 THEN 1.0 ELSE 0 END) AS avg_pes, -- Среднегодовая вероятность PEs
            sa.avg_f30  -- Среднегодовой индекс солнечной активности
        FROM data d
        LEFT JOIN solar_avg sa ON d.year_ = sa.year_
        WHERE station = %s AND d.fmin IS NOT NULL
        GROUP BY d.year_, sa.avg_f30
        ORDER BY d.year_;"""

        self.cursor.execute(query, (self.station_code,))
        data = self.cursor.fetchall()

        # Выгрузка данных в Excel
        df = pd.DataFrame(data, columns=['Год', 'Среднегодовые PEs', 'Индекс солнечной активности'])
        self.uploadData(df, "PEs_year_cycle_hight_foEs")

        years = [row[0] for row in data]
        avg_pes = [row[1] for row in data]
        avg_solar_index = [row[2] for row in data]

        fig, ax1 = plt.subplots()

        # Первая линия - PEs
        color = 'tab:blue'
        ax1.set_xlabel('Годы')
        ax1.set_ylabel('Среднегодовые PEs', color=color)
        ax1.plot(years, avg_pes, color=color, marker='o', label="Среднегодовые PEs")
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.legend(loc="upper left")

        # Вторая линия - Индекс солнечной активности
        ax2 = ax1.twinx()  # Создаём вторую ось y
        color = 'tab:orange'
        ax2.set_ylabel('Индекс солнечной активности', color=color)
        ax2.plot(years, avg_solar_index, color=color, marker='s', linestyle='--', label="Индекс СА")
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.legend(loc="upper right")

        fig.tight_layout()
        plt.title("Зависимость PEs от года и индекса солнечной активности")
        plt.grid(True)
        plt.show()

    def calculate_pes_from_season(self):
        seasons = {
            "Зима": [12, 1, 2],
            "Весна": [3, 4, 5],
            "Лето": [6, 7, 8],
            "Осень": [9, 10, 11]
        }
        results = {}
        try:
            for season_name, months in seasons.items():
                # Формируем условие для зимы (учёт перехода года для декабря)
                if season_name == "Зима":
                    query = """
                        SELECT CASE 
                                WHEN month_ = 12 THEN year_ + 1
                                ELSE year_
                            END AS winter_year,
                            COUNT(*) AS total,
                            SUM(CASE WHEN foes IS NOT NULL THEN 1 ELSE 0 END) AS non_null_count
                        FROM data
                        WHERE station = %s AND fmin IS NOT NULL AND month_ IN (12, 1, 2)
                        GROUP BY winter_year
                        ORDER BY winter_year;
                    """
                else:
                    # Запрос данных для остальных сезонов
                    query = f"""
                        SELECT year_,
                            COUNT(*) AS total,
                            SUM(CASE WHEN foes IS NOT NULL THEN 1 ELSE 0 END) AS non_null_count
                        FROM data
                        WHERE station = %s AND fmin IS NOT NULL AND month_ IN ({', '.join(map(str, months))})
                        GROUP BY year_
                        ORDER BY year_;
                    """

                # Выполняем запрос
                self.cursor.execute(query, (self.station_code,))
                rows = self.cursor.fetchall()

                # Считаем вероятность появления
                years = []
                probabilities = []
                for row in rows:
                    year, total, non_null_count = row
                    years.append(int(year))
                    probabilities.append(non_null_count / total if total > 0 else 0)

                # Сохраняем результаты для сезона
                results[season_name] = (years, probabilities)

                # Сохраняем данные в Excel
                df = pd.DataFrame({
                    'Год': years,
                    'Вероятность': probabilities
                })
                self.uploadData(df, f"pes_{season_name}")

            # Строим графики
            fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
            fig.suptitle("Вероятность появления по сезонам", fontsize=16)

            for ax, (season_name, (years, probabilities)) in zip(axes.flat, results.items()):
                ax.plot(years, probabilities, marker='o')
                ax.set_title(season_name)
                ax.set_xlabel("Годы")
                ax.set_ylabel("Вероятность")
                ax.grid(True)

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.show()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при выполнении расчета: {e}")

    def high_foEs_calculate_pes_from_season(self):
        seasons = {
            "Зима": [12, 1, 2],
            "Весна": [3, 4, 5],
            "Лето": [6, 7, 8],
            "Осень": [9, 10, 11]
        }
        results = {}
        try:
            for season_name, months in seasons.items():
                # Формируем условие для зимы (учёт перехода года для декабря)
                if season_name == "Зима":
                    query = """
                        SELECT CASE 
                                WHEN month_ = 12 THEN year_ + 1
                                ELSE year_
                            END AS winter_year,
                            COUNT(*) AS total,
                            SUM(CASE WHEN foes IS NOT NULL AND foes > 3 THEN 1 ELSE 0 END) AS non_null_count
                        FROM data
                        WHERE station = %s AND fmin IS NOT NULL AND month_ IN (12, 1, 2)
                        GROUP BY winter_year
                        ORDER BY winter_year;
                    """
                else:
                    # Запрос данных для остальных сезонов
                    query = f"""
                        SELECT year_,
                            COUNT(*) AS total,
                            SUM(CASE WHEN foes IS NOT NULL AND foes > 3 THEN 1 ELSE 0 END) AS non_null_count
                        FROM data
                        WHERE station = %s AND fmin IS NOT NULL AND month_ IN ({', '.join(map(str, months))})
                        GROUP BY year_
                        ORDER BY year_;
                    """

                # Выполняем запрос
                self.cursor.execute(query, (self.station_code,))
                rows = self.cursor.fetchall()

                # Считаем вероятность появления
                years = []
                probabilities = []
                for row in rows:
                    year, total, non_null_count = row
                    years.append(int(year))
                    probabilities.append(non_null_count / total if total > 0 else 0)

                # Сохраняем результаты для сезона
                results[season_name] = (years, probabilities)

                # Сохраняем данные в Excel
                df = pd.DataFrame({
                    'Год': years,
                    'Вероятность': probabilities
                })
                self.uploadData(df, f"pes_{season_name}_hight_foEs")

            # Строим графики
            fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
            fig.suptitle("Вероятность появления по сезонам", fontsize=16)

            for ax, (season_name, (years, probabilities)) in zip(axes.flat, results.items()):
                ax.plot(years, probabilities, marker='o')
                ax.set_title(season_name)
                ax.set_xlabel("Годы")
                ax.set_ylabel("Вероятность")
                ax.grid(True)

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.show()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при выполнении расчета: {e}")

    def calculate_foesav_from_year_and_cycle(self):
        query = """
        WITH solar_avg AS (
            SELECT 
                year_, 
                AVG(f30) AS avg_f30  -- Среднегодовой индекс солнечной активности
            FROM solar_activity
            GROUP BY year_
        )
        SELECT 
            d.year_,
            AVG(CASE WHEN d.foes IS NOT NULL THEN 1.0 ELSE 0 END) AS avg_pes, -- Среднегодовая вероятность PEs
            sa.avg_f30  -- Среднегодовой индекс солнечной активности
        FROM data d
        LEFT JOIN solar_avg sa ON d.year_ = sa.year_
        WHERE station = %s AND d.fmin IS NOT NULL
        GROUP BY d.year_, sa.avg_f30
        ORDER BY d.year_;"""

        self.cursor.execute(query, (self.station_code,))
        data = self.cursor.fetchall()

        # Выгрузка данных в Excel
        df = pd.DataFrame(data, columns=['Год', 'Среднегодовые foEs', 'Индекс солнечной активности'])
        self.uploadData(df, "foEsAv_year_cycle")

        years = [row[0] for row in data]
        avg_pes = [row[1] for row in data]
        avg_solar_index = [row[2] for row in data]

        fig, ax1 = plt.subplots()

        # Первая линия - PEs
        color = 'tab:blue'
        ax1.set_xlabel('Годы')
        ax1.set_ylabel('Среднегодовые f0Es', color=color)
        ax1.plot(years, avg_pes, color=color, marker='o', label="Среднегодовые foEs")
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.legend(loc="upper left")

        # Вторая линия - Индекс солнечной активности
        ax2 = ax1.twinx()  # Создаём вторую ось y
        color = 'tab:orange'
        ax2.set_ylabel('Индекс солнечной активности', color=color)
        ax2.plot(years, avg_solar_index, color=color, marker='s', linestyle='--', label="Индекс СА")
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.legend(loc="upper right")

        fig.tight_layout()
        plt.title("Зависимость foEs от года и индекса солнечной активности")
        plt.grid(True)
        plt.show()

    def calculate_foesav_from_season(self):
        seasons = {
            "Зима": [12, 1, 2],
            "Весна": [3, 4, 5],
            "Лето": [6, 7, 8],
            "Осень": [9, 10, 11]
        }
        results = {}
        try:
            for season_name, months in seasons.items():
                # Формируем условие для зимы (учёт перехода года для декабря)
                if season_name == "Зима":
                    query = """
                        SELECT CASE 
                                WHEN month_ = 12 THEN year_ + 1
                                ELSE year_
                            END AS winter_year,
                            AVG(foes::numeric) AS avg_foes
                        FROM data
                        WHERE station = %s AND fmin IS NOT NULL AND month_ IN (12, 1, 2) AND foes IS NOT NULL
                        GROUP BY winter_year
                        ORDER BY winter_year;
                    """
                else:
                    # Запрос данных для остальных сезонов
                    query = f"""
                        SELECT year_,
                            AVG(foes::numeric) AS avg_foes
                        FROM data
                        WHERE station = %s AND fmin IS NOT NULL AND month_ IN ({', '.join(map(str, months))}) AND foes IS NOT NULL
                        GROUP BY year_
                        ORDER BY year_;
                    """

                # Выполняем запрос
                self.cursor.execute(query, (self.station_code,))
                rows = self.cursor.fetchall()

                # Сохраняем годы и средние значения foEs
                years = []
                averages = []
                for row in rows:
                    year, avg_foes = row
                    years.append(int(year))
                    averages.append(float(avg_foes) if avg_foes is not None else 0)

                # Сохраняем результаты для сезона
                results[season_name] = (years, averages)

                # Сохраняем данные в Excel
                df = pd.DataFrame({
                    'Год': years,
                    'Среднее foEs': averages
                })
                self.uploadData(df, f"foEsAvg_{season_name}")

            # Строим графики
            fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
            fig.suptitle("Среднее значение foEs по сезонам", fontsize=16)

            for ax, (season_name, (years, averages)) in zip(axes.flat, results.items()):
                ax.plot(years, averages, marker='o')
                ax.set_title(season_name)
                ax.set_xlabel("Годы")
                ax.set_ylabel("Среднее значение foEs")
                ax.grid(True)

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.show()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при выполнении расчета: {e}")

    def calculate_pes_by_hes(self):
        try:
            query = """
                WITH total_counts AS (
                    SELECT 
                        month_,
                        COUNT(*) AS total_count
                    FROM data
                    WHERE station = %s AND fmin IS NOT NULL
                    GROUP BY month_
                ),
                hhes_counts AS (
                    SELECT 
                        month_,
                        COUNT(*) FILTER (WHERE hhes BETWEEN 100 AND 110) AS count_100_110,
                        COUNT(*) FILTER (WHERE hhes BETWEEN 115 AND 130) AS count_115_130,
                        COUNT(*) FILTER (WHERE hhes BETWEEN 135 AND 150) AS count_135_150,
                        COUNT(*) FILTER (WHERE hhes BETWEEN 155 AND 170) AS count_155_170,
                        COUNT(*) FILTER (WHERE hhes BETWEEN 175 AND 190) AS count_175_190
                    FROM data
                    WHERE station = %s AND fmin IS NOT NULL AND hhes IS NOT NULL
                    GROUP BY month_
                )
                SELECT 
                    t.month_,
                    COALESCE(f.count_100_110, 0) * 1.0 / NULLIF(t.total_count, 0) AS prob_100_110,
                    COALESCE(f.count_115_130, 0) * 1.0 / NULLIF(t.total_count, 0) AS prob_115_130,
                    COALESCE(f.count_135_150, 0) * 1.0 / NULLIF(t.total_count, 0) AS prob_135_150,
                    COALESCE(f.count_155_170, 0) * 1.0 / NULLIF(t.total_count, 0) AS prob_155_170,
                    COALESCE(f.count_175_190, 0) * 1.0 / NULLIF(t.total_count, 0) AS prob_175_190
                FROM total_counts t
                LEFT JOIN hhes_counts f 
                ON t.month_ = f.month_
                ORDER BY t.month_;"""
            
            # Выполняем SQL-запрос
            self.cursor.execute(query, (self.station_code, self.station_code))
            rows = self.cursor.fetchall()

            # Загружаем данные в DataFrame
            df = pd.DataFrame(rows, columns=["month", "prob_100_110", "prob_115_130", "prob_135_150", "prob_155_170", "prob_175_190"])
            df["month"] = pd.to_numeric(df["month"], errors="coerce")

            # Сохраняем данные в Excel
            long_df = df.melt(id_vars=["month"], var_name="Диапазон высот", value_name="Вероятность")
            height_ranges = {
                "prob_100_110": "100-110 км",
                "prob_115_130": "115-130 км",
                "prob_135_150": "135-150 км",
                "prob_155_170": "155-170 км",
                "prob_175_190": "175-190 км"
            }
            long_df["Диапазон высот"] = long_df["Диапазон высот"].replace(height_ranges)
            self.uploadData(long_df, "height_PEs")

            # Задаем диапазоны высот для подписей
            height_ranges = ["100-110", "115-130", "135-150", "155-170", "175-190"]

            # Создаем 5 графиков
            fig, axes = plt.subplots(5, 1, figsize=(10, 20), sharex=True)

            for i, column in enumerate(["prob_100_110", "prob_115_130", "prob_135_150", "prob_155_170", "prob_175_190"]):
                axes[i].plot(df["month"], df[column], marker="o", linestyle="-", label=f"Высота {height_ranges[i]} км")
                axes[i].set_ylabel("Вероятность")
                axes[i].legend()
                axes[i].grid(True)

            # Общие подписи осей
            axes[-1].set_xlabel("Месяц")
            plt.suptitle("Вероятность появления слоя на конкретной высоте по месяцу", fontsize=16)

            # Отображаем графики
            plt.show()
        
        except Exception as error:
            print(f"Ошибка: {error}")

    def calculate_pes_from_hours(self):
        query = """
            WITH total_counts AS (
                SELECT 
                    (year_ - (SELECT MIN(year_) FROM data)) * 12 + month_ AS month_index,
                    hour_,
                    COUNT(*) AS total_count
                FROM data
                WHERE station = %s AND fmin IS NOT NULL
                GROUP BY month_index, hour_
            ),
            foEs_counts AS (
                SELECT 
                    (year_ - (SELECT MIN(year_) FROM data)) * 12 + month_ AS month_index,
                    hour_,
                    COUNT(*) AS foEs_count
                FROM data
                WHERE station = %s AND fmin IS NOT NULL AND foes IS NOT NULL
                GROUP BY month_index, hour_
            )
            SELECT 
                t.month_index,
                t.hour_,
                COALESCE(f.foEs_count, 0) * 1.0 / NULLIF(t.total_count, 0) AS probability
            FROM total_counts t
            LEFT JOIN foEs_counts f 
            ON t.month_index = f.month_index AND t.hour_ = f.hour_
            ORDER BY t.month_index, t.hour_;
            """

        # Выполняем запрос и загружаем данные в DataFrame
        self.cursor.execute(query, (self.station_code, self.station_code))
        rows = self.cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Номер месяца", "Час", "Вероятность"])
        df["Вероятность"] = pd.to_numeric(df["Вероятность"], errors="coerce")

        # Выгрузка данных в Excel
        self.uploadData(df, "PEs_hours")

        # Переводим данные в pivot-таблицу для heatmap
        heatmap_data = df.pivot(index="Час", columns="Номер месяца", values="Вероятность")

        # Получаем список уникальных годов из базы данных
        query_years = "SELECT DISTINCT year_ FROM data ORDER BY year_;"
        self.cursor.execute(query_years)
        years_list = [row[0] for row in self.cursor.fetchall()]

        # Привязываем реальные годы к шкале месяцев
        years_positions = list(range(1, len(years_list) * 12 + 1, 12))  # Каждые 12 месяцев
        years_labels = [str(year) for year in years_list]  # Метки для оси X

        # Отображаем тепловую карту
        plt.figure(figsize=(16, 8))
        sns.heatmap(heatmap_data, cmap="coolwarm", cbar_kws={'label': 'Вероятность появления'}, linewidths=0.5)

        # Подписи осей
        plt.xlabel("Год", fontsize=14)
        plt.ylabel("Час", fontsize=14)
        plt.title("Вероятность появления слоя по месяцам и часам", fontsize=16)

        # Устанавливаем реальные года на оси X
        plt.xticks(years_positions, labels=years_labels, rotation=45)
        plt.gca().invert_yaxis()

        plt.show()

        self.calculate_pes_by_years_and_hours()

    def calculate_pes_by_years_and_hours(self):
        query = """
            WITH total_counts AS (
                SELECT 
                    year_ AS year,
                    hour_ AS hour,
                    COUNT(*) AS total_count
                FROM data
                WHERE station = %s AND fmin IS NOT NULL
                GROUP BY year_, hour_
            ),
            foEs_counts AS (
                SELECT 
                    year_ AS year,
                    hour_ AS hour,
                    COUNT(*) AS foEs_count
                FROM data
                WHERE station = %s AND fmin IS NOT NULL AND foes IS NOT NULL
                GROUP BY year_, hour_
            )
            SELECT 
                t.year,
                t.hour,
                COALESCE(f.foEs_count, 0) * 1.0 / NULLIF(t.total_count, 0) AS probability
            FROM total_counts t
            LEFT JOIN foEs_counts f 
            ON t.year = f.year AND t.hour = f.hour
            ORDER BY t.year, t.hour;"""
        
        # Выполняем SQL-запрос
        self.cursor.execute(query, (self.station_code, self.station_code))
        rows = self.cursor.fetchall()

        # Загружаем данные в DataFrame
        df = pd.DataFrame(rows, columns=["Год", "Час", "Вероятность"])
        df["Вероятность"] = pd.to_numeric(df["Вероятность"], errors="coerce")

        # Выгрузка данных в Excel
        self.uploadData(df, "PEs_years_hours")

        # Переводим в pivot-таблицу для heatmap
        heatmap_data = df.pivot(index="Час", columns="Год", values="Вероятность")

        # Размер графика
        plt.figure(figsize=(16, 8))

        # Тепловая карта вероятности
        sns.heatmap(heatmap_data, cmap="coolwarm", cbar_kws={'label': 'Вероятность появления'}, linewidths=0.5)

        # Настройка подписей осей
        plt.xlabel("Год", fontsize=14)
        plt.ylabel("Час", fontsize=14)
        plt.title("Вероятность появления слоя по годам и часам", fontsize=16)

        # Переворачиваем ось Y (часы от 0 до 23 снизу вверх)
        plt.gca().invert_yaxis()

        # Отображаем график
        plt.show()

    def calculate_PEs_avg_all_months(self):
        query = """
            WITH total_counts AS (
                SELECT 
                    year_ AS year,
                    month_ AS month,
                    COUNT(*) AS total_count
                FROM data
                WHERE station = %s AND fmin IS NOT NULL
                GROUP BY year_, month_
            ),
            foEs_counts AS (
                SELECT 
                    year_ AS year,
                    month_ AS month,
                    COUNT(*) AS foEs_count
                FROM data
                WHERE station = %s AND fmin IS NOT NULL AND foes IS NOT NULL
                GROUP BY year_, month_
            )
            SELECT 
                t.year,
                t.month,
                COALESCE(f.foEs_count, 0) * 1.0 / NULLIF(t.total_count, 0) AS probability
            FROM total_counts t
            LEFT JOIN foEs_counts f 
            ON t.year = f.year AND t.month = f.month
            ORDER BY t.year, t.month;"""
        
        # Выполняем SQL-запрос
        self.cursor.execute(query, (self.station_code, self.station_code))
        rows = self.cursor.fetchall()

        # Загружаем данные в DataFrame
        df = pd.DataFrame(rows, columns=["Год", "Месяц", "Вероятность"])
        df["Вероятность"] = pd.to_numeric(df["Вероятность"], errors="coerce")

        # Выгрузка данных в Excel
        self.uploadData(df, "PEs_avg_all_months")

        # Переводим в pivot-таблицу для heatmap
        heatmap_data = df.pivot(index="Месяц", columns="Год", values="Вероятность")

        # Размер графика
        plt.figure(figsize=(16, 8))

        # Тепловая карта вероятности
        sns.heatmap(heatmap_data, cmap="coolwarm", cbar_kws={'label': 'Вероятность появления'}, linewidths=0.5)

        # Настройка подписей осей
        plt.xlabel("Год", fontsize=14)
        plt.ylabel("Месяц", fontsize=14)
        plt.title("Вероятность появления слоя по месяцам и годам", fontsize=16)

        # Инвертируем ось Y (чтобы месяцы шли сверху вниз от января к декабрю)
        plt.gca().invert_yaxis()

        # Отображаем график
        plt.show()

    def uploadData(self, df, fileName):
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y.%m.%d_%H-%M")
        output_file_path = output_dir / f"{fileName}_{timestamp}.xlsx"
        df.to_excel(output_file_path, index=False, engine='openpyxl')