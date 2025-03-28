import tkinter as tk
from tkinter import messagebox, filedialog
from DBWorker import DBWorker
from DataAnalyzer import DataAnalyzer

dbWorker = DBWorker()

# Функция для открытия проводника и выбора файлов
def open_file_dialog():
    code = station_code.get()
    if not code.strip():
        messagebox.showwarning("Ошибка", "Поле ввода пустое! Введите код станции.")
    else:
        file_paths = filedialog.askopenfilenames(title="Выберите файлы", filetypes=(("Все файлы", "*.*"), ("Нужные файлы", "*.csv")))
        if file_paths:  # Проверяем, выбрал ли пользователь файлы
                dbWorker.add_new_data(file_paths, code)

def start_analysis():
    code = station_code.get()
    if not code.strip():
        messagebox.showwarning("Ошибка", "Поле ввода пустое! Введите код станции.")
    else:
        check_values = [var.get() for var in check_vars]
        analyzer = DataAnalyzer(check_values, code)
        analyzer.start()

window = tk.Tk()
window.title("Анализ спорадического слоя")
window.geometry("600x450")

newDataButton = tk.Button(window, text="Добавить новые данные в базу", command=open_file_dialog)
newDataButton.pack(pady=5)

# Поле ввода кода станции
label = tk.Label(window, text="Введите код станции:")
label.pack(pady=5)
station_code = tk.Entry(window)
station_code.pack(pady=5)

# Область с чекбоксами
checkbox_frame = tk.LabelFrame(window, text="Выберите, что хотите рассчитать", padx=10, pady=10)
checkbox_frame.pack(pady=10)

# Список переменных для чекбоксов (каждый чекбокс имеет свою переменную)
check_vars = [tk.IntVar() for _ in range(9)]

# Создание чекбоксов с расположением их в две колонки
tk.Checkbutton(checkbox_frame, text=f"PEs от года и цикла СА", variable=check_vars[0]).grid(row=0, column=0, sticky='w')
tk.Checkbutton(checkbox_frame, text=f"Только для foEs > 3", variable=check_vars[5]).grid(row=0, column=1, sticky='w')

tk.Checkbutton(checkbox_frame, text=f"PEs от сезона (4 графика)", variable=check_vars[1]).grid(row=1, column=0, sticky='w')
tk.Checkbutton(checkbox_frame, text=f"Только для foEs > 3", variable=check_vars[6]).grid(row=1, column=1, sticky='w')

tk.Checkbutton(checkbox_frame, text=f"Зависимость PEs по часам от месяца и года", variable=check_vars[7]).grid(row=2, column=0, sticky='w')
tk.Checkbutton(checkbox_frame, text=f"Зависимость PEs от месяца и года", variable=check_vars[8]).grid(row=3, column=0, sticky='w')

tk.Checkbutton(checkbox_frame, text=f"foEsav от года и цикла СА", variable=check_vars[2]).grid(row=4, column=0, sticky='w')
tk.Checkbutton(checkbox_frame, text=f"foEsav от сезона (4 графика)", variable=check_vars[3]).grid(row=5, column=0, sticky='w')

tk.Checkbutton(checkbox_frame, text=f"Вероятность появления на конкретной высоте внутри месяца", variable=check_vars[4]).grid(row=6, column=0, sticky='w')

startButton = tk.Button(window, text="Рассчитать", command=start_analysis)
startButton.pack(pady=5)

window.mainloop()

# + вероятность появления в каждом месяце за каждый час за конкретный год. по ох - месяцы за все годы (от 1 до 12*43 и раз в 12 
# + пунктов пометить какой год), по оу - час, а вероятность цветом

# + вероятность появления в году каждом за каждый час - по оси ох - год, по оу - час, а вероятность цветом

# + среднее для месяца по каждому году - также по ох - месяцы (1, 2, ..., 12, 13 (за след.год), ...), по оу - вероятность
# + либо - по ох - год, по оу - месяц, цветом вероятность

# + высоты от 100 до 115 в один график, от 115(вкл) до 135 и тд в несколько графиков. По оси х - вероятность, по оси у - месяц (за все годы)

# + отредачить данные за 1989 и 1990, проверить в целом все данные

# + добавить номер ионосферной станции. Включить поле для вставки данных - введите код станции 

# + добавить выгрузку данных, по которым были рассчеты, в файл csv или xlsx

# + чета не так с высотами

# - написать нейронку

# написать документацию для выбираемых пунктов и входных данных

# + время, UT - подпись

# + в 7 ячейку добавить столбец год в выгрузку данных

# + неправильно считается foEsav от года и цикла СА - там случайно вероятность