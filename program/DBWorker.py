import psycopg2
from tkinter import messagebox
import csv

class DBWorker:

    def add_new_data(self, file_paths, station_code):
        self.file_paths = file_paths

        self.connect_to_db()
        self.insert_new_data(file_paths, station_code)
        self.close_connection()

    column_mapping = {
            "YYYY": "year_",
            "m": "month_",
            "d": "day_",
            "h": "hour_",
            "fmin": "fmin",
            "foEs": "foes",
            "h'Es": "hhes",
            "f30": "f30"
        }

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

    def insert_new_data(self, file_paths, station_code):
        try:
            for file_path in file_paths:
                with open(file_path, "r") as file:
                    reader = csv.reader(file)

                    # Считываем заголовок
                    header = next(reader)
                    header = [col.strip() for col in header]  # Удаляем пробелы

                    # Определяем, какие столбцы есть в файле
                    columns_in_db = [self.column_mapping[col] for col in header if col in self.column_mapping]

                    if not columns_in_db:
                        raise ValueError("Файл не содержит допустимых столбцов для вставки.")

                    # Проверяем, есть ли f30
                    has_f30 = "f30" in self.column_mapping and "f30" in header

                    # Обработка строк данных
                    for row in reader:
                        # Преобразуем "NaN" в None (NULL)
                        row = [None if value == "NaN" else value for value in row]

                        # Извлекаем ключевые поля
                        year = row[header.index("YYYY")]
                        month = row[header.index("m")]
                        day = row[header.index("d")]
                        hour = row[header.index("h")] if "h" in header else None

                        # Вставка в solar_activity, если есть f30
                        if has_f30:
                            f30_value = row[header.index("f30")]
                            self.cursor.execute("""
                                INSERT INTO solar_activity (year_, month_, day_, f30)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT (year_, month_, day_)
                                DO UPDATE SET f30 = EXCLUDED.f30;
                            """, (year, month, day, f30_value))

                        # Вставка в data
                        columns_to_insert = [
                        col for col in columns_in_db if col not in ["f30", "year_", "month_", "day_", "hour_"]]
                        if columns_to_insert:
                            columns_string = "station, year_, month_, day_, hour_, " + ", ".join(columns_to_insert)
                            placeholders = ", ".join(["%s"] * (len(columns_to_insert) + 5))

                            data_to_insert = [station_code, year, month, day, hour] + [
                            row[header.index(col)] for col in header if col in self.column_mapping and col not in ["f30", "YYYY", "m", "d", "h"]]

                            # Вставляем данные в таблицу data
                            print(row)
                            print(columns_string)
                            print(placeholders)
                            print(columns_to_insert)
                            print(data_to_insert)
                            self.cursor.execute(f"""
                                INSERT INTO data ({columns_string})
                                VALUES ({placeholders})
                                ON CONFLICT (station, year_, month_, day_, hour_)
                                DO UPDATE SET {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_to_insert)};
                            """, data_to_insert)

            self.conn.commit()
            messagebox.showinfo("Добавление файлов", "Все файлы успешно добавлены в базу данных")
        except (Exception, psycopg2.DatabaseError) as error:
            messagebox.showerror("Ошибка", f"Ошибка вставки данных: {error}")
            self.conn.rollback()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
