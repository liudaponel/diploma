import pandas as pd
import numpy as np

# Чтение Excel-файла
excel_file = "files_excel_to_cvs/1985h_my.xlsx"
df = pd.read_excel(excel_file)

pd.set_option('future.no_silent_downcasting', True)
df.replace("ССС", np.nan, inplace=True)
df.replace("CCC", np.nan, inplace=True)

columns_to_int = ["YYYY", "m", "d", "h", "h'Es"]
for col in columns_to_int:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Сохранение в CSV с разделителем-запятой
csv_file = "files_excel_to_cvs/output/1985h_my.cvs"
df.to_csv(csv_file, index=False, sep=',', na_rep='NaN')
