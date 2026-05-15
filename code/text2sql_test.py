import os
import pandas as pd
from openai import OpenAI
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_llm_result(user_prompt, api_list,
                   model="qwen3-235b-a22b",
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                   system_prompt="你是一个中医专家",
                   temperature=0.00001):
    try:
        api_key = random.choice(api_list)
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"```调用模型时出错: {e}"


def get_llm_result_stream(user_prompt, api_list,
                          model="qwen3-235b-a22b",
                          base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                          system_prompt="你是一个中医专家", temperature=0.00001):
    try:
        api_key = random.choice(api_list)
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,  # 启用流式输出
            extra_body={"enable_thinking": True},
            temperature=temperature,
        )

        full_content = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                content_piece = chunk.choices[0].delta.content
                full_content += content_piece  # 合并流式输出的内容片段

        return full_content  # 返回完整的结果
    except Exception as e:
        return f"调用模型时出错: {e}"


def get_struct_json_think(user_prompt, api_list,
                          model="qwen3-235b-a22b",
                          base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                          system_prompt="你是一个中医专家", temperature=0.00001):
    result_string = get_llm_result_stream(user_prompt=user_prompt,
                                          api_list=api_list,
                                          model=model,
                                          base_url=base_url,
                                          system_prompt=system_prompt,
                                          temperature=temperature)
    try:
        result_string = result_string.split("```json")[1].split("```")[0]
        result_json = json.loads(result_string)
        return result_json
    except Exception as e:
        return f"解析模型输出时出错: {e}"


def get_struct_json(user_prompt, api_list,
                    model="qwen3-235b-a22b",
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    system_prompt="你是一个中医专家",
                    temperature=0.00001):
    result_string = get_llm_result(user_prompt=user_prompt,
                                   api_list=api_list,
                                   model=model,
                                   base_url=base_url,
                                   system_prompt=system_prompt,
                                   temperature=temperature)
    print("result_String", result_string)

    try:
        result_string = result_string.split("```json")[1].split("```")[0]
        result_json = json.loads(result_string)
        return result_json
    except Exception as e:
        return {"answer": result_string}


def process_single_row(data_row, prompt_text, api_list_src, model_list, base_url, thread_id, key="sourceText"):
    """
    处理单行数据的函数
    """
    print(f"线程 {thread_id} 正在处理第 {data_row.name} 行数据")
    try:
        result_json = get_struct_json(
            user_prompt=prompt_text + dict(data_row)[key],
            api_list=api_list_src,
            model=model_list[0],
            base_url=base_url
        )
        print(f"线程 {thread_id} 处理第 {data_row.name} 行完成，结果: {result_json}")

        cur_dict = dict(data_row)
        for key in result_json.keys():
            cur_dict[key] = result_json[key]
        return cur_dict
    except Exception as e:
        print(f"线程 {thread_id} 处理第 {data_row.name} 行时出错: {e}")
        # 出错时返回原始数据
        cur_dict = dict(data_row)
        return cur_dict


def process_data_multithread(df_data, prompt_text, api_list_src, model_list, base_url, max_workers=5, key="sourceText"):
    """
    多线程处理数据
    """
    dst_data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_row = {
            executor.submit(
                process_single_row,
                data_row,
                prompt_text,
                api_list_src,
                model_list,
                base_url,
                i % max_workers + 1,
                key
            ): data_row.name for i, (_, data_row) in enumerate(df_data.iterrows())
        }

        # 收集结果
        for future in as_completed(future_to_row):
            row_index = future_to_row[future]
            try:
                result = future.result()
                dst_data.append(result)
                print(f"成功处理第 {row_index} 行数据")
            except Exception as e:
                print(f"处理第 {row_index} 行数据时发生异常: {e}")
                # 即使出错也保留原始数据
                dst_data.append(dict(df_data.loc[row_index]))

    return dst_data


def process_single_row_with_multiple_models(data_row, prompt_text, dict_config_list, thread_id, key="sourceText"):
    """
    处理单行数据并使用多个模型配置的函数
    """
    print(f"线程 {thread_id} 正在处理第 {data_row.name} 行数据")

    try:
        cur_json = dict(data_row)

        # 对每个配置调用模型
        for config in dict_config_list:
            llm_json = get_struct_json(
                user_prompt=prompt_text + dict(data_row)[key],
                api_list=config['api_list_src'],
                base_url=config['base_url'],
                model=config['model'],
                temperature=config['temperature']
            )

            # 将结果添加到当前行数据中
            for key in llm_json.keys():
                cur_json[f"{key}_{config['model']}"] = llm_json[key]

        print(f"线程 {thread_id} 处理第 {data_row.name} 行完成")
        return cur_json

    except Exception as e:
        print(f"线程 {thread_id} 处理第 {data_row.name} 行时出错: {e}")
        # 出错时返回原始数据
        return dict(data_row)


def process_data_with_multiple_models_multithread(df_data, prompt_text, dict_config_list, max_workers=10,
                                                  key="sourceText"):
    """
    多线程处理数据，每个线程处理一行数据并使用所有模型配置
    """
    dst_data = []

    # 计算最大线程数（取所有配置的最大线程数之和）
    total_max_threads = sum(config.get('max_thread_count', 2) for config in dict_config_list)
    actual_max_workers = min(max_workers, total_max_threads, len(df_data))

    print(f"使用 {actual_max_workers} 个线程处理数据")

    with ThreadPoolExecutor(max_workers=actual_max_workers) as executor:
        # 提交所有任务
        future_to_row = {
            executor.submit(
                process_single_row_with_multiple_models,
                data_row,
                prompt_text,
                dict_config_list,
                i % actual_max_workers + 1,
                key
            ): data_row.name for i, (_, data_row) in enumerate(df_data.iterrows())
        }

        # 收集结果
        for future in as_completed(future_to_row):
            row_index = future_to_row[future]
            try:
                result = future.result()
                dst_data.append(result)
                print(f"成功处理第 {row_index} 行数据")
            except Exception as e:
                print(f"处理第 {row_index} 行数据时发生异常: {e}")
                # 即使出错也保留原始数据
                dst_data.append(dict(df_data.loc[row_index]))

    return dst_data


def generate_sql(content, api_list, model, base_url):
    prompt = (f'你需要根据用户问题生成SQL语句，生成的SQL语句使用```sql 开始，使用```结束'
              f'{content}')
    return get_llm_result(prompt, api_list, model, base_url)


if __name__ == '__main__':
    # 读取API配置
    df_api = pd.read_excel(r"api_list/config_1api_v2_or.xlsx")
    dict_config_list = []
    model_list = []
    for api_index, api_row in df_api.iterrows():
        dict_config = {}
        if str(dict(api_row)['api_key']) != 'nan':
            api_list_src = str(dict(api_row)['api_key']).split('、')
        else:
            continue
        if str(dict(api_row)['model']) != 'nan':
            model = str(dict(api_row)['model'])
        else:
            continue

        if str(dict(api_row)['base_url']) != 'nan':
            base_url = str(dict(api_row)['base_url'])
        else:
            continue

        try:
            temperature = float(dict(api_row)['temperature'])
        except Exception as e:
            temperature = 0.00001

        try:
            max_thread_count = int(dict(api_row)['single_threads']) * len(api_list_src)
            if max_thread_count > int(api_row['max_threads']):
                max_thread_count = int(api_row['max_threads'])
        except Exception as e:
            max_thread_count = 2

        dict_config = {
            'api_list_src': api_list_src,
            'model': model,
            'base_url': base_url,
            'temperature': temperature,
            'max_thread_count': max_thread_count
        }
        if str(dict(api_row)['used']) == "yes":
            dict_config_list.append(dict_config)

    from baselib import read_docx_text

    # prompt_text = ""
    prompt_text = read_docx_text(r"prompt/指南SQL生成例子-a.docx")

    # 读取数据
    df_data = pd.read_excel(r"src_data/测试问题.xlsx")
    dst = []
    for df_idx, df_row in df_data.iterrows():
        cur_dict = dict(df_row)
        for m_c in dict_config_list:
            print(m_c)
            import datetime
            start_time = datetime.datetime.now()
            model = m_c['model']
            base_url = m_c['base_url']
            result = get_llm_result(user_prompt=prompt_text.replace("{content}", str(dict(df_row)['question'])),
                                    api_list=m_c['api_list_src'],
                                    base_url=base_url,
                                    model=model
                                    )
            # if "\nGuideline title:" in result:
            #     start = result.index("Guideline title:")
            #     if start > 0:
            #         result = result[start:]
            #
            # if "\n指南名称：" in result:
            #     start = result.index("指南名称：")
            #     if start > 0:
            #         result = result[start:]
            # cur_dict[f"{model}_answer"] = result
            if "```sql" in result:
                list1 = result.split("```sql")

                cur_dict[f"{model}_answer"] = list1[-1].split("```")[0].strip().replace("\n", "")
                for idx in range(0, 5):
                    cur_dict[f"{model}_answer"] = cur_dict[f"{model}_answer"] .replace("  ", " ")
                print(cur_dict[f"{model}_answer"])
            else:
                cur_dict[f"{model}_answer"] = result
                print(result)
            end_time = datetime.datetime.now()
            cur_dict[f"{model}_time"] = (end_time - start_time).total_seconds()
            print(f"{model}_time: {(end_time - start_time).total_seconds()} 秒")
        dst.append(cur_dict)

    df = pd.DataFrame(dst)
    df.to_excel(r"dst_data/SQL测试-z5_10.xlsx", index=False)

