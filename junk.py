import random
import numpy as np

# Исходные данные
data = [[1, 1], [0, 4], [2, 1], [5, 2], [4, 2], [2, 3], [3, 4], [2, 0], [4, 4], [1, 3], [3, 0], [0, 3], [5, 0], [3, 4], [1, 5], [0, 0], [0, 0], [3, 5], [4, 3], [5, 4]]

# Функция для вычисления суммы столбцов
def calculate_sums(subset):
    return np.sum(subset, axis=0)

# Функция для вычисления ошибки
def calculate_error(subset1, subset2, total_sums):
    sums1 = calculate_sums(subset1)
    sums2 = calculate_sums(subset2)
    error = np.sum(np.abs(sums1 - 0.7 * total_sums) + np.abs(sums2 - 0.3 * total_sums))
    return error

# Инициализация
total_sums = calculate_sums(data)
subset1 = data[:int(len(data) * 0.7)]
subset2 = data[int(len(data) * 0.7):]

# Поиск оптимального разбиения
best_subset1 = subset1
best_subset2 = subset2
best_error = calculate_error(subset1, subset2, total_sums)

# Параметры генетического алгоритма
population_size = 50
generations = 1000
mutation_rate = 0.01

# Создание начальной популяции
population = []
for _ in range(population_size):
    random.shuffle(data)
    subset1 = data[:int(len(data) * 0.7)]
    subset2 = data[int(len(data) * 0.7):]
    population.append((subset1, subset2))

# Генетический алгоритм
for generation in range(generations):
    # Оценка популяции
    errors = [calculate_error(subset1, subset2, total_sums) for subset1, subset2 in population]
    best_index = np.argmin(errors)
    if errors[best_index] < best_error:
        best_error = errors[best_index]
        best_subset1, best_subset2 = population[best_index]

    # Селекция
    selected = random.choices(population, weights=[1 / e for e in errors], k=population_size)

    # Скрещивание
    new_population = []
    for i in range(0, population_size, 2):
        parent1, parent2 = selected[i], selected[i + 1]
        subset1_parent1, subset2_parent1 = parent1
        subset1_parent2, subset2_parent2 = parent2

        # Скрещивание
        crossover_point = random.randint(1, len(data) - 1)
        subset1_child1 = subset1_parent1[:crossover_point] + subset1_parent2[crossover_point:]
        subset2_child1 = subset2_parent1[:crossover_point] + subset2_parent2[crossover_point:]
        subset1_child2 = subset1_parent2[:crossover_point] + subset1_parent1[crossover_point:]
        subset2_child2 = subset2_parent2[:crossover_point] + subset2_parent1[crossover_point:]

        new_population.append((subset1_child1, subset2_child1))
        new_population.append((subset1_child2, subset2_child2))

    # Мутация
    for i in range(population_size):
        if random.random() < mutation_rate:
            subset1, subset2 = new_population[i]
            if random.random() < 0.5 and subset1:
                row = random.choice(subset1)
                subset1.remove(row)
                subset2.append(row)
            elif subset2:
                row = random.choice(subset2)
                subset2.remove(row)
                subset1.append(row)
            new_population[i] = (subset1, subset2)

    population = new_population

# Результат
print("Best subset 1:", best_subset1)
print("Best subset 2:", best_subset2)
print("Error:", best_error)

exit()
#------------------------------------------------------------------------------------------
import numpy as np
from scipy.optimize import minimize

# Пример данных
data = np.array([[1, 1], [0, 4], [2, 1], [5, 2], [4, 2], [2, 3], [3, 4], [2, 0], [4, 4], [1, 3], [3, 0], [0, 3], [5, 0], [3, 4], [1, 5], [0, 0],  [0, 0], [3, 5], [4, 3], [5, 4]])

# Определение функции оценки
def score_func(x):
    eighty_percent_data = data[:int(x[0])]
    twenty_percent_data = data[int(x[0]):]
    return abs(len(eighty_percent_data) / len(data) - 0.8) + abs(len(twenty_percent_data) / len(data) - 0.2)

# Определение ограничений
def constraint1(x):
    return len(data[:int(x[0])]) / len(data) - 0.8

def constraint2(x):
    return len(data[int(x[0]):]) / len(data) - 0.2

# Определение начальных параметров
x0 = [0.5 * len(data)]

# Определение ограничений и функции оценки для метода множителей Лагранжа
constraints = ({'type': 'ineq', 'fun': constraint1},
                {'type': 'ineq', 'fun': constraint2})

# Вызов функции minimize
result = minimize(score_func, x0, constraints=constraints, method='SLSQP')

# Вывод результата
print(result)


exit()



import numpy as np
from scipy.optimize import brute

# Пример данных
data = np.array([[1, 1], [0, 4], [2, 1], [5, 2], [4, 2], [2, 3], [3, 4], [2, 0], [4, 4], [1, 3], [3, 0], [0, 3], [5, 0], [3, 4], [1, 5], [0, 0],  [0, 0], [3, 5], [4, 3], [5, 4]])

# Определение функции оценки
def score_func(x):
    eighty_percent_data = data[:int(x[0])]
    twenty_percent_data = data[int(x[0]):]
    print("80%", eighty_percent_data)
    print("20%", twenty_percent_data)
    return abs(len(eighty_percent_data) / len(data) - 0.8) + abs(len(twenty_percent_data) / len(data) - 0.2)

# Определение границ для индекса разделения
bounds = [(0, len(data) - 1)]

# Вызов функции brute
result = brute(score_func, bounds, args=(), full_output=True, finish=None)

# Вывод результата
print(result)


exit()

#-----------------------------------------------------------------------------------------------------------------------


import random

# Исходные данные
data = [[1, 1], [0, 4], [2, 1], [5, 2], [4, 2], [2, 3], [3, 4], [2, 0], [4, 4], [1, 3], [3, 0], [0, 3], [5, 0], [3, 4], [1, 5], [0, 0], [0, 0], [3, 5], [4, 3], [5, 4]]

