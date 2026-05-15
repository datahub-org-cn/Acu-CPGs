from docx import Document
import os

def read_docx_text(file_path):
    try:
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return None


def read_docx_to_paragraphs(file_path, separator='--------------------'):
    """
    Reads a docx file and returns a list of paragraphs.
    """
    text = read_docx_text(file_path)
    if text is None:
        return None
    text_list = text.split(separator)
    return text_list


def read_xlsx_to_dictlist(file_path):
    import pandas as pd
    df = pd.read_excel(file_path)
    dict_list = df.to_dict('records')
    return dict_list


def read_xlsx_column_to_list(file_path, column_name):
    import pandas as pd
    df = pd.read_excel(file_path)
    column_list = df[column_name].tolist()
    return column_list





def is_file_locked(filepath):
    try:
        # 尝试以独占模式打开文件
        fd = os.open(filepath, os.O_WRONLY | os.O_EXCL)
        os.close(fd)
        return False  # 文件未被占用
    except OSError:
        return True  # 文件被占用或无法访问
