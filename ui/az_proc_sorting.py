from PyQt5 import QtWidgets, QtGui, QtCore
from utils import format_time, helper
import numpy as np
from itertools import combinations
import random
import time
import re


# ----------------------------------------------------------------------------------------------------------------------
# Данные для тестирования
test_synth_small = {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mama": [2, 0, 0, 3], "brother": [2, 3, 1, 3],
                    "pet": [0, 2, 1, 2], "grandpa": [1, 1, 2, 3], "fish": [1, 0, 3, 3]}

sort_data_15 = {0: [3, 2, 0, 3, 2], 1: [1, 3, 1, 1, 0], 2: [2, 0, 0, 3, 0], 3: [2, 3, 1, 3, 2],
                4: [0, 2, 1, 2, 0], 5: [1, 1, 2, 3, 0], 6: [1, 0, 3, 3, 3], 7: [2, 3, 3, 2, 1],
                8: [2, 0, 1, 3, 3], 9: [2, 1, 1, 3, 1], 10: [2, 2, 2, 3, 0], 11: [0, 2, 0, 1, 1],
                12: [1, 0, 1, 2, 2], 13: [2, 0, 3, 2, 0], 14: [0, 1, 0, 2, 3]}

test_synth_40_small = {0: [8, 11, 11], 1: [4, 2, 1], 2: [5, 6, 6], 3: [9, 11, 7], 4: [3, 0, 5], 5: [12, 12, 12],
                       6: [3, 9, 7], 7: [3, 0, 10], 8: [9, 1, 10], 9: [1, 4, 7], 10: [1, 11, 12], 11: [10, 2, 7],
                       12: [4, 2, 5], 13: [1, 1, 12], 14: [7, 12, 10], 15: [4, 11, 11], 16: [12, 2, 1], 17: [8, 0, 3],
                       18: [0, 5, 4],
                       19: [8, 9, 10], 20: [4, 12, 5], 21: [4, 1, 7], 22: [12, 5, 8], 23: [12, 12, 4], 24: [2, 9, 11],
                       25: [12, 0, 2], 26: [2, 5, 0], 27: [10, 1, 7], 28: [0, 12, 8], 29: [2, 8, 3], 30: [4, 6, 0],
                       31: [8, 4, 9], 32: [3, 8, 1], 33: [8, 0, 6], 34: [11, 4, 12], 35: [8, 8, 0], 36: [7, 11, 5],
                       37: [1, 9, 7], 38: [7, 6, 2], 39: [4, 11, 9]}

sort_data_20 = {0: [0, 1, 1, 0], 1: [3, 1, 0, 3], 2: [1, 0, 1, 2], 3: [4, 1, 2, 0], 4: [5, 4, 0, 2], 5: [0, 1, 2, 4],
                6: [5, 0, 0, 2], 7: [0, 0, 4, 2], 8: [2, 0, 2, 2], 9: [4, 0, 2, 1], 10: [5, 1, 3, 4], 11: [4, 1, 3, 0],
                12: [1, 3, 4, 0], 13: [0, 4, 5, 5], 14: [3, 5, 0, 2], 15: [3, 4, 4, 1], 16: [0, 3, 3, 2],
                17: [5, 4, 0, 3], 18: [5, 1, 4, 2], 19: [0, 4, 1, 2]}