# Функция для вычисления суммы столбцов
def calculate_sums(subset):
    sum1 = sum(row[0] for row in subset)
    sum2 = sum(row[1] for row in subset)
    return sum1, sum2

# Функция для вычисления ошибки
def calculate_error(subset1, subset2, total_sum1, total_sum2):
    sum1_1, sum2_1 = calculate_sums(subset1)
    sum1_2, sum2_2 = calculate_sums(subset2)
    error1 = abs(sum1_1 - 0.8 * total_sum1) + abs(sum1_2 - 0.2 * total_sum1)
    error2 = abs(sum2_1 - 0.8 * total_sum2) + abs(sum2_2 - 0.2 * total_sum2)
    return error1 + error2

# Инициализация
total_sum1, total_sum2 = calculate_sums(data)
subset1 = data[:4]  # Начальное разбиение
subset2 = data[4:]

# Поиск оптимального разбиения
best_subset1 = subset1
best_subset2 = subset2
best_error = calculate_error(subset1, subset2, total_sum1, total_sum2)

for _ in range(10000):  # Количество итераций
    # Случайное перемещение строки между подмножествами
    if random.random() < 0.5 and subset1:
        row = random.choice(subset1)
        subset1.remove(row)
        subset2.append(row)
    elif subset2:
        row = random.choice(subset2)
        subset2.remove(row)
        subset1.append(row)

    # Вычисление ошибки для текущего разбиения
    current_error = calculate_error(subset1, subset2, total_sum1, total_sum2)
    print(current_error), subset1
    # Обновление лучшего разбиения
    if current_error < best_error:
        best_error = current_error
        best_subset1 = subset1.copy()
        best_subset2 = subset2.copy()

# Результат
print("Best subset 1:", best_subset1)
print("Best subset 2:", best_subset2)
print("Error:", best_error)


exit()
#-----------------------------------------------------------------------------------------------------------------------
import random
import copy
data = [[1, 1], [0, 4], [2, 1], [5, 2], [4, 2], [2, 3], [3, 4], [2, 0], [4, 4], [1, 3], [3, 0], [0, 3], [5, 0], [3, 4], [1, 5], [0, 0],  [0, 0], [3, 5], [4, 3], [5, 4]]

n = len(data)
eighty_percent = int(n * 0.8)

# Инициализируем переменные для хранения лучшего результата
best_eighty_percent_data = []
best_twenty_percent_data = []
best_score = float('inf')

# Генерируем случайные разделения и проверяем их на соответствие условиям
for i in range(1000):  # Вы можете увеличить количество итераций для более точного результата
    eighty_percent_data = random.sample(data, eighty_percent)
    twenty_percent_data = [x for x in data if x not in eighty_percent_data]
    # Проверяем соответствие условиям
    score = abs(len(eighty_percent_data) / n - 0.8) + abs(len(twenty_percent_data) / n - 0.2)

    print(score)
    if score < best_score:
        best_eighty_percent_data = copy.deepcopy(eighty_percent_data)
        best_twenty_percent_data = copy.deepcopy(twenty_percent_data)
        best_score = score


print("80%: ", best_eighty_percent_data, sum(row[0] for row in best_eighty_percent_data), sum(row[1] for row in best_eighty_percent_data))
print("20%: ", best_twenty_percent_data, sum(row[0] for row in best_twenty_percent_data), sum(row[1] for row in best_twenty_percent_data))
exit()


import numpy as np

data = {
    0: [3, 2, 0, 3, 2], 1: [1, 3, 1, 1, 0], 2: [2, 0, 0, 3, 0], 3: [2, 3, 1, 3, 2],
    4: [0, 2, 1, 2, 0], 5: [1, 1, 2, 3, 0], 6: [1, 0, 3, 3, 3], 7: [2, 3, 3, 2, 1],
    8: [2, 0, 1, 3, 3], 9: [2, 1, 1, 3, 1], 10: [2, 2, 2, 3, 0], 11: [0, 2, 0, 1, 1],
    12: [1, 0, 1, 2, 2], 13: [2, 0, 3, 2, 0], 14: [0, 1, 0, 2, 3]
}

# Convert data to a numpy array for easier manipulation
data_array = np.array(list(data.values()))

# Calculate the total sum of each column
total_sums = np.sum(data_array, axis=0)

# Calculate the target sums for 65%, 20%, and 15%
target_65 = total_sums * 0.65
target_20 = total_sums * 0.20
target_15 = total_sums * 0.15

# Initialize three lists for the 65%, 20%, and 15% groups
group_65 = []
group_20 = []
group_15 = []

# Sort the data by the sum of each row
sorted_indices = np.argsort(np.sum(data_array, axis=1))[::-1]

# Greedy algorithm to split the data
current_sums_65 = np.zeros(data_array.shape[1])
current_sums_20 = np.zeros(data_array.shape[1])
current_sums_15 = np.zeros(data_array.shape[1])

for idx in sorted_indices:
    row = data_array[idx]
    if all(current_sums_65 + row <= target_65):
        group_65.append(row)
        current_sums_65 += row
    elif all(current_sums_20 + row <= target_20):
        group_20.append(row)
        current_sums_20 += row
    else:
        group_15.append(row)
        current_sums_15 += row

# Convert lists back to numpy arrays for easier manipulation
group_65 = np.array(group_65)
group_20 = np.array(group_20)
group_15 = np.array(group_15)

# Print the results
print("Group 65%:")
print(group_65)
print("Sum of columns in Group 65%:")
print(np.sum(group_65, axis=0))

print("\nGroup 20%:")
print(group_20)
print("Sum of columns in Group 20%:")
print(np.sum(group_20, axis=0))

print("\nGroup 15%:")
print(group_15)
print("Sum of columns in Group 15%:")
print(np.sum(group_15, axis=0))

exit()


import random
from utils import az_math

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
          '09_chn_emeishan_2022-05_001.jpg': [1, 0, 0, 0, 4, 1, 0, 0, 0, 0]}
