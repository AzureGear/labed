from utils import format_time
from utils import helper
import numpy as np
import itertools
import random
import time
import copy
import re

# ----------------------------------------------------------------------------------------------------------------------
def generate_dict(count: int, length_val: int, max_rand: int = 3) -> dict:
    """
    Генерация тестовых словарей для проверки работы алгоритма автоматической сортировки.
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
def get_group_objects(data, pattern=helper.PATTERNS.get("double_underscore")):
    objects = []
    for item in data:
        match = re.search(pattern, item)
        if match is not None:
            if match.group(0) not in objects:
                objects.append(match.group(0))
    return objects


# ----------------------------------------------------------------------------------------------------------------------

# Пример использования
sort_small = {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mama": [2, 0, 0, 3], "brother": [2, 3, 1, 3],
              "pet": [0, 2, 1, 2], "grandpa": [1, 1, 2, 3], "fish": [1, 0, 3, 3]}
sort_data_15 = {0: [3, 2, 0, 3, 2], 1: [1, 3, 1, 1, 0], 2: [2, 0, 0, 3, 0], 3: [2, 3, 1, 3, 2],
                4: [0, 2, 1, 2, 0], 5: [1, 1, 2, 3, 0], 6: [1, 0, 3, 3, 3], 7: [2, 3, 3, 2, 1],
                8: [2, 0, 1, 3, 3], 9: [2, 1, 1, 3, 1], 10: [2, 2, 2, 3, 0], 11: [0, 2, 0, 1, 1],
                12: [1, 0, 1, 2, 2], 13: [2, 0, 3, 2, 0], 14: [0, 1, 0, 2, 3]}

sort_data_40_small = {0: [8, 11, 11], 1: [4, 2, 1], 2: [5, 6, 6], 3: [9, 11, 7], 4: [3, 0, 5], 5: [12, 12, 12],
                      6: [3, 9, 7],
                      7: [3, 0, 10], 8: [9, 1, 10], 9: [1, 4, 7], 10: [1, 11, 12], 11: [10, 2, 7], 12: [4, 2, 5],
                      13: [1, 1, 12], 14: [7, 12, 10], 15: [4, 11, 11], 16: [12, 2, 1], 17: [8, 0, 3], 18: [0, 5, 4],
                      19: [8, 9, 10], 20: [4, 12, 5], 21: [4, 1, 7], 22: [12, 5, 8], 23: [12, 12, 4], 24: [2, 9, 11],
                      25: [12, 0, 2], 26: [2, 5, 0], 27: [10, 1, 7], 28: [0, 12, 8], 29: [2, 8, 3], 30: [4, 6, 0],
                      31: [8, 4, 9], 32: [3, 8, 1], 33: [8, 0, 6], 34: [11, 4, 12], 35: [8, 8, 0], 36: [7, 11, 5],
                      37: [1, 9, 7], 38: [7, 6, 2], 39: [4, 11, 9]}

sort_data_20 = {0: [0, 1, 1, 0], 1: [3, 1, 0, 3], 2: [1, 0, 1, 2], 3: [4, 1, 2, 0], 4: [5, 4, 0, 2], 5: [0, 1, 2, 4],
                6: [5, 0, 0, 2], 7: [0, 0, 4, 2], 8: [2, 0, 2, 2], 9: [4, 0, 2, 1], 10: [5, 1, 3, 4], 11: [4, 1, 3, 0],
                12: [1, 3, 4, 0], 13: [0, 4, 5, 5], 14: [3, 5, 0, 2], 15: [3, 4, 4, 1], 16: [0, 3, 3, 2],
                17: [5, 4, 0, 3], 18: [5, 1, 4, 2], 19: [0, 4, 1, 2]}

sort_data_20_big = {0: [6, 10, 7, 12, 12, 11, 1, 10, 0, 4, 3, 11, 6, 12, 12, 6, 4, 11, 0, 11, 2, 4, 2, 0, 1, 0, 2, 7],
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

unsort = {'08_chn_lanzhou_2022-11_000.jpg': [0, 0, 0, 0, 5, 1, 1, 0, 0, 0],
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


def calc_ratio(train, val):
    """Расчет и вывод статистики для выборок"""
    if len(train) != len(val):
        raise ValueError("Списки должны быть одинаковой длины")
    # на 0 делить нельзя, поэтому вводим правило, и считаем сумму/столбец для train и val
    train_percentages = [(t / (t + v)) * 100 if (t + v) != 0 else 0 for t, v in zip(train, val)]
    val_percentages = [(v / (t + v)) * 100 if (t + v) != 0 else 0 for t, v in zip(train, val)]
    return train_percentages, val_percentages


def calculate_sum(items):
    """Расчет поэлементной суммы (по столбцам) для набора items"""
    return [sum(row[i] for row in items) for i in range(len(items[0]))]


def calculate_error(train, val, ratio=0.8):
    """Расчет ошибки между классами. Вычисляется как модуль между abs(train*ration - val*(1 - ratio)) для всех
    столбцов"""
    sum_train = calculate_sum(train)
    sum_val = calculate_sum(val)
    abs_error = sum(abs(sum_train[i] * (1 - ratio) - (sum_val[i] * ratio)) for i in range(len(train[0])))
    # train_, val_ = calc_ratio(sum_train, sum_val)
    # print("sum_train:", sum_train, "; sum_val:", sum_val, f"; error: {error:.1f}, %t: ",
    #       [f"{p:.0f}" for p in train_], ";  %v:", [f"{p:.0f}" for p in val_])
    return abs_error


def optimum_split_for_data(data, ratio=0.8, accept_error=6.5):
    """Автоматизированная сортировка данных"""
    # TODO: Работа алгоритма должна включать в себя "группу" и формирование связанных индексов, с последующим просмотром
    # значений индексов и удаления среди них тех, кто из одной "группы" оказывается в разнесён и в train и в val.
    if len(data) < 2:
        raise ValueError("Список должен содержать хотя бы 2 строки")
    num_rows = len(data)
    min_error = float('inf')
    count = 0  # количество перебранных вариантов
    for train_size in range(1, num_rows):
        for val_indices in itertools.combinations(data.keys(), train_size):
            train_indices = tuple([i for i in data.keys() if i not in val_indices])
            train_data = [data[i] for i in train_indices]
            val_data = [data[i] for i in val_indices]
            error = calculate_error(train_data, val_data, ratio)
            count += 1
            # Compare
            if count % 100000 == 0:
                print(f"still work: {count}")
            if error < min_error:
                min_error = error
                print(f"{count}: min error {error}")
                best_train = copy.copy(train_data)
                best_val = copy.copy(val_data)

                if error <= accept_error:
                    return best_train, best_val, count
    return best_train, best_val, count


def optimum_by_greed(data, ratio=0.8, group_pattern=None):
    """Поиск оптимального разбиения на основе жадного алгоритма. Исходные данные data являются словарем списка
     типа: {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mama": [2, 0, 0, 3]}
     ratio - это размер отношения для выборки train от 1 до 0"""
    data_array = np.array(list(data.values()))  # преобразуем в массив numpy для оптимизации
    keys = list(data.keys())  # сохраняем список ключей
    total_sums = np.sum(data_array, axis=0)  # сумма каждой колонки
    train_score = total_sums * ratio  # рассчитываем идеальное соотношение
    train_data, val_data = [], []  # списки для выходных данных: train и val
    train_keys, val_keys = [], []  # ключи для выходных данных

    # TODO: попробовать сортировать исходя из значения ошибки
    sums = np.sum(data_array, axis=1)  # считаем суммы строк
    sorted_idx = np.argsort(sums)[::-1]  # сортируем данные
    train_sums, val_sums = np.zeros(data_array.shape[1]), np.zeros(data_array.shape[1])  # нулевые матрицы для суммы

    for i in sorted_idx:  # используем жадный алгоритм для разбиения данных на отсортированных индексах
        row = data_array[i]
        if all(train_sums + row <= train_score):
            train_data.append(row.tolist())
            train_keys.append(keys[i])  # индексы отсортированы, но значения верные
            train_sums += row
        else:
            val_data.append(row.tolist())
            val_keys.append(keys[i])
            val_sums += row

    result = {"train": dict(zip(train_keys, train_data)), "val": dict(zip(val_keys, val_data))}
    return train_data, val_data, result

    # # Конвертируем списки в numpy для оптимизации
    # train_data = np.array(train_data)
    # val_data = np.array(val_data)

def optimum_by_greed_with_group(data, ratio=0.8, group_pattern=None):
    """Поиск оптимального разбиения на основе жадного алгоритма. Исходные данные data являются словарем списка
     типа: {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mama": [2, 0, 0, 3]}
     ratio - это размер отношения для выборки train от 1 до 0
     group_pattern - шаблон образования групп для переченя"""
    data_array = np.array(list(data.values()))  # преобразуем в массив numpy для оптимизации
    keys = list(data.keys())  # сохраняем список ключей
    total_sums = np.sum(data_array, axis=0)  # сумма каждой колонки
    train_score = total_sums * ratio  # рассчитываем идеальное соотношение
    train_data, val_data = [], []  # списки для выходных данных: train и val
    train_keys, val_keys = [], []  # ключи для выходных данных

    # TODO: попробовать сортировать исходя из значения ошибки
    sums = np.sum(data_array, axis=1)  # считаем суммы строк
    sorted_idx = np.argsort(sums)[::-1]  # сортируем данные
    train_sums, val_sums = np.zeros(data_array.shape[1]), np.zeros(data_array.shape[1])  # нулевые матрицы для суммы

    for i in sorted_idx:  # используем жадный алгоритм для разбиения данных на отсортированных индексах
        row = data_array[i]
        if all(train_sums + row <= train_score):
            train_data.append(row.tolist())
            train_keys.append(keys[i])  # индексы отсортированы, но значения верные
            train_sums += row
        else:
            val_data.append(row.tolist())
            val_keys.append(keys[i])
            val_sums += row

    result = {"train": dict(zip(train_keys, train_data)), "val": dict(zip(val_keys, val_data))}
    return train_data, val_data, result

# ----------------------------------------------------------------------------------------------------------------------
# res = generate_dict(40, 3, 12)
# print(res)
start_time = time.time()
sorted_dict = {i: unsort[key] for i, key in enumerate(unsort.keys())}

file = "c:/Users/user/Dropbox/sort_info.json"
big_real_data = helper.load(file)
groups = get_group_objects(big_real_data.keys())
print(groups)
cur_ratio = 0.8
train, val, result = optimum_by_greed_with_group(big_real_data, cur_ratio, helper.PATTERNS.get("double_underscore"))
# print(big_real_data)
# train, val, count = optimum_split_for_data(unsort, 0.8, 6.5)
end_time = time.time()
sec = (end_time - start_time)  # / 3600
train_, val_ = calc_ratio(calculate_sum(train), calculate_sum(val))
print(f"error: {calculate_error(train, val, cur_ratio):.1f};\n%t:", [f"{p:.0f}" for p in train_], ";\n%v:",
      [f"{p:.0f}" for p in val_])
print(f"Обработано строк: {None}; занятое время: {format_time(sec)}")

# # Print the results
# print("Group 80%:")
# print(train_data)
# print("Sum of columns in Group 80%:")
# print(np.sum(train_data, axis=0))
#
# print("\nGroup 20%:")
# print(val_data)
# print("Sum of columns in Group 20%:")
# print(np.sum(val_data, axis=0))

exit()


def calculate_error_np(train_data, val_data, ratio):
    # Пример функции для вычисления ошибки
    train_sum = np.sum(train_data)
    val_sum = np.sum(val_data)
    return np.abs(train_sum - val_sum * ratio)


def calculate_sum_np(data):
    return np.sum(data)


def calc_ratio_np(train_sum, val_sum):
    return train_sum / val_sum


def optimum_split_for_data_np(data, ratio=0.8):
    """Автоматизированная сортировка данных"""
    if len(data) < 2:
        raise ValueError("Список должен содержать хотя бы 2 строки")

    num_rows = len(data)
    results = []

    # Преобразуем данные в массив NumPy
    data_array = np.array(list(data.values()))

    for train_size in range(1, num_rows):
        for train_indices in itertools.combinations(range(num_rows), train_size):
            val_indices = tuple([i for i in range(num_rows) if i not in train_indices])
            train_data = data_array[list(train_indices)]
            val_data = data_array[list(val_indices)]
            error = calculate_error(train_data, val_data, ratio)
            results.append((train_indices, val_indices, error))

    min_index = min(enumerate(results), key=lambda x: x[1][2])[0]  # находим строку с минимальным значением ошибки
    # формируем из неё значение
    best_train = data_array[list(results[min_index][0])]
    best_val = data_array[list(results[min_index][1])]
    print(calc_ratio(calculate_sum(best_train), calculate_sum(best_val)))

    return results, min_index


# Пример использования
data = {"a": [0, 1], "b": [1, 1], "c": [2, 4], "d": [0, 6]}
results, min_index = optimum_split_for_data(data)
print(results)
print(min_index)


def optimum_split_for_data_old(data, ratio=0.8):
    """Автоматизированная сортировка данных. Изначальный алгоритм"""
    # значений индексов и удаления среди них тех, кто из одной "группы" оказывается в разнесён и в train и в val.
    if len(data) < 2:
        raise ValueError("Список должен содержать хотя бы 2 строки")
    num_rows = len(data)
    results = []
    for train_size in range(1, num_rows):
        for train_indices in itertools.combinations(data.keys(), train_size):
            val_indices = tuple([i for i in data.keys() if i not in train_indices])
            train_data = [data[i] for i in train_indices]
            val_data = [data[i] for i in val_indices]
            error = calculate_error(train_data, val_data, ratio)
            results.append((train_indices, val_indices, error))
    min_index = min(enumerate(results), key=lambda x: x[1][2])[0]  # находим строку с минимальным значением ошибки
    # формируем из неё значение
    best_train = [data[i] for i in results[min_index][0]]
    best_val = [data[i] for i in results[min_index][1]]
    print(calc_ratio(calculate_sum(best_train), calculate_sum(best_val)))

    return results, min_index