test_synth_20_big = {0: [6, 10, 7, 12, 12, 11, 1, 10, 0, 4, 3, 11, 6, 12, 12, 6, 4, 11, 0, 11, 2, 4, 2, 0, 1, 0, 2, 7],
                     1: [8, 11, 5, 10, 3, 6, 10, 3, 2, 6, 5, 1, 11, 7, 11, 11, 4, 1, 9, 11, 0, 1, 8, 6, 5, 12, 7, 4],
                     2: [6, 6, 0, 2, 9, 4, 11, 9, 11, 8, 1, 1, 9, 3, 7, 3, 11, 6, 1, 0, 12, 0, 8, 9, 2, 10, 1, 5],
                     3: [7, 5, 0, 3, 9, 3, 1, 2, 6, 0, 10, 8, 3, 2, 7, 9, 0, 8, 10, 7, 7, 6, 4, 4, 0, 1, 5, 3],
                     4: [8, 0, 8, 7, 5, 4, 1, 1, 6, 4, 4, 4, 11, 10, 8, 5, 9, 5, 8, 6, 11, 8, 0, 9, 8, 6, 3, 7],
                     5: [5, 5, 0, 7, 5, 5, 12, 8, 9, 6, 11, 10, 9, 6, 2, 0, 8, 10, 9, 4, 10, 0, 5, 1, 11, 2, 9, 7],
                     6: [4, 8, 12, 1, 6, 1, 0, 9, 0, 11, 0, 2, 10, 1, 2, 10, 4, 12, 12, 3, 5, 0, 0, 9, 6, 11, 6, 1],
                     7: [0, 9, 6, 4, 7, 4, 9, 10, 4, 11, 1, 0, 10, 12, 11, 3, 0, 4, 8, 8, 7, 5, 12, 12, 7, 2, 7, 9],
                     8: [11, 8, 9, 9, 7, 1, 12, 8, 7, 5, 11, 1, 1, 8, 9, 8, 12, 9, 10, 3, 9, 12, 0, 5, 4, 7, 10, 0],
                     9: [6, 8, 4, 9, 3, 11, 11, 7, 12, 7, 10, 2, 6, 6, 9, 5, 3, 9, 7, 2, 1, 2, 4, 0, 10, 4, 7, 2],
                     10: [7, 3, 8, 7, 3, 7, 5, 5, 5, 11, 0, 6, 12, 7, 10, 4, 1, 0, 12, 2, 9, 0, 6, 12, 2, 10, 8, 5],
                     11: [3, 3, 8, 5, 0, 5, 5, 7, 2, 4, 8, 12, 3, 3, 8, 0, 1, 5, 10, 12, 10, 11, 4, 0, 8, 3, 7, 2],
                     12: [7, 6, 7, 0, 4, 8, 0, 10, 5, 2, 6, 6, 11, 1, 5, 7, 6, 12, 10, 6, 6, 3, 3, 2, 0, 8, 7, 4],
                     13: [7, 11, 8, 11, 3, 5, 4, 1, 4, 2, 5, 8, 3, 10, 8, 3, 4, 7, 2, 0, 12, 1, 5, 6, 4, 2, 2, 7],
                     14: [3, 3, 4, 5, 12, 0, 2, 10, 11, 0, 3, 11, 5, 4, 8, 0, 3, 12, 6, 0, 6, 8, 0, 7, 1, 12, 4, 3],
                     15: [9, 5, 11, 3, 0, 12, 9, 2, 8, 1, 1, 1, 6, 5, 4, 4, 8, 6, 0, 6, 8, 11, 5, 11, 12, 1, 10, 10],
                     16: [12, 8, 5, 9, 8, 3, 6, 4, 10, 0, 0, 5, 0, 10, 5, 7, 8, 4, 9, 3, 1, 10, 2, 11, 12, 10, 7, 4],
                     17: [9, 2, 1, 8, 7, 6, 8, 3, 7, 0, 9, 3, 11, 10, 8, 7, 8, 0, 6, 9, 1, 5, 5, 5, 4, 5, 2, 4],
                     18: [11, 0, 3, 3, 8, 4, 10, 0, 6, 12, 0, 9, 8, 3, 9, 12, 9, 4, 1, 7, 11, 10, 3, 3, 6, 6, 12, 2],
                     19: [0, 6, 9, 5, 12, 9, 8, 8, 5, 8, 7, 7, 8, 9, 11, 9, 7, 11, 10, 5, 8, 4, 0, 12, 1, 3, 2, 4]}

