import pandas as pd
import sqlite3
#read excel sheets，and save to sqlite
def excel_2_sqlite(excel_file, sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    for sheet_name in pd.ExcelFile(excel_file).sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.to_sql(sheet_name, conn, if_exists='replace', index=False)
        print(f"translate {sheet_name} to sql table")

if __name__ == '__main__':
    excel_2_sqlite(excel_file='src_data/ag.xlsx', sqlite_file='dst_data/ag.db')