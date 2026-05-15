import sqlite3
import pandas as pd
import os

def query_knee_osteoarthritis(query, db_path="dst_data/ag.db"):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

if __name__ == "__main__":
    src_file = "dst_data/SQL测试-z5_10.xlsx"
    dst_file = "dst_data/SQL测试-z5_10-命中情况.xlsx"

    # 检查文件是否存在
    if not os.path.exists(src_file):
        raise FileNotFoundError(f"源文件不存在：{src_file}")

    df = pd.read_excel(src_file)
    print(f"读取 {src_file}，共 {len(df)} 条记录")

    dict_list = df.to_dict('records')
    dst = []

    for i, dict_v in enumerate(dict_list):
        cur_dict = dict_v.copy()
        for key in dict_v.keys():
            if "answer" in key:
                sql_statement = dict_v[key]
                try:
                    result = query_knee_osteoarthritis(sql_statement)
                    cur_dict[f"{key}_hit"] = "yes" if not result.empty else "no"
                except Exception as e:
                    print(f"[{i}] 执行 {key} 出错：{e}")
                    cur_dict[f"{key}_hit"] = "error"
        dst.append(cur_dict)

    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
    df_out = pd.DataFrame(dst)
    df_out.to_excel(dst_file, index=False)