train = {'01_bra_resende_2023-08_02_000.jpg': [1, 0, 0, 0, 2, 2, 1, 0, 3, 0],
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
         '02_gbr_capenhurst_2018-03_004.jpg': [0, 0, 0, 1, 8, 5, 1, 0, 1, 1]}
val = {'01_bra_resende_bing_03_000.jpg': [1, 0, 0, 0, 2, 2, 1, 0, 3, 0]}

def balance_dice(bags):
    # Initialize the white and black boxes
    white_box = []
    black_box = []

    # Step 1: Initial Sorting
    for bag in bags:
        if random.random() < 0.5:
            white_box.append(bag)
        else:
            black_box.append(bag)

    def calculate_imbalance(white_box, black_box):
        # Step 2: Calculate Imbalance
        counts_white = [sum(bag.count(i) for bag in white_box) for i in range(0, 5)]
        counts_black = [sum(bag.count(i) for bag in black_box) for i in range(0, 5)]
        imbalance = sum(abs(counts_white[i] - 2/3 * counts_black[i]) for i in range(6))
        return imbalance

    def try_swaps(white_box, black_box):
        # Step 3: Swap Bags
        for i, bag_w in enumerate(white_box):
            for j, bag_b in enumerate(black_box):
                # Try swapping the bags
                white_box_new = white_box[:i] + white_box[i+1:] + [bag_b]
                black_box_new = black_box[:j] + black_box[j+1:] + [bag_w]

                # Step 4: Repeat
                imbalance_new = calculate_imbalance(white_box_new, black_box_new)
                if imbalance_new < imbalance:
                    # If the swap reduces the imbalance, keep it
                    imbalance = imbalance_new
                    white_box = white_box_new
                    black_box = black_box_new

        return white_box, black_box

    # Main loop
    imbalance = calculate_imbalance(white_box, black_box)
    while imbalance > 0:
        white_box, black_box = try_swaps(white_box, black_box)
        imbalance = calculate_imbalance(white_box, black_box)

    return white_box, black_box



# ----------------------------------------------------------------------------------------------------------------------

import numpy as np

data = {
    0: [3, 2, 0, 3, 2], 1: [1, 3, 1, 1, 0], 2: [2, 0, 0, 3, 0], 3: [2, 3, 1, 3, 2],
    4: [0, 2, 1, 2, 0], 5: [1, 1, 2, 3, 0], 6: [1, 0, 3, 3, 3], 7: [2, 3, 3, 2, 1],
    8: [2, 0, 1, 3, 3], 9: [2, 1, 1, 3, 1], 10: [2, 2, 2, 3, 0], 11: [0, 2, 0, 1, 1],
    12: [1, 0, 1, 2, 2], 13: [2, 0, 3, 2, 0], 14: [0, 1, 0, 2, 3]
}

# Convert data to a numpy array for easier manipulation
data_array = np.array(list(data.values()))

# Calculate the total sum of each column
total_sums = np.sum(data_array, axis=0)

# Calculate the target sums for 80% and 20%
target_80 = total_sums * 0.8
target_20 = total_sums * 0.2

# Initialize two lists for the 80% and 20% groups
group_80 = []
group_20 = []

# Sort the data by the sum of each row
sorted_indices = np.argsort(np.sum(data_array, axis=1))[::-1]

# Greedy algorithm to split the data
current_sums_80 = np.zeros(data_array.shape[1])
current_sums_20 = np.zeros(data_array.shape[1])

for idx in sorted_indices:
    row = data_array[idx]
    if all(current_sums_80 + row <= target_80):
        group_80.append(row)
        current_sums_80 += row
    else:
        group_20.append(row)
        current_sums_20 += row

# Convert lists back to numpy arrays for easier manipulation
group_80 = np.array(group_80)
group_20 = np.array(group_20)

# Print the results
print("Group 80%:")
print(group_80)
print("Sum of columns in Group 80%:")
print(np.sum(group_80, axis=0))

print("\nGroup 20%:")
print(group_20)
print("Sum of columns in Group 20%:")
print(np.sum(group_20, axis=0))

# ----------------------------------------------------------------------------------------------------------------------
# from ui.az_exp_mnist import *
# img = load_image_from_dataset(False)
# print (img)

# ----------------------------------------------------------------------------------------------------------------------
# def pixelate_rgb(img, window):
#     """Пикселизация изображения"""
#     n, m, _ = img.shape
#     n, m = n - n % window, m - m % window
#     img1 = np.zeros((n, m, 3))
#     for x in range(0, n, window):
#         for y in range(0, m, window):
#             img1[x:x + window, y:y + window] = img[x:x + window, y:y + window].mean(axis=(0, 1))
#     return img1
#
#
# def pixelate_bin(img, window, threshold):
#     n, m = img.shape
#     n, m = n - n % window, m - m % window
#     img1 = np.zeros((n, m))
#     for x in range(0, n, window):
#         for y in range(0, m, window):
#             if img[x:x + window, y:y + window].mean() > threshold:
#                 img1[x:x + window, y:y + window] = 1
#     return img1
#
#
# def convert_to_grey():
#     # конвертация изображения в оттенки серого
#     img = np.dot(plt.imread('test.png'), [0.299, 0.587, 0.114])
#
#     fig, ax = plt.subplots(1, 3, figsize=(15, 10))
#
#     plt.tight_layout()
#     ax[0].imshow(pixelate_bin(img, 5, .2), cmap='gray')
#     ax[1].imshow(pixelate_bin(img, 5, .3), cmap='gray')
#     ax[2].imshow(pixelate_bin(img, 5, .45), cmap='gray')
#
#     # remove frames
#     [a.set_axis_off() for a in ax.flatten()]
#     plt.subplots_adjust(wspace=0.03, hspace=0)

# ----------------------------------------------------------------------------------------------------------------------
# change_color = "#238b45"
# self.project_description.setStyleSheet(f"*{{background-color: {bg_color}; border: 1px solid #d90909;;}}")
# ----------------------------------------------------------------------------------------------------------------------
# indexes = self.image_table.selectionModel().selectedIndexes()
# print(len(indexes))
# for index in indexes:
#     role = QtCore.Qt.ItemDataRole.DisplayRole  # or Qt.DecorationRole
#     print(self.image_table.model().data(self.image_table.model().index(index.row(), 1)))
#     # print(self.image_table.model().data(index, role))
#     # print(self.image_table.model().data(self.image_table.index .index(index.row(), 0)))
#     # QTableView, Selection, QModelIndexes
# ----------------------------------------------------------------------------------------------------------------------
# # example for pandas QTableView
# import sys
# from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import Qt
# import pandas as pd
#
#
# class TableModel(QtCore.QAbstractTableModel):
#
#     def __init__(self, data):
#         super(TableModel, self).__init__()
#         self._data = data
#
#     def data(self, index, role):
#         if role == Qt.DisplayRole:
#             value = self._data.iloc[index.row(), index.column()]
#             return str(value)
#
#     def rowCount(self, index):
#         return self._data.shape[0]
#
#     def columnCount(self, index):
#         return self._data.shape[1]
#
#     def headerData(self, section, orientation, role):
#         # section is the index of the column/row.
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Horizontal:
#                 return str(self._data.columns[section])
#
#             if orientation == Qt.Vertical:
#                 return str(self._data.index[section])
#
#
# class MainWindow(QtWidgets.QMainWindow):
#
#     def __init__(self):
#         super().__init__()
#
#         self.table = QtWidgets.QTableView()
#
#         data = pd.DataFrame([
#           [1, 9, 2],
#           [1, 0, -1],
#           [3, 5, 2],
#           [3, 3, 2],
#           [5, 8, 9],
#         ], columns = ['A', 'B', 'C'], index=['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'])
#
#         self.model = TableModel(data)
#         self.table.setModel(self.model)
#
#         self.setCentralWidget(self.table)
#
#
# app=QtWidgets.QApplication(sys.argv)
# window=MainWindow()
# window.show()
# app.exec_()
# ----------------------------------------------------------------------------------------------------------------------
import re

# s = "asdasdasdaasdasdad03.jpg"
# pattern = r"^([^_]+)_([^_]+)"
# match = re.search(pattern, s)
# result1 = match.group(0)
# result2 = match.group(2)
# print(len(match))  # Выведет "19981"

# ----------------------------------------------------------------------------------------------------------------------
# import sys
# from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView
# from PyQt5.uic import loadUi
# from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
#
# class CustomTableModel(QAbstractTableModel):
#     def __init__(self, data, parent=None):
#         QAbstractTableModel.__init__(self, parent)
#         self._data = data
#
#     def rowCount(self, parent=QModelIndex()):
#         return len(self._data)
#
#     def columnCount(self, parent=QModelIndex()):
#         if self._data:
#             return len(self._data[0])
#         else:
#             return 0
#
#     def data(self, index, role=Qt.DisplayRole):
#         if index.isValid() and role == Qt.DisplayRole:
#             return self._data[index.row()][index.column()]
#         return None
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.tableView = QtWidgets.QTableView()
#         data = [
#             ["Item 1", "Description 1", "Category 1"],
#             ["Item 2", "Description 2", "Category 2"],
#             ["Item 3", "Description 3", "Category 3"],
#             ["Item 4", "Description 4", "Category 4"],
#             ["Item 5", "Description 5", "Category 5"],
#             ["Item 6", "Description 6", "Category 6"],
#             ["Item 7", "Description 7", "Category 7"],
#             ["Item 8", "Description 8", "Category 8"],
#         ]
#
#         table_model = CustomTableModel(data)
#         self.tableView.setModel(table_model)
#
#         # Set selection behavior and selection mode
#         self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
#
#         self.setCentralWidget(self.tableView)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec_())
# ----------------------------------------------------------------------------------------------------------------------
# from PyQt5 import QtWidgets, QtGui, QtCore
# import sys
#
# class MyApp(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.initUI()
#
#     def initUI(self):
#         self.layout = QtWidgets.QVBoxLayout(self)
#         self.layout.setContentsMargins(10, 10, 10, 10)
#         self.layout.setSpacing(10)
#         self.layout.setStyleSheet("border: 2px solid black;")
#
#         for i in range(3):
#             button = QtWidgets.QPushButton(f"Button {i+1}", self)
#             self.layout.addWidget(button)
#
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#
#     ex = MyApp()
#     ex.show()
#
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------
# from PyQt5 import QtCore, QtWidgets
#
#
# class MyThread(QtCore.QThread):
#     mysignal = QtCore.pyqtSignal(str)
#
#     def __init__(self, parent=None):
#         QtCore.QThread.__init__(self, parent)
#
#     def run(self):
#         for i in range(1, 21):
#             self.sleep(3)  # "Засыпаем" на 3 секунды
#             # Передача данных из потока через сигнал
#             self.mysignal.emit("i = %s" % i)
#
#
# class MyWindow(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         QtWidgets.QWidget.__init__(self, parent)
#         self.label = QtWidgets.QLabel("Нажмите кнопку для запуска потока")
#         self.label.setAlignment(QtCore.Qt.AlignHCenter)
#         self.button = QtWidgets.QPushButton("Запустить процесс")
#         self.vbox = QtWidgets.QVBoxLayout()
#         self.vbox.addWidget(self.label)
#         self.vbox.addWidget(self.button)
#         self.setLayout(self.vbox)
#         self.mythread = MyThread()  # Создаем экземпляр класса
#         self.button.clicked.connect(self.on_clicked)
#         self.mythread.started.connect(self.on_started)
#         self.mythread.finished.connect(self.on_finished)
#         self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
#
#     def on_clicked(self):
#         self.button.setDisabled(True)  # Делаем кнопку неактивной
#         self.mythread.start()  # Запускаем поток
#
#     def on_started(self):  # Вызывается при запуске потока
#         self.label.setText("Вызван метод on_started ()")
#
#     def on_finished(self):  # Вызывается при завершении потока
#         self.label.setText("Вызван метод on_finished()")
#         self.button.setDisabled(False)  # Делаем кнопку активной
#
#     def on_change(self, s):
#         self.label.setText(s)
#
#
# if __name__ == "__main__":
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     window = MyWindow()
#     window.setWindowTitle("Использование класса QThread")
#     window.resize(300, 70)
#     window.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
# from PyQt5.QtCore import Qt, QRect
# from PyQt5.QtGui import QPainter, QColor, QPen
#
# class MyWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         # Create two QLabel widgets
#         self.label1 = QLabel("Label 1")
#         self.label2 = QLabel("Label 2")
#
#         # Create a vertical box layout and add the labels
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.label1)
#         self.layout.addWidget(self.label2)
#
#         # Set the layout on the widget
#         self.setLayout(self.layout)
#
#         # Set the margin and spacing of the layout to 0
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.layout.setSpacing(0)
#
#         # Set the widget's background color to white
#         self.setAutoFillBackground(True)
#         palette = self.palette()
#         palette.setColor(palette.Window, Qt.white)
#         self.setPalette(palette)
#
#     def paintEvent(self, event):
#         # Call the base class paintEvent method
#         super().paintEvent(event)
#
#         # Create a QPainter object
#         painter = QPainter(self)
#
#         # Set the pen to a red, thin line
#         pen = QPen(QColor(255, 0, 0), 1)
#         painter.setPen(pen)
#
#         # Get the rectangles for the labels
#         label1_rect = self.label1.geometry()
#         label2_rect = self.label2.geometry()
#
#         # Draw the rectangles for the labels
#         painter.drawRect(label1_rect)
#         painter.drawRect(label2_rect)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     # Create an instance of the custom widget
#     widget = MyWidget()
#
#     # Set the window title and size
#     widget.setWindowTitle("My Widget")
#     widget.resize(300, 200)
#
#     # Show the widget and start the Qt event loop
#     widget.show()
#     sys.exit(app.exec_())
# ----------------------------------------------------------------------------------------------------------------------

# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
#
# class NoMouseButtonMoveRectItem(QGraphicsRectItem):
#     moving = False
#     def mousePressEvent(self, event):
#         super().mousePressEvent(event)
#         if event.button() == Qt.LeftButton:
#             # by defaults, mouse press events are not accepted/handled,
#             # meaning that no further mouseMoveEvent or mouseReleaseEvent
#             # will *ever* be received by this item; with the following,
#             # those events will be properly dispatched
#             event.accept()
#             self.pressPos = event.screenPos()
#
#     def mouseMoveEvent(self, event):
#         if self.moving:
#             # map the position to the parent in order to ensure that the
#             # transformations are properly considered:
#             currentParentPos = self.mapToParent(
#                 self.mapFromScene(event.scenePos()))
#             originParentPos = self.mapToParent(
#                 self.mapFromScene(event.buttonDownScenePos(Qt.LeftButton)))
#             self.setPos(self.startPos + currentParentPos - originParentPos)
#         else:
#             super().mouseMoveEvent(event)
#
#     def mouseReleaseEvent(self, event):
#         super().mouseReleaseEvent(event)
#         if (event.button() != Qt.LeftButton
#             or event.pos() not in self.boundingRect()):
#                 return
#
#         # the following code block is to allow compatibility with the
#         # ItemIsMovable flag: if the item has the flag set and was moved while
#         # keeping the left mouse button pressed, we proceed with our
#         # no-mouse-button-moved approach only *if* the difference between the
#         # pressed and released mouse positions is smaller than the application
#         # default value for drag movements; in this way, small, involuntary
#         # movements usually created between pressing and releasing the mouse
#         # button will still be considered as candidates for our implementation;
#         # if you are *not* interested in this flag, just ignore this code block
#         distance = (event.screenPos() - self.pressPos).manhattanLength()
#         if (not self.moving and distance > QApplication.startDragDistance()):
#             return
#         # end of ItemIsMovable support
#
#         self.moving = not self.moving
#         # the following is *mandatory*
#         self.setAcceptHoverEvents(self.moving)
#         if self.moving:
#             self.startPos = self.pos()
#             self.grabMouse()
#         else:
#             self.ungrabMouse()
#
#
# if __name__ == '__main__':
#     import sys
#     from random import randrange, choice
#     app = QApplication(sys.argv)
#     scene = QGraphicsScene()
#     view = QGraphicsView(scene)
#     view.resize(QApplication.primaryScreen().size() * 2 / 3)
#     # create random items that support click/release motion
#     for i in range(10):
#         item = NoMouseButtonMoveRectItem(0, 0, 100, 100)
#         item.setPos(randrange(500), randrange(500))
#         item.setPen(QColor(*(randrange(255) for _ in range(3))))
#         if choice((0, 1)):
#             item.setFlags(item.ItemIsMovable | item.ItemIsSelectable)
#             QGraphicsSimpleTextItem('Movable flag', item)
#         else:
#             item.setBrush(QColor(*(randrange(255) for _ in range(3))))
#         scene.addItem(item)
#     view.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5.Qt import *
# from PyQt5 import QtWidgets
# from PyQt5 import QtGui
#
# the_color = Qt.yellow
#
#
# class RectItem(QGraphicsRectItem):
#     def __init__(self, qrectf):
#         super().__init__()
#         self.qrectf = qrectf
#         self.setRect(self.qrectf)
#         self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
#
#         self.line = QGraphicsLineItem(self)
#         self.line.setPen(QPen(Qt.red, 2, Qt.SolidLine))
#         self.line.setLine(0, 0, 50, 50)
#         self.line2 = QGraphicsLineItem(self)
#         self.line2.setPen(QPen(Qt.green, 2, Qt.SolidLine))
#         self.line2.setLine(QLineF(0, 50, 50, 0))
#
#     def mouseMoveEvent(self, event):
#         self.moveBy(event.pos().x() - event.lastPos().x(),
#                     event.pos().y() - event.lastPos().y())
#
#
# class PointWithRect(QGraphicsRectItem):
#     """
#     Класс для хранения точки-центра с рамкой вокруг по значению Crop-size'а
#     Принимает точку (QPointF) и величину кадрирования (int)
#     """
#
#     def __init__(self, point: QPointF, crop_size):
#         super().__init__()
#         self.point = point  # сохраняем значение центральной точки
#         self.crop_size = crop_size  # значение величины кадрирования, например 1280, или 256
#         self.line = QGraphicsLineItem(self)
#         self.line.setPen(QtGui.QPen(the_color, 1, Qt.SolidLine))  # диагональная линия
#         self.line.setLine(point[0] - crop_size / 2.5, point[1] - crop_size / 2.5,
#                           point[0] + crop_size / 2.5, point[1] + crop_size / 2.5)
#         self.line2 = QGraphicsLineItem(self)
#         self.line2.setPen(QtGui.QPen(the_color, 1, Qt.SolidLine))  # диагональная линия 2
#         self.line2.setLine(point[0] + crop_size / 2.5, point[1] - crop_size / 2.5,
#                            point[0] - crop_size / 2.5, point[1] + crop_size / 2.5)
#
#         rect = QRectF(point[0] - crop_size / 2, point[1] - crop_size / 2, crop_size, crop_size)
#         self.setRect(rect)
#         self.setPen(QtGui.QPen(the_color, 2, Qt.SolidLine))
#         self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
#
#     def mouseMoveEvent(self, event):
#         self.moveBy(event.pos().x() - event.lastPos().x(),
#                     event.pos().y() - event.lastPos().y())
#
#
# class Scene(QGraphicsScene):
#     def __init__(self):
#         super().__init__()
#
#         self.setSceneRect(0, 0, 400, 400)
#         self.qrectf = None
#         self.list_rect = []
#         self.num_old = 0  # прошлый номер для полигонов
#
#     def add_rect(self, num):  # добавление квадратов
#         if num == 0:  # очистить сцену
#             self.clear()
#         elif num > self.num_old:
#             for i in range(self.num_old, num):
#                 rect = RectItem(QRectF(0, 0, 50, 50))
#                 # rect.moveBy(25, 100)
#                 self.list_rect.append(rect)
#                 self.addItem(rect)
#         elif num < self.num_old:
#             for i in range(num, self.num_old):
#                 self.removeItem(self.list_rect[-1])
#                 self.list_rect.pop()
#         else:
#             pass
#         self.num_old = num
#
#     def add_circle(self):
#         point = PointWithRect([125.441, 122.111], 33)
#         self.addItem(point)
#         # item = QtWidgets.QGraphicsEllipseItem(44, 85, 2, 2)
#         # item.setPen(QPen(Qt.yellow, 15, Qt.SolidLine))
#         # self.addItem(item)
#
#
# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.scene = Scene()
#         self.canvas = QGraphicsView()
#         self.canvas.setScene(self.scene)
#         # self.qrectf = QRectF(0, 0, 50, 50)
#         self.spinbox = QSpinBox()
#         self.spinbox.setRange(0, 8)  # +
#         self.spinbox.valueChanged.connect(self.spinbox_event)
#
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.canvas)
#         layout.addWidget(self.spinbox)
#
#         # self.scene.add_qrectf(self.qrectf)
#
#     def spinbox_event(self):
#         self.scene.add_rect(self.spinbox.value())
#         self.scene.add_circle()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = Window()
#     w.show()
#     app.exec()

# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5.Qt import *
# class RectItem(QGraphicsRectItem):
#     def __init__(self, qrectf):
#         super().__init__()
#
#         self.qrectf = qrectf
#         self.setRect(self.qrectf)
#         self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
#
#         self.line = QGraphicsLineItem(self)
#         self.line.setPen(QPen(Qt.red, 2, Qt.SolidLine))
#         self.line.setLine(0, 0, 50, 50)
#         self.line2 = QGraphicsLineItem(self)
#         self.line2.setPen(QPen(Qt.green, 2, Qt.SolidLine))
#         self.line2.setLine(QLineF(0, 50, 50, 0))
#
#     def mouseMoveEvent(self, event):
#         self.moveBy(event.pos().x() - event.lastPos().x(),
#                     event.pos().y() - event.lastPos().y())
#
#
# class Scene(QGraphicsScene):
#     def __init__(self):
#         super().__init__()
#
#         self.setSceneRect(0, 0, 400, 400)
#         self.qrectf = None
#         self.list_rect = []
#         self.num_old = 0  # прошлый номер для полигонов
#
#     def add_qrectf(self, qrectf):
#         self.qrectf = qrectf  # принимаем QRectF
#
#     def add_rect(self, num):  # добавление квадратов
#         if num == 0:  # очистить сцену
#             self.clear()
#         elif num > self.num_old:
#             for i in range(self.num_old, num):
#                 rect = RectItem(self.qrectf)
#                 rect.moveBy(25, 100)
#                 self.list_rect.append(rect)
#                 self.addItem(rect)
#         elif num < self.num_old:
#             for i in range(num, self.num_old):
#                 self.removeItem(self.list_rect[-1])
#                 self.list_rect.pop()
#         else:
#             pass
#         self.num_old = num
#
#     def add_circle(self):
#         rad = 1
#         self.addEllipse(rad, rad, rad * 2, rad * 2, Qt.QPen(Qt.green), Qt.green)
#
#
# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.scene = Scene()
#         self.canvas = QGraphicsView()
#         self.canvas.setScene(self.scene)
#         self.qrectf = QRectF(0, 0, 50, 50)
#         self.spinbox = QSpinBox()
#         self.spinbox.setRange(0, 8)  # +
#         self.spinbox.valueChanged.connect(self.spinbox_event)
#
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.canvas)
#         layout.addWidget(self.spinbox)
#
#         self.scene.add_qrectf(self.qrectf)
#
#     def spinbox_event(self):
#         self.scene.add_rect(self.spinbox.value())
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = Window()
#     w.show()
#     app.exec()

# ----------------------------------------------------------------------------------------------------------------------

# # Автоматическое изменение размера картинки автомасштабирование
# from PyQt5.Qt import *
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         centralWidget = QWidget()
#         self.setCentralWidget(centralWidget)
#
#         self.label = QLabel()
#         self.pixmap = QPixmap("test.jpg")
#         self.label.setPixmap(self.pixmap.scaled(self.label.size(),
#                                                 Qt.KeepAspectRatio, Qt.SmoothTransformation))
#
#         self.label.setSizePolicy(QSizePolicy.Expanding,
#                                  QSizePolicy.Expanding)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.label.setMinimumSize(100, 100)
#
#         self.pushButton = QPushButton('Выбрать изображение')
#         self.pushButton.clicked.connect(self.load_image)
#
#         layout = QGridLayout(centralWidget)
#         layout.addWidget(self.label)
#         layout.addWidget(self.pushButton)
#
#     def load_image(self):
#         imagePath, _ = QFileDialog.getOpenFileName(
#             self,
#             "Select Image",
#             ".",
#             "Image Files (*.png *.jpg *.jpeg *.bmp)")
#         if imagePath:
#             self.pixmap = QPixmap(imagePath)
#             self.label.setPixmap(self.pixmap.scaled(
#                 self.label.size(),
#                 Qt.KeepAspectRatio,
#                 Qt.SmoothTransformation
#             ))
#
#     def resizeEvent(self, event):
#         scaledSize = self.label.size()
#         scaledSize.scale(self.label.size(), Qt.KeepAspectRatio)
#         if not self.label.pixmap() or scaledSize != self.label.pixmap().size():
#             self.updateLabel()
#
#     def updateLabel(self):
#         self.label.setPixmap(self.pixmap.scaled(
#             self.label.size(),
#             Qt.KeepAspectRatio,
#             Qt.SmoothTransformation
#         ))
#
#
# if __name__ == "__main__":
#     import sys
#
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------

# # Разница между сигналами в pySide и PyQt5
# # my_custom_signal = pyqtSignal()  # PyQt5
# my_custom_signal = Signal()  # PySide2
#
# my_other_signal = pyqtSignal(int)  # PyQt5
# my_other_signal = Signal(int)  # PySide2

# ----------------------------------------------------------------------------------------------------------------------
# hor_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
# Спейсер, спайсер


# def getFileName(self):
#     filename, filetype = QFileDialog.getOpenFileName(self,
#                                                      "Выбрать файл",
#                                                      ".",
#                                                      "Text Files(*.txt);;JPEG Files(*.jpeg);;\
#                                                      PNG Files(*.png);;GIF File(*.gif);;All Files(*)")
#     self.plainTextEdit.appendHtml("<br>Выбрали файл: <b>{}</b> <br> <b>{:*^54}</b>"
#                                   "".format(filename, filetype))
#
#
# def getFileNames(self):
#     filenames, ok = QFileDialog.getOpenFileNames(self,
#                                                  "Выберите несколько файлов",
#                                                  ".",
#                                                  "All Files(*.*)")
#     self.plainTextEdit.appendHtml("""<br>Выбрали несколько файлов:
#                                    <b>{}</b> <br> <b>{:*^80}</b>"""
#                                   "".format(filenames, ok))
#
# ----------------------------------------------------------------------------------------------------------------------
# Отображение картинок, текста и проч. - было добавлено в init
# test_img = os.path.join(current_folder, "..", "test.jpg")
# scene = QGraphicsScene()  # Создание графической сцены
# graphicView = QGraphicsView(scene)  # Создание инструмента для отрисовки графической сцены
# graphicView.setGeometry(200, 220, 400, 400)  # Задание местоположения и размера графической сцены
# picture = QPixmap(test_img)  # Создание объекта QPixmap
# image_container = QGraphicsPixmapItem()  # Создание "пустого" объекта QGraphicsPixmapItem
# image_container.setPixmap(picture)  # Задание изображения в объект QGraphicsPixmapItem
# image_container.setOffset(0, 0)  # Позиция объекта QGraphicsPixmapItem
# # Добавление объекта QGraphicsPixmapItem на сцену
# scene.addItem(image_container)
#
# # Создание объекта QGraphicsSimpleTextItem
# text = QGraphicsSimpleTextItem('Пример текста')
# # text.setX(0) # Задание позиции текста
# # text.setY(200)
# scene.addItem(text)  # Добавление текста на сцену
# layout.addWidget(graphicView)
#
# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5.Qt import *
#
#
# class GraphicsView(QGraphicsView):
#     def __init__(self):
#         super(GraphicsView, self).__init__()
#         self.resize(400, 400)
#
#         self.scene = QGraphicsScene()
#         self.scene.setSceneRect(0, 0, 400, 400)
#
#         self.pic = QGraphicsPixmapItem()
#         self.pic.setPixmap(QPixmap('Ok.png').scaled(60, 60))
#         # позволяет выбирать его и перемещать
#         self.pic.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
#         # установить смещение изображения от начала координат сцены
#         self.pic.setOffset(170, 170)
#
#         self.text = QGraphicsTextItem()
#         self.text.setPlainText('Hello QGraphicsPixmapItem')
#         self.text.setDefaultTextColor(QColor('#91091e'))  # для установки цвета текста
#         # setPos - для установки положения текстовых примитивов относительно начала координат сцены
#         self.text.setPos(130, 230)
#
#         self.scene.addItem(self.pic)
#         self.scene.addItem(self.text)
#         self.setScene(self.scene)
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.centralWidget = QWidget()
#         self.setCentralWidget(self.centralWidget)
#
#         self.graphicsView = GraphicsView()  # создаём QGraphicView
#         self.open_im = QPushButton('Add image')
#         self.open_im.clicked.connect(self.addImage)
#
#         layout = QVBoxLayout(self.centralWidget)
#         layout.addWidget(self.graphicsView)
#         layout.addWidget(self.open_im)
#
#     def addImage(self):
#         #        pixmap = QGraphicsItem(QPixmap(fname))
#         #        form.srcGraphicsView.addItem(pixmap)
#         fname, _ = QFileDialog.getOpenFileName(
#             self, 'Open file', '.', 'Image Files (*.png *.jpg *.bmp)')
#         if fname:
#             pic = QGraphicsPixmapItem()
#             pic.setPixmap(QPixmap(fname).scaled(160, 160))
#             pic.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
#             pic.setOffset(12, 12)
#             self.graphicsView.scene.addItem(pic)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     demo = MainWindow()  # Demo()
#     demo.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------

# try:
#  обычный код
# except KeyboardInterrupt:
#  код при завершении програмы через ctrl + c

# ----------------------------------------------------------------------------------------------------------------------
# if __name__ == '__main__':
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     toolBox = AnimatedToolBox()
#     for i in range(8):
#         container = QtWidgets.QWidget()
#         layout = QtWidgets.QVBoxLayout(container)
#         for b in range((i + 1) * 2):
#             layout.addWidget(QtWidgets.QPushButton('Button {}'.format(b + 1)))
#         layout.addStretch()
#         toolBox.addItem(container, 'Box {}'.format(i + 1))
#     toolBox.show()
#     sys.exit(app.exec())

# ----------------------------------------------------------------------------------------------------------------------


# tab_widget.setStyleSheet('background: rgb(%d, %d, %d); margin: 1px; font-size: 14px;'
#                                  % (randint(244, 255), randint(244, 255), randint(244, 255)))
# style = current_folder + "/tabwidget.qss"
# with open(style, "r") as fh:
#     self.setStyleSheet(fh.read())

# ----------------------------------------------------------------------------------------------------------------------

# from functools import partial
# def add(x, y):
#     return x + y
# add_partials = []
# for i in range(1, 10):
#     function = partial(add, i)  # делаем функцию (1+y), (2+y) и т.д. до 10
#     add_partials.append(function)  # добавляем модифицированную функцию к листу add_partials
#     print('Sum of {} and 2 is {}'.format(i, add_partials[i - 1](2))) # вызываем функцию для при y = 2

# ----------------------------------------------------------------------------------------------------------------------

# colors = ('red', 'green', 'black', 'blue')
# for i, color in enumerate(colors):
#     self.tab_widget.addTab(QWidget(), 'Tab #{}'.format(i + 1))
#     self.tab_widget.tabBar().setTabTextColor(i, QColor(color))

# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5 import QtCore, QtGui, QtWidgets
#
#
# class Demo(QtWidgets.QWidget):
#     def __init__(self):
#         super(Demo, self).__init__()
#         self.button = QtWidgets.QPushButton()
#         self.label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
#
#         self.combo = QtWidgets.QComboBox(self)
#         self.combo.currentIndexChanged.connect(self.change_func)
#
#         self.trans = QtCore.QTranslator(self)   # переводчик
#
#         self.v_layout = QtWidgets.QVBoxLayout(self)
#         self.v_layout.addWidget(self.combo)
#         self.v_layout.addWidget(self.button)
#         self.v_layout.addWidget(self.label)
#
#         options = ([('English', ''), ('français', 'eng-fr'), ('中文', 'eng-chs'), ])
#
#         for i, (text, lang) in enumerate(options):
#             self.combo.addItem(text)
#             self.combo.setItemData(i, lang)
#         self.retranslateUi()
#
#     @QtCore.pyqtSlot(int)
#     def change_func(self, index):
#         data = self.combo.itemData(index)
#         if data:
#             self.trans.load(data)
#             QtWidgets.QApplication.instance().installTranslator(self.trans)
#         else:
#             QtWidgets.QApplication.instance().removeTranslator(self.trans)
#
#     def changeEvent(self, event):
#         if event.type() == QtCore.QEvent.LanguageChange:
#             self.retranslateUi()
#         super(Demo, self).changeEvent(event)
#
#     def retranslateUi(self):
#         self.button.setText(QtWidgets.QApplication.translate('Demo', 'Start'))
#         self.label.setText(QtWidgets.QApplication.translate('Demo', 'Hello, World'))
#
#
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     demo = Demo()
#     demo.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------
# Отображение границы виджета
# self.label_info.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
# self.label_file_path.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)


# ----------------------------------------------------------------------------------------------------------------------
# class _TableModel(QtCore.QAbstractTableModel):  # Реализация qdarktheme
#     def __init__(self) -> None:
#         super().__init__()
#         self._data = [[i * 10 + j for j in range(4)] for i in range(5)]
#
#     def data(self, index: QtCore.QModelIndex, role: int):
#         if role == QtCore.Qt.ItemDataRole.DisplayRole:
#             return self._data[index.row()][index.column()]
#         if role == QtCore.Qt.ItemDataRole.CheckStateRole and index.column() == 1:
#             return QtCore.Qt.CheckState.Checked if index.row() % 2 == 0 else QtCore.Qt.CheckState.Unchecked
#         if role == QtCore.Qt.ItemDataRole.EditRole and index.column() == 2:
#             return self._data[index.row()][index.column()]  # pragma: no cover
#         return None
#
#     def rowCount(self, index) -> int:  # noqa: N802
#         return len(self._data)
#
#     def columnCount(self, index) -> int:  # noqa: N802
#         return len(self._data[0])
#
#     def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
#         flag = super().flags(index)
#         if index.column() == 1:
#             flag |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
#         elif index.column() in (2, 3):
#             flag |= QtCore.Qt.ItemFlag.ItemIsEditable
#         return flag  # type: ignore
#
#     def headerData(  # noqa: N802
#             self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
#         if role != QtCore.Qt.ItemDataRole.DisplayRole:
#             return None
#         if orientation == QtCore.Qt.Orientation.Horizontal:
#             return ["Normal", "Checkbox", "Spinbox", "LineEdit"][section]
#         return section * 100
# ----------------------------------------------------------------------------------------------------------------------
