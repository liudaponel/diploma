import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from pathlib import Path
from datetime import datetime

def parse(file_paths):
    data_fmin = {}
    data_foEs = {}
    data_hEs = {}

    # Функция для парсинга строк
    def parse_line(line):
        parts = line.strip().split(',')
        year, month, day, hour = parts[:4]
        data_value = parts[4] if len(parts) > 4 and parts[4].strip() else "NaN"  # Заменяем пустые строки на NaN
        return (int(year), int(month), int(day), int(hour)), data_value

    # Определяем, какой файл какой, и считываем в соответствующий словарь
    for file_path in file_paths:
        file_name = Path(file_path).stem
        with open(file_path, 'r') as f:
            for line in f:
                if file_name.endswith("fmin"):
                    key, value = parse_line(line)
                    data_fmin[key] = value
                elif file_name.endswith("foEs"):
                    key, value = parse_line(line)
                    data_foEs[key] = value
                elif file_name.endswith("hEs"):
                    key, value = parse_line(line)
                    data_hEs[key] = value

    # Список уникальных ключей для объединенного файла
    all_keys = set(data_fmin.keys()) | set(data_foEs.keys()) | set(data_hEs.keys())

    # Создаем папку output, если её нет
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Запись данных в объединённый файл в папке output
    timestamp = datetime.now().strftime("%Y.%m.%d_%H-%M")
    output_file_path = output_dir / f"combined_data_{timestamp}.csv"

    # Запись данных в объединённый файл
    with open(output_file_path, "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["YYYY", "m", "d", "h", "h'Es"])

        for key in sorted(all_keys):
            year, month, day, hour = key
            hEs = data_hEs.get(key, "NaN")
            writer.writerow([year, month, day, hour, hEs])
    
    messagebox.showinfo("Преобразование файлов", "Выбранные файлы объеденены в один. Он находится в папке output")

    

# Функция для открытия проводника и выбора файлов
def open_file_dialog():
    file_paths = filedialog.askopenfilenames(title="Выберите файлы", filetypes=(("Все файлы", "*.*"), ("Нужные файлы", "*.cvs")))
    if file_paths:  # Проверка, были ли выбраны файлы
        parse(file_paths)

window = tk.Tk()
window.title("Предобработчик данных")
window.geometry("300x200")

newDataButton = tk.Button(window, text="Добавить файлы", command=open_file_dialog)
newDataButton.pack(pady=20)
window.mainloop()