test_real_uranium = {'08_chn_lanzhou_2022-11_000.jpg': [0, 0, 0, 0, 5, 1, 1, 0, 0, 0],
                     '08_chn_lanzhou_2022-11_001.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '08_chn_lanzhou_2022-11_002.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                     '08_chn_lanzhou_2022-11_003.jpg': [0, 0, 0, 0, 12, 1, 1, 1, 0, 0],
                     '08_chn_lanzhou_2022-11_004.jpg': [0, 0, 0, 1, 2, 0, 0, 0, 2, 0],
                     '08_chn_lanzhou_2022-11_005.jpg': [0, 0, 0, 1, 10, 0, 0, 1, 1, 0],
                     '04_ind_ratnahalli_2023-05_000.jpg': [1, 0, 0, 0, 2, 0, 1, 1, 0, 0],
                     '07_chn_hanzhun_shaanxi_2021-11_000.jpg': [0, 3, 0, 0, 15, 1, 2, 1, 0, 0],
                     '07_chn_hanzhun_shaanxi_2021-11_001.jpg': [0, 0, 0, 0, 5, 2, 2, 1, 0, 0],
                     '13_fra_georges_besse_two_here-com_000.jpg': [0, 0, 0, 0, 8, 8, 1, 0, 1, 2],
                     '13_fra_georges_besse_two_here-com_001.jpg': [0, 0, 0, 0, 6, 6, 1, 0, 0, 0],
                     '13_fra_georges_besse_two_here-com_002.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 6, 0],
                     '13_fra_georges_besse_two_here-com_003.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
                     '13_fra_georges_besse_two_here-com_004.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 3, 2],
                     '13_fra_georges_besse_two_here-com_005.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '13_fra_georges_besse_two_here-com_006.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                     '13_fra_georges_besse_two_here-com_007.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                     '13_fra_georges_besse_two_here-com_008.jpg': [0, 0, 0, 0, 0, 0, 0, 0, 3, 0],
                     '13_fra_georges_besse_two_here-com_009.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '13_fra_georges_besse_two_here-com_010.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '13_fra_georges_besse_two_here-com_011.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '13_fra_georges_besse_two_here-com_012.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '13_fra_georges_besse_two_here-com_013.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '09_chn_emeishan_2022-05_000.jpg': [1, 0, 0, 0, 4, 3, 0, 0, 0, 0],
                     '09_chn_emeishan_2022-05_001.jpg': [1, 0, 0, 0, 4, 1, 0, 0, 0, 0],
                     '01_bra_resende_2023-08_02_000.jpg': [1, 0, 0, 0, 2, 2, 1, 0, 3, 0],
                     '12_usa_nef_2019-02_001.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '10_nld_almelo_2021-05_002.jpg': [0, 0, 1, 2, 2, 0, 0, 0, 0, 0],
                     '14_jpn_rokkasho_2021-07_000.jpg': [1, 3, 0, 4, 5, 0, 1, 0, 0, 0],
                     '12_usa_nef_2019-02_000.jpg': [0, 0, 1, 0, 3, 3, 0, 0, 2, 1],
                     '03_deu_gronau_2022-04_000.jpg': [0, 0, 0, 1, 5, 5, 1, 1, 2, 0],
                     '11_pak_kahuta_2023-01_000.jpg': [0, 0, 0, 0, 4, 0, 0, 0, 0, 0],
                     '02_gbr_capenhurst_2018-03_000.jpg': [0, 0, 0, 0, 4, 2, 1, 1, 0, 0],
                     '02_gbr_capenhurst_2018-03_001.jpg': [0, 3, 0, 0, 0, 1, 0, 0, 0, 0],
                     '02_gbr_capenhurst_2018-03_005.jpg': [1, 0, 0, 1, 4, 0, 1, 0, 1, 0],
                     '02_gbr_capenhurst_2018-03_002.jpg': [0, 0, 0, 0, 16, 1, 1, 2, 4, 4],
                     '02_gbr_capenhurst_2018-03_003.jpg': [0, 0, 0, 0, 2, 2, 0, 1, 4, 4],
                     '10_nld_almelo_2021-05_001.jpg': [1, 0, 0, 2, 8, 1, 1, 1, 0, 0],
                     '02_gbr_capenhurst_2018-03_007.jpg': [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '10_nld_almelo_2021-05_000.jpg': [0, 1, 1, 1, 7, 4, 2, 2, 0, 0],
                     '02_gbr_capenhurst_2018-03_006.jpg': [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     '03_deu_gronau_2022-04_001.jpg': [0, 0, 0, 1, 7, 1, 1, 1, 0, 0],
                     '03_deu_gronau_2022-04_002.jpg': [1, 0, 0, 0, 0, 0, 1, 0, 2, 2],
                     '02_gbr_capenhurst_2018-03_004.jpg': [0, 0, 0, 1, 8, 5, 1, 0, 1, 1],
                     '01_bra_resende_bing_03_000.jpg': [1, 0, 0, 0, 2, 2, 1, 0, 3, 0]}


# ----------------------------------------------------------------------------------------------------------------------


class AzSortingDatasetDialog(QtWidgets.QWidget):
    """
    Диалоговое окно для автоматизированной сортировки датасета
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал передачи сообщения родительскому виджету
    inner_signal = QtCore.pyqtSignal(str)  # внутренний сигнал
    signal_info = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения в self.info

    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)
        self.name = "MNIST"
        self.settings = AppSettings()


# ----------------------------------------------------------------------------------------------------------------------
def generate_dict(count: int, length_val: int, max_rand: int = 3) -> dict:
    """
    Генерация тестовых словарей для проверки работы алгоритма автоматической сортировки. Аргументы:
    count - количество ключей в словаре начиная с 0
    length_val - количество столбцов в единичной записи;
    max_rand верхняя - граница случайного распределения;
    Example: result = generate_dict(40, 6, 15)
    :return: словарь с полученными случайными значениями типа {0: [0, 1, 1], 1:[2, 0, 0], ... }
    """
    result_dict = {}
    for i in range(0, count):
        result_dict[i] = [random.randint(0, max_rand) for _ in range(length_val)]
    return result_dict




# ----------------------------------------------------------------------------------------------------------------------


def get_group_objects(data_for_group, pattern=helper.PATTERNS.get("double_underscore")):
    objects = []
    for item in data_for_group:
        match = re.search(pattern, item)
        if match:
            if match.group(0) not in objects:
                objects.append(match.group(0))
    return objects


def calc_ratio(train_ratio, val_ratio):
    """Расчет и вывод статистики для выборок"""
    if len(train_ratio) != len(val_ratio):
        raise ValueError("Списки должны быть одинаковой длины")
    # на 0 делить нельзя, поэтому вводим правило, и считаем сумму/столбец для train и val
    train_percentages = [(t / (t + v)) * 100 if (t + v) != 0 else 0 for t, v in zip(train_ratio, val_ratio)]
    val_percentages = [(v / (t + v)) * 100 if (t + v) != 0 else 0 for t, v in zip(train_ratio, val_ratio)]
    return train_percentages, val_percentages


def group_data_by_pattern(data, pattern):
    """
    Объединение данных и суммация их значений по заданному шаблону.
    Example. Принимаем словарь типа {"bar": [3, 2, 0, 3], "bond": [1, 3, 1, 1], "cell": [2, 0, 0, 3]}, с шаблоном
    типа r"^." получаем словарь новых значений { "b": [4, 5, 1, 4], "c": [2, 0, 0, 3]} и словарь связанных
    ключей {"b": ["bar", "bond"], "c":["cell"]}
    """
    if not data or not pattern:
        raise ValueError("Отсутствуют данные либо шаблон")
    groups = get_group_objects(data.keys())
    if not groups:
        return None, None  # по заданному шаблону ничего не найдено

    array = np.array(list(data.values()))  # преобразуем в массив numpy значений типа [0, 1, 3, 0]
    group_data, group_keys = {}, {}  # создаем словари новых данных и ключей к ним

    for group in groups:
        key_record = []  # связанные значения
        summ_for_group = np.zeros(array.shape[1])  # сумма для группы

        for key, row_vals in zip(data.keys(), array):  # для изображений: key - имя изображения
            if key.startswith(group):
                key_record.append(key)
                summ_for_group += row_vals

        group_data[group] = summ_for_group.tolist()  # преобразуем в лист
        group_keys[group] = key_record
    return group_data, group_keys


def optimum_by_greed_with_group(data, ratio=0.8, names=["train", "val"], group_pattern=None):
    """Поиск оптимального разбиения на основе жадного алгоритма. Исходные данные data являются словарем списка
     типа: {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mom": [2, 0, 0, 3]}
     names - названия групп, по умолчанию "train", "val" (первая группа имеет распределение ratio)
     ratio - это размер отношения для выборки train от 1 до 0 (70% = 0.7)
     group_pattern - шаблон образования групп; если None то группировка не используется"""
    if group_pattern:  # есть необходимость использования групп
        group_data, group_links = group_data_by_pattern(data, group_pattern)  # упаковываем данные
        data_array = np.array(list(group_data.values()))
        keys = list(group_data.keys())
    else:
        data_array = np.array(list(data.values()))  # преобразуем в массив numpy для оптимизации
        keys = list(data.keys())  # сохраняем список ключей

    total_sums = np.sum(data_array, axis=0)  # сумма каждой колонки
    train_score = total_sums * ratio  # рассчитываем идеальное соотношение
    train_keys, val_keys = [], []  # ключи для выходных данных

    sums = np.sum(data_array, axis=1)  # считаем суммы строк
    sorted_idx = np.argsort(sums)[::-1]  # сортируем данные через индексы
    train_sums, val_sums = np.zeros(data_array.shape[1]), np.zeros(data_array.shape[1])  # нулевые матрицы для сумм

    for i in sorted_idx:  # используем жадный алгоритм для разбиения данных на отсортированных индексах
        row = data_array[i]
        if all(train_sums + row <= train_score):
            train_keys.append(keys[i])  # индексы отсортированы, но сами значения верные
            train_sums += row
        else:
            val_keys.append(keys[i])
            val_sums += row

    error = calculate_error(train_sums, val_sums, ratio)  # величина ошибки

    result = {}  # словарь выходных данных
    if group_pattern:  # если были использованы группы
        unpack_train, unpack_val = {}, {}  # имеем набор данных train и val, которые надо распаковать

        for group in train_keys:  # просматриваем список групп: '022_AUT', '030_BEL'...)
            for item in group_links[group]:  # смотрим словарь связей: {'022_AUT': "aut_01.jpg", "aut_02.jpg", ... }
                unpack_train[item] = data[item]
        for group in val_keys:
            for item in group_links[group]:
                unpack_val[item] = data[item]
        result[names[0]] = unpack_train
        result[names[1]] = unpack_val

    else:  # простой вариант
        train_dict = {key: data[key] for key in train_keys if key in data}  # списки для выходных данных train и val...
        val_dict = {key: data[key] for key in val_keys if key in data}  # ...строим по ключам через исходные "data"
        result[names[0]] = train_dict
        result[names[1]] = val_dict

    # не пробуем оптимизацию
    #  optimization_swap(result[names[0]], result[names[1]], ratio, error)

    result["ratio"] = [train_sums.tolist(), val_sums.tolist()]  # итоговое
    result["error"] = error  # значение ошибки
    return result


def calculate_error(train_sums, val_sums, ratio):
    """Расчет величины ошибки производится как модуль разницы между train и val суммами всех столбцов"""
    return np.sum(np.abs(train_sums * (1 - ratio) - val_sums * ratio))


def move_rows(train, val, row_indices):
    # Преобразуем кортеж индексов в список
    row_indices = list(row_indices)
    rows = train[row_indices]
    train = np.delete(train, row_indices, axis=0)
    val = np.vstack([val, rows])
    return train, val


def optimization_swap(train_data, val_data, ratio, input_error, max_iterations=1):
    """Попытка модификации алгоритма в задаче оптимизации результата с помощью перемещения одной, двух строк туда-сюда,
    из/в train-val. Провал. Слишком затратно по времени, при отсутствии результата."""
    array_train = np.array(list(train_data.values()))
    array_val = np.array(list(val_data.values()))
    best_error = input_error
    best_train = array_train.copy()
    best_val = array_val.copy()
    count = 0
    # формируем вариант перебора, где сначала по одной строке из train в val переносится, потом по две, потом одна из
    # train, одна из val (меняются местами); а затем аналогичная процедура и для второго массива
    for num_rows_train in range(max_iterations + 1):
        for num_rows_val in range(max_iterations + 1):
            for train_indices in combinations(range(len(array_train)), num_rows_train):
                for val_indices in combinations(range(len(array_val)), num_rows_val):
                    # сначала перемещаем строки из train в val (если необходимо)...
                    new_train, new_val = move_rows(array_train.copy(), array_val.copy(), train_indices)
                    # ...теперь (при необходимости перемещаем строки из val в train)
                    new_train, new_val = move_rows(new_val, new_train, val_indices)

                    # Считаем суммы по столбцам и ошибку
                    train_sums, val_sums = np.sum(new_train, axis=0), np.sum(new_val, axis=0)
                    error = calculate_error(train_sums, val_sums, ratio)
                    # if count % 10000 == 0:
                    #     print(f"{count} iteration")

                    if error < best_error:  # у нас есть лучшее решение
                        print(f"{count} iteration, find less error: {error}")
                        best_error = error
                        best_train = new_train
                        best_val = new_val
                    count += 1
    return best_train, best_val


# ----------------------------------------------------------------------------------------------------------------------
start_time = time.time()

file = "c:/Users/user/Dropbox/sort_info.json"
big_real_data = helper.load(file)

cur_ratio = 0.8
# result = optimum_by_greed_with_group(big_real_data, cur_ratio)
result = optimum_by_greed_with_group(unsort, cur_ratio, group_pattern=helper.PATTERNS.get("double_underscore"))
train = result["train"].values()
val = result["val"].values()
# print(big_real_data)
# train, val, count = optimum_split_for_data(unsort, 0.8, 6.5)
end_time = time.time()
sec = (end_time - start_time)  # / 3600
train_per, val_per = calc_ratio(result['ratio'][0], result['ratio'][1])
if SHOW_PRINTS:
    print(f"Обработано строк: {len(unsort.keys())}; занятое время: {format_time(sec)},"
          f"error: {result['error']:.1f};\n%t:",
          [f"{p:.0f}" for p in train_per], ";\n%v:",
          [f"{p:.0f}" for p in val_per])
    print()
