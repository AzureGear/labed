# Общие вспомогательные функции Azura.
import random
import re
import os
import ujson
import string
import pickle

# общие паттерны поиска
PATTERNS = {"double_underscore": r"^([^_]+)_([^_]+)",
            "one_underscore": "\d+(?=_(?!_))",  # число, после которого идет подчёркивание с чем угодно
            "any_number": "\d",  # любое число
            "any_letter": "\w"}  # любая буква


# ----------------------------------------------------------------------------------------------------------------------
def generate_random_name(length=5, letters=True, digits=True):
    """Генерация случайных имен, определенной длинны. С помощью флагов можно указать генерацию только цифр/букв"""
    letters = string.ascii_letters if letters else ''
    digits = string.digits if digits else ''
    symbols = letters + digits
    if not letters:
        return None

    random_name = ''.join(random.choice(symbols) for _ in range(length))
    return random_name


# ----------------------------------------------------------------------------------------------------------------------
def get_random_files(path, percentage, template="image", extensions=None):
    """
    Принимает каталог и указанное значение в процентах, а возвращает перечень случайных файлов из каталога,
    но не более указанного числа процентов.
    """
    all_files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]  # все файлы
    if extensions:
        filtered_files = [file for file in all_files if check_ext(file, template, extensions)]  # фильтр расширения
    else:
        filtered_files = all_files

    count_return = max(1, int(len(filtered_files) * percentage / 100))  # определяем число файлов
    random_files = random.sample(filtered_files, count_return)  # выбираем случайные файлы
    return random_files


# ----------------------------------------------------------------------------------------------------------------------
def natural_order(val):
    """Естественная сортировка"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', val)]


# ----------------------------------------------------------------------------------------------------------------------
def save_pickle(file_path, data):
    """Сохранение данных (data) словаря в файл json (json_path) с использованием модуля pickle. Запись проводится в
    бинарном режиме."""
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


# ----------------------------------------------------------------------------------------------------------------------
def load_pickle(file_path):
    """Загрузка данных типа json с поддержкой pickle из файла (file_path). Загрузка проводится в бинарном режиме."""
    with open(file_path, "rb") as file:
        data = pickle.load(file)
        return data


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
def save_txt(txt_path, data, mode='w', add_line_breaks=False):
    """Сохранение данных (data) в формате txt (txt_path), для добавления переноса строк использовать
    флаг add_line_breaks"""
    if add_line_breaks:
        for item in data:
            item += "\n"  # добавляем перенос строк

    with open(txt_path, mode) as f:
        if data == "":
            f.write(data)
            return
        for item in data:
            f.write(item)


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
def check_list(the_list, count=1):
    """Двойная проверка перечня (листа): на существование и наличие числа объектов (count)"""
    if the_list is None:  # проверка на существование...
        return False
    if len(the_list) < count:  # ...и количество
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
def check_ext(file_path, template="image", extensions=None):
    """
    Проверка окончания файла: принимает имя файла и возвращает True, если в сете расширений такое имеется.
    Есть готовые шаблоны "image", "text". Для кастомных запросов в extensions передать свой список расширений.
    """

    if template == "text" and extensions is None:
        extensions = {".log", ".txt"}
    elif template == "image" and extensions is None:
        extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".svg", ".webp"}
    if extensions is None:
        extensions = set()

    if len(extensions) > 0:
        extensions = [ext_low.lower() for ext_low in extensions]

    _, file_ext = os.path.splitext(file_path)

    return file_ext.lower() in extensions



# ----------------------------------------------------------------------------------------------------------------------
def get_files(path, types: tuple = None, deep=False):
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
                if file.lower().endswith(types):
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
def format_time(seconds, lang="en"):
    """Преобразование секунд в более удобный для восприятия формат, в зависимости от пройденного времени"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if lang == "ru":
        hour_af = "ч"
        min_af = "мин"
        sec_af = "сек"
    else:
        hour_af = "h"
        min_af = "min"
        sec_af = "sec"

    if hours > 0:
        return f"{int(hours)} {hour_af} {int(minutes)} {min_af} {int(seconds)} {sec_af} "
    elif minutes > 0:
        return f"{int(minutes)} {min_af} {int(seconds)} {sec_af}"
    else:
        return f"{int(seconds)} {sec_af}"

# ----------------------------------------------------------------------------------------------------------------------
