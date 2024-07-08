# Общие вспомогательные функции.
import re
import os

# ----------------------------------------------------------------------------------------------------------------------
import ujson


# ----------------------------------------------------------------------------------------------------------------------

def natural_order(val):  # естественная сортировка
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', val)]


# ----------------------------------------------------------------------------------------------------------------------
def load(file_path):
    """Загрузка данных типа json из файла (file_path)"""
    try:
        with open(file_path, 'r') as f:
            data = ujson.load(f)
            return data
    except ujson.JSONDecodeError:
        print(f"Файл {file_path} пустой, либо содержит некорректные данные.")
        return None


# ----------------------------------------------------------------------------------------------------------------------

def save(json_path, data, mode='w'):
    """Сохранение данных (data) в файл json (json_path)"""
    with open(json_path, mode) as f:
        ujson.dump(data, f)


# ----------------------------------------------------------------------------------------------------------------------

def check_file(file):
    """Двойная проверка на наличие файла или директории"""
    if file is None:  # проверка на существование...
        return False
    if not os.path.exists(file):  # ...и открытие
        return False
    return True


# ----------------------------------------------------------------------------------------------------------------------

def check_files(args):
    """Двойная проверка на наличие файлов, если принимаем список"""
    if args is None:  # проверка на существование...
        return False
    if not os.path.exists(args[0]):  # ...и открытие
        return False
    return True


# ----------------------------------------------------------------------------------------------------------------------

def get_files(path, types: list = None, deep=False):
    """
    Возвращает перечень всех файлов, заданного расширения (types) из каталога (path). Для рекурсивного погружения
    в каталог используется флаг (deep)
    """
    all_files = True
    if types:
        all_files = False

    return_files = []  # перечень возвращаемых файлов с заданными (или нет) расширениями
    for root, dirs, files in os.walk(path):
        for file in files:
            if all_files:
                relative_path = os.path.normpath(os.path.join(root, file))
                return_files.append(relative_path)
            else:
                if file.lower().endswith(tuple(types)):
                    relative_path = os.path.normpath(os.path.join(root, file))
                    return_files.append(relative_path)
        if not deep:  # если поиск по субдиректориям False
            return return_files  # сразу возвращаем перечень файлов
    return return_files


# ----------------------------------------------------------------------------------------------------------------------
def get_file_line(filename, n):
    """
    Возвращает данные из определенной строки файла
    """
    if not check_file(filename):
        return None

    with open(filename, 'r') as file:
        lines = file.readlines()
        if n < 1 or n > len(lines):
            return None
        return lines[n - 1].strip()

# ----------------------------------------------------------------------------------------------------------------------
