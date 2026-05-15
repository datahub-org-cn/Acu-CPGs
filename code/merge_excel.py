import pandas as pd
temp_dst = []
temp_data = pd.read_excel(r"src_data/中文.xlsx")
for temp_index, temp_row in temp_data.iterrows():
    temp_dict = dict(temp_row)
    keys = temp_dict.keys()
    sourceText = ""
    for key in keys:
        if key != 'sourceText':
            sourceText += f"{temp_dict[key]}||"
    temp_dict['sourceText'] = sourceText
    temp_dst.append(temp_dict)
temp_df = pd.DataFrame(temp_dst)
temp_df.to_excel(r"src_data/中文3.xlsx", index=False)