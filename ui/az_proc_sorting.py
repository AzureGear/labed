from utils import format_time
import itertools
import random
import time

# ----------------------------------------------------------------------------------------------------------------------
def generate_dict(count: int, length_val: int, max_rand: int = 3) -> dict:
    """
    Генерация тестовых словарей для проверки работы алгоритма автоматической сортировки.
    :count: количество ключей в словаре начиная с 0
    :length_val: количество столбцов в единичной записи;
    :max_rand: верхняя граница случайного распределения;
    :return: словарь с полученными случайными значениями типа {0: [0, 1, 1], 1:[2, 0, 0], ... }
    Example: result = generate_dict(40, 6, 15)
    """
    result_dict = {}
    for i in range(0, count):
        result_dict[i] = [random.randint(0, max_rand) for _ in range(length_val)]
    return result_dict

# ----------------------------------------------------------------------------------------------------------------------

# Пример использования
sort_data2 = {0: [3, 2, 0, 3, 2], 1: [1, 3, 1, 1, 0], 2: [2, 0, 0, 3, 0], 3: [2, 3, 1, 3, 2],
              4: [0, 2, 1, 2, 0], 5: [1, 1, 2, 3, 0], 6: [1, 0, 3, 3, 3], 7: [2, 3, 3, 2, 1],
              8: [2, 0, 1, 3, 3], 9: [2, 1, 1, 3, 1], 10: [2, 2, 2, 3, 0], 11: [0, 2, 0, 1, 1],
              12: [1, 0, 1, 2, 2], 13: [2, 0, 3, 2, 0], 14: [0, 1, 0, 2, 3]}
sort_data3 = {0: [2, 4, 8, 10, 0, 7, 1, 5, 3, 10, 6, 6], 1: [9, 1, 3, 1, 5, 0, 8, 4, 9, 5, 6, 7], 2: [7, 0, 3, 6, 3, 0, 5, 1, 6, 8, 4, 2], 3: [8, 10, 0, 4, 2, 6, 1, 8, 7, 3, 8, 9], 4: [6, 4, 4, 2, 5, 5, 0, 2, 9, 2, 8, 10], 5: [5, 9, 0, 0, 10, 5, 7, 2, 4, 0, 8, 3], 6: [5, 10, 6, 5, 0, 6, 10, 8, 9, 5, 0, 9], 7: [5, 8, 4, 6, 8, 1, 2, 4, 9, 4, 6, 6], 8: [8, 6, 0, 6, 8, 6, 10, 5, 1, 9, 2, 3], 9: [0, 10, 3, 0, 10, 3, 3, 8, 1, 9, 9, 3], 10: [9, 10, 9, 8, 6, 2, 6, 1, 2, 7, 6, 5], 11: [0, 6, 8, 8, 9, 0, 3, 3, 4, 0, 10, 6], 12: [7, 5, 9, 10, 9, 1, 1, 8, 9, 10, 0, 7], 13: [0, 2, 5, 6, 7, 2, 0, 10, 2, 7, 5, 8], 14: [4, 1, 3, 7, 7, 5, 5, 8, 6, 10, 1, 10]}


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
          '13_fra_georges_besse_two_here-com_013.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
          # '09_chn_emeishan_2022-05_000.jpg': [1, 0, 0, 0, 4, 3, 0, 0, 0, 0],
          # '09_chn_emeishan_2022-05_001.jpg': [1, 0, 0, 0, 4, 1, 0, 0, 0, 0],
          # '01_bra_resende_2023-08_02_000.jpg': [1, 0, 0, 0, 2, 2, 1, 0, 3, 0],
          # '12_usa_nef_2019-02_001.jpg': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          # '10_nld_almelo_2021-05_002.jpg': [0, 0, 1, 2, 2, 0, 0, 0, 0, 0],
          # '14_jpn_rokkasho_2021-07_000.jpg': [1, 3, 0, 4, 5, 0, 1, 0, 0, 0],
          # '12_usa_nef_2019-02_000.jpg': [0, 0, 1, 0, 3, 3, 0, 0, 2, 1],
          # '03_deu_gronau_2022-04_000.jpg': [0, 0, 0, 1, 5, 5, 1, 1, 2, 0],
          # '11_pak_kahuta_2023-01_000.jpg': [0, 0, 0, 0, 4, 0, 0, 0, 0, 0],
          # '02_gbr_capenhurst_2018-03_000.jpg': [0, 0, 0, 0, 4, 2, 1, 1, 0, 0],
          # '02_gbr_capenhurst_2018-03_001.jpg': [0, 3, 0, 0, 0, 1, 0, 0, 0, 0],
          # '02_gbr_capenhurst_2018-03_005.jpg': [1, 0, 0, 1, 4, 0, 1, 0, 1, 0],
          # '02_gbr_capenhurst_2018-03_002.jpg': [0, 0, 0, 0, 16, 1, 1, 2, 4, 4],
          # '02_gbr_capenhurst_2018-03_003.jpg': [0, 0, 0, 0, 2, 2, 0, 1, 4, 4],
          # '10_nld_almelo_2021-05_001.jpg': [1, 0, 0, 2, 8, 1, 1, 1, 0, 0],
          # '02_gbr_capenhurst_2018-03_007.jpg': [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          # '10_nld_almelo_2021-05_000.jpg': [0, 1, 1, 1, 7, 4, 2, 2, 0, 0],
          # '02_gbr_capenhurst_2018-03_006.jpg': [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          # '03_deu_gronau_2022-04_001.jpg': [0, 0, 0, 1, 7, 1, 1, 1, 0, 0],
          # '03_deu_gronau_2022-04_002.jpg': [1, 0, 0, 0, 0, 0, 1, 0, 2, 2],
          # '02_gbr_capenhurst_2018-03_004.jpg': [0, 0, 0, 1, 8, 5, 1, 0, 1, 1],
          # '01_bra_resende_bing_03_000.jpg': [1, 0, 0, 0, 2, 2, 1, 0, 3, 0]}


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


def optimum_split_for_data(data, ratio=0.8):
    """Автоматизированная сортировка данных"""
    # TODO: Работа алгоритма должна включать в себя "группу" и формирование связанных индексов, с последующим просмотром
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


# ----------------------------------------------------------------------------------------------------------------------
res = generate_dict(15,12,10)
print(res)
start_time = time.time()
sorted_dict = {i: unsort[key] for i, key in enumerate(unsort.keys())}
results, opt = optimum_split_for_data(sort_data3)
end_time = time.time()
sec = (end_time - start_time)  # / 3600
print(f"Всего строк: {len(results)}; строка с min: {opt}; занятое время: {format_time(sec)}")

for train_indices, val_indices, error in results:
    pass
    # print(f"Train Indices: {train_indices}, Val Indices: {val_indices}, error: {error:.1f}")
exit()


import numpy as np
import itertools

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