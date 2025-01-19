import utils.helper as helper
from ui.az_proc_sorting import optimum_by_greed_with_group, group_data_by_pattern, get_group_objects
import numpy as np
import pytest

INPUT_DICTS = {"small": {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mama": [2, 0, 0, 3], "brother": [2, 3, 1, 3], "pet": [0, 2, 1, 2], "grandpa": [1, 1, 2, 3], "fish": [1, 0, 3, 3]},

               "big_numbers": {0: [6, 10, 7, 12, 12, 11, 1, 10, 0, 4, 3, 11, 6, 12, 12, 6, 4, 11, 0, 11, 2, 4, 2, 0, 1, 0, 2, 7],
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
                               19: [0, 6, 9, 5, 12, 9, 8, 8, 5, 8, 7, 7, 8, 9, 11, 9, 7, 11, 10, 5, 8, 4, 0, 12, 1, 3, 2, 4]},

               "real": {'08_chn_lanzhou_2022-11_000.jpg': [0, 0, 0, 0, 5, 1, 1, 0, 0, 0],
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
               }

# Структура данных теста сортировки: (исходный словарь, параметр функции ratio, параметр группировки, (dict) ожидаемый результат)
ALL_DATA = [
    (INPUT_DICTS["small"], 0.8, None, {"train": {'brother': [], 'dad': [], 'fish': [], 'grandpa': []},
                                       "val": {'sister': [], 'pet': [], 'mama': []},
                                       "ratio_summ": [[7, 6, 6, 12], [3, 5, 2, 6]],
                                       "error": 6.6}),
    (INPUT_DICTS["big_numbers"], 0.8, None, {'train': {8: [], 19: [], 7: [], 1: [], 5: [], 16: [], 18: [], 15: [], 10: [], 9: [], 0: [], 4: [], 12: []},
                                             'val': {2: [], 17: [], 11: [], 6: [], 13: [], 14: [], 3: []},
                                             'ratio_summ': [[90, 79, 82, 85, 77, 85, 94, 76, 79, 77, 59, 63, 99, 96, 106, 81, 79, 86, 93, 74, 83, 70, 50, 84, 79, 71, 91, 65], [39, 38, 33, 35, 46, 24, 31, 41, 41, 25, 36, 45, 44, 33, 48, 32, 31, 50, 47, 31, 53, 31, 26, 40, 25, 44, 27, 25]],
                                             'error': 366.2}),
    (INPUT_DICTS["real"], 0.8, None, {'train': {'02_gbr_capenhurst_2018-03_002.jpg': [],
                                                '07_chn_hanzhun_shaanxi_2021-11_000.jpg': [],
                                                '13_fra_georges_besse_two_here-com_000.jpg': [],
                                                '10_nld_almelo_2021-05_000.jpg': [],
                                                '02_gbr_capenhurst_2018-03_004.jpg': [],
                                                '08_chn_lanzhou_2022-11_003.jpg': [],
                                                '03_deu_gronau_2022-04_000.jpg': [],
                                                '14_jpn_rokkasho_2021-07_000.jpg': [],
                                                '10_nld_almelo_2021-05_001.jpg': [],
                                                '08_chn_lanzhou_2022-11_005.jpg': [],
                                                '02_gbr_capenhurst_2018-03_003.jpg': [],
                                                '13_fra_georges_besse_two_here-com_001.jpg': [],
                                                '03_deu_gronau_2022-04_001.jpg': [],
                                                '12_usa_nef_2019-02_000.jpg': [],
                                                '01_bra_resende_bing_03_000.jpg': [],
                                                '02_gbr_capenhurst_2018-03_005.jpg': [],
                                                '13_fra_georges_besse_two_here-com_002.jpg': [],
                                                '13_fra_georges_besse_two_here-com_003.jpg': [],
                                                '02_gbr_capenhurst_2018-03_007.jpg': [],
                                                '13_fra_georges_besse_two_here-com_008.jpg': [],
                                                '02_gbr_capenhurst_2018-03_006.jpg': [],
                                                '08_chn_lanzhou_2022-11_001.jpg': [],
                                                '08_chn_lanzhou_2022-11_002.jpg': [],
                                                '13_fra_georges_besse_two_here-com_012.jpg': [],
                                                '13_fra_georges_besse_two_here-com_011.jpg': [],
                                                '13_fra_georges_besse_two_here-com_010.jpg': [],
                                                '12_usa_nef_2019-02_001.jpg': [],
                                                '13_fra_georges_besse_two_here-com_005.jpg': [],
                                                '13_fra_georges_besse_two_here-com_006.jpg': [],
                                                '13_fra_georges_besse_two_here-com_007.jpg': [],
                                                '13_fra_georges_besse_two_here-com_009.jpg': [],
                                                '13_fra_georges_besse_two_here-com_013.jpg': []},
                                      'val': {'07_chn_hanzhun_shaanxi_2021-11_001.jpg': [],
                                              '01_bra_resende_2023-08_02_000.jpg': [],
                                              '02_gbr_capenhurst_2018-03_000.jpg': [],
                                              '09_chn_emeishan_2022-05_000.jpg': [],
                                              '08_chn_lanzhou_2022-11_000.jpg': [],
                                              '09_chn_emeishan_2022-05_001.jpg': [],
                                              '03_deu_gronau_2022-04_002.jpg': [],
                                              '10_nld_almelo_2021-05_002.jpg': [],
                                              '08_chn_lanzhou_2022-11_004.jpg': [],
                                              '13_fra_georges_besse_two_here-com_004.jpg': [],
                                              '04_ind_ratnahalli_2023-05_000.jpg': [],
                                              '11_pak_kahuta_2023-01_000.jpg': [],
                                              '02_gbr_capenhurst_2018-03_001.jpg': []},
                                      'ratio_summ': [[18, 7, 2, 12, 118, 40, 15, 11, 34, 13], [5, 3, 1, 3, 34, 12, 7, 3, 10, 4]],
                                      'error': 11.6}),
    (INPUT_DICTS["small"], 0.5, None, {'train': {'brother': [], 'dad': []},
                                       'val': {'fish': [], 'grandpa': [], 'sister': [], 'pet': [], 'mama': []},
                                       "ratio_summ": [[5, 5, 1, 6], [5, 6, 7, 12]],
                                       "error": 6.5}),
    (INPUT_DICTS["real"], 0.1, None, {'train': {'02_gbr_capenhurst_2018-03_004.jpg': [], '04_ind_ratnahalli_2023-05_000.jpg': [], '11_pak_kahuta_2023-01_000.jpg': [], '13_fra_georges_besse_two_here-com_008.jpg': [], '08_chn_lanzhou_2022-11_001.jpg': []},
                                      'val': {'02_gbr_capenhurst_2018-03_002.jpg': [], '07_chn_hanzhun_shaanxi_2021-11_000.jpg': [], '13_fra_georges_besse_two_here-com_000.jpg': [], '10_nld_almelo_2021-05_000.jpg': [], '08_chn_lanzhou_2022-11_003.jpg': [], '03_deu_gronau_2022-04_000.jpg': [], '14_jpn_rokkasho_2021-07_000.jpg': [], '10_nld_almelo_2021-05_001.jpg': [], '08_chn_lanzhou_2022-11_005.jpg': [], '02_gbr_capenhurst_2018-03_003.jpg': [], '13_fra_georges_besse_two_here-com_001.jpg': [], '03_deu_gronau_2022-04_001.jpg': [], '07_chn_hanzhun_shaanxi_2021-11_001.jpg': [], '12_usa_nef_2019-02_000.jpg': [], '01_bra_resende_bing_03_000.jpg': [], '01_bra_resende_2023-08_02_000.jpg': [], '02_gbr_capenhurst_2018-03_000.jpg': [], '09_chn_emeishan_2022-05_000.jpg': [], '02_gbr_capenhurst_2018-03_005.jpg': [], '08_chn_lanzhou_2022-11_000.jpg': [], '09_chn_emeishan_2022-05_001.jpg': [], '03_deu_gronau_2022-04_002.jpg': [], '13_fra_georges_besse_two_here-com_002.jpg': [], '10_nld_almelo_2021-05_002.jpg': [], '08_chn_lanzhou_2022-11_004.jpg': [], '13_fra_georges_besse_two_here-com_004.jpg': [], '13_fra_georges_besse_two_here-com_003.jpg': [], '02_gbr_capenhurst_2018-03_001.jpg': [], '02_gbr_capenhurst_2018-03_007.jpg': [], '02_gbr_capenhurst_2018-03_006.jpg': [], '08_chn_lanzhou_2022-11_002.jpg': [], '13_fra_georges_besse_two_here-com_012.jpg': [], '13_fra_georges_besse_two_here-com_011.jpg': [], '13_fra_georges_besse_two_here-com_010.jpg': [], '12_usa_nef_2019-02_001.jpg': [], '13_fra_georges_besse_two_here-com_005.jpg': [], '13_fra_georges_besse_two_here-com_006.jpg': [], '13_fra_georges_besse_two_here-com_007.jpg': [], '13_fra_georges_besse_two_here-com_009.jpg': [], '13_fra_georges_besse_two_here-com_013.jpg': []},
                                      'ratio_summ': [[2, 0, 0, 1, 14, 5, 2, 1, 4, 1], [21, 10, 3, 14, 138, 47, 20, 13, 40, 16]],
                                      'error': 5.2}),
    (INPUT_DICTS["real"], 0.5, helper.PATTERNS.get("double_underscore"), {'train': {'13_fra_georges_besse_two_here-com_000.jpg': [], '13_fra_georges_besse_two_here-com_001.jpg': [], '13_fra_georges_besse_two_here-com_002.jpg': [], '13_fra_georges_besse_two_here-com_003.jpg': [], '13_fra_georges_besse_two_here-com_004.jpg': [], '13_fra_georges_besse_two_here-com_005.jpg': [], '13_fra_georges_besse_two_here-com_006.jpg': [], '13_fra_georges_besse_two_here-com_007.jpg': [], '13_fra_georges_besse_two_here-com_008.jpg': [], '13_fra_georges_besse_two_here-com_009.jpg': [], '13_fra_georges_besse_two_here-com_010.jpg': [], '13_fra_georges_besse_two_here-com_011.jpg': [], '13_fra_georges_besse_two_here-com_012.jpg': [], '13_fra_georges_besse_two_here-com_013.jpg': [], '08_chn_lanzhou_2022-11_000.jpg': [], '08_chn_lanzhou_2022-11_001.jpg': [], '08_chn_lanzhou_2022-11_002.jpg': [], '08_chn_lanzhou_2022-11_003.jpg': [], '08_chn_lanzhou_2022-11_004.jpg': [], '08_chn_lanzhou_2022-11_005.jpg': [], '07_chn_hanzhun_shaanxi_2021-11_000.jpg': [], '07_chn_hanzhun_shaanxi_2021-11_001.jpg': [], '09_chn_emeishan_2022-05_000.jpg': [], '09_chn_emeishan_2022-05_001.jpg': [], '04_ind_ratnahalli_2023-05_000.jpg': []}, 
                                                                          'val': {'02_gbr_capenhurst_2018-03_000.jpg': [], '02_gbr_capenhurst_2018-03_001.jpg': [], '02_gbr_capenhurst_2018-03_005.jpg': [], '02_gbr_capenhurst_2018-03_002.jpg': [], '02_gbr_capenhurst_2018-03_003.jpg': [], '02_gbr_capenhurst_2018-03_007.jpg': [], '02_gbr_capenhurst_2018-03_006.jpg': [], '02_gbr_capenhurst_2018-03_004.jpg': [], '10_nld_almelo_2021-05_002.jpg': [], '10_nld_almelo_2021-05_001.jpg': [], '10_nld_almelo_2021-05_000.jpg': [], '03_deu_gronau_2022-04_000.jpg': [], '03_deu_gronau_2022-04_001.jpg': [], '03_deu_gronau_2022-04_002.jpg': [], '01_bra_resende_2023-08_02_000.jpg': [], '01_bra_resende_bing_03_000.jpg': [], '14_jpn_rokkasho_2021-07_000.jpg': [], '12_usa_nef_2019-02_001.jpg': [], '12_usa_nef_2019-02_000.jpg': [], '11_pak_kahuta_2023-01_000.jpg': []}, 
                                                                          'ratio_summ': [[10, 3, 0, 2, 73, 23, 9, 5, 22, 5], [13, 7, 3, 13, 79, 29, 13, 9, 22, 12]], 
                                                                          'error': 24.0}),


]

# Структура данных теста поиска групп: (исходный словарь, паттер/шаблон, (set) ожидаемый результат)
GROUPS_RE = [
    (INPUT_DICTS["small"], r'a', {'a'}),  # буква "а"
    (INPUT_DICTS["small"], r'A', set()),  # буква "A"
    (INPUT_DICTS["small"], r'\b\w{5,}\b', {
     'sister', 'brother', 'grandpa'}),  # слова больше 4 символов
    (INPUT_DICTS["small"], r'-1', set()),  # cимвол "-1"
    (INPUT_DICTS["small"], r'\w', {'d', 's', 'm',
     'b', 'p', 'g', 'f'}),  # любая первая буква
    (INPUT_DICTS["small"], r'\d', set()),  # любая цифра
    (INPUT_DICTS["real"], helper.PATTERNS.get("double_underscore"), {
     '08_chn', '04_ind', '07_chn', '13_fra', '09_chn', '01_bra', '12_usa', '10_nld', '14_jpn', '03_deu', '11_pak', '02_gbr'}),
    (INPUT_DICTS["real"], r'\d{2}_', {'08_', '04_', '07_', '13_', '09_', '01_', '12_',
     '10_', '14_', '03_', '11_', '02_'}),  # две цифры подряд и подчеркивание после
]

# Структура данных теста группировки: (исходный словарь, паттер/шаблон, (dict) результат суммации, (dict) словарь группы исходных данных)
GROUPING_DATA = [
    (INPUT_DICTS["small"], r'\w', "start", {'p': [0, 2, 1, 2], 'd': [3, 2, 0, 3], 'g': [1, 1, 2, 3], 'b': [2, 3, 1, 3], 's': [1, 3, 1, 1], 'f': [1, 0, 3, 3], 'm': [2, 0, 0, 3]}, {'p': ['pet'], 'd': ['dad'], 'g': ['grandpa'], 'b': ['brother'], 's': ['sister'], 'f': ['fish'], 'm': ['mama']}),
    (INPUT_DICTS["real"], r'\d{2}_', "start", {'10_': [1, 1, 2, 5, 17, 5, 3, 3, 0, 0], '13_': [6, 0, 0, 0, 14, 14, 2, 0, 18, 5], '02_': [7, 3, 0, 2, 34, 11, 4, 4, 10, 9], '07_': [0, 3, 0, 0, 20, 3, 4, 2, 0, 0], '08_': [1, 0, 0, 2, 29, 2, 2, 2, 4, 0], '01_': [2, 0, 0, 0, 4, 4, 2, 0, 6, 0], '09_': [2, 0, 0, 0, 8, 4, 0, 0, 0, 0], '12_': [1, 0, 1, 0, 3, 3, 0, 0, 2, 1], '03_': [1, 0, 0, 2, 12, 6, 3, 2, 4, 2], '14_': [1, 3, 0, 4, 5, 0, 1, 0, 0, 0], '11_': [0, 0, 0, 0, 4, 0, 0, 0, 0, 0], '04_': [1, 0, 0, 0, 2, 0, 1, 1, 0, 0]}, {'10_': ['10_nld_almelo_2021-05_002.jpg', '10_nld_almelo_2021-05_001.jpg', '10_nld_almelo_2021-05_000.jpg'], '13_': ['13_fra_georges_besse_two_here-com_000.jpg', '13_fra_georges_besse_two_here-com_001.jpg', '13_fra_georges_besse_two_here-com_002.jpg', '13_fra_georges_besse_two_here-com_003.jpg', '13_fra_georges_besse_two_here-com_004.jpg', '13_fra_georges_besse_two_here-com_005.jpg', '13_fra_georges_besse_two_here-com_006.jpg', '13_fra_georges_besse_two_here-com_007.jpg', '13_fra_georges_besse_two_here-com_008.jpg', '13_fra_georges_besse_two_here-com_009.jpg', '13_fra_georges_besse_two_here-com_010.jpg', '13_fra_georges_besse_two_here-com_011.jpg', '13_fra_georges_besse_two_here-com_012.jpg', '13_fra_georges_besse_two_here-com_013.jpg'], '02_': ['02_gbr_capenhurst_2018-03_000.jpg', '02_gbr_capenhurst_2018-03_001.jpg', '02_gbr_capenhurst_2018-03_005.jpg', '02_gbr_capenhurst_2018-03_002.jpg', '02_gbr_capenhurst_2018-03_003.jpg', '02_gbr_capenhurst_2018-03_007.jpg', '02_gbr_capenhurst_2018-03_006.jpg', '02_gbr_capenhurst_2018-03_004.jpg'], '07_': ['07_chn_hanzhun_shaanxi_2021-11_000.jpg', '07_chn_hanzhun_shaanxi_2021-11_001.jpg'], '08_': ['08_chn_lanzhou_2022-11_000.jpg', '08_chn_lanzhou_2022-11_001.jpg', '08_chn_lanzhou_2022-11_002.jpg', '08_chn_lanzhou_2022-11_003.jpg', '08_chn_lanzhou_2022-11_004.jpg', '08_chn_lanzhou_2022-11_005.jpg'], '01_': ['01_bra_resende_2023-08_02_000.jpg', '01_bra_resende_bing_03_000.jpg'], '09_': ['09_chn_emeishan_2022-05_000.jpg', '09_chn_emeishan_2022-05_001.jpg'], '12_': ['12_usa_nef_2019-02_001.jpg', '12_usa_nef_2019-02_000.jpg'], '03_': ['03_deu_gronau_2022-04_000.jpg', '03_deu_gronau_2022-04_001.jpg', '03_deu_gronau_2022-04_002.jpg'], '14_': ['14_jpn_rokkasho_2021-07_000.jpg'], '11_': ['11_pak_kahuta_2023-01_000.jpg'], '04_': ['04_ind_ratnahalli_2023-05_000.jpg']}),
    (INPUT_DICTS["real"], helper.PATTERNS.get("three_letters"), "re", {'_jpn_': [1, 3, 0, 4, 5, 0, 1, 0, 0, 0], '_pak_': [0, 0, 0, 0, 4, 0, 0, 0, 0, 0], '_deu_': [1, 0, 0, 2, 12, 6, 3, 2, 4, 2], '_gbr_': [7, 3, 0, 2, 34, 11, 4, 4, 10, 9], '_chn_': [3, 3, 0, 2, 57, 9, 6, 4, 4, 0], '_usa_': [1, 0, 1, 0, 3, 3, 0, 0, 2, 1], '_nld_': [1, 1, 2, 5, 17, 5, 3, 3, 0, 0], '_ind_': [1, 0, 0, 0, 2, 0, 1, 1, 0, 0], '_fra_': [6, 0, 0, 0, 14, 14, 2, 0, 18, 5], '_bra_': [2, 0, 0, 0, 4, 4, 2, 0, 6, 0]}, {'_jpn_': ['14_jpn_rokkasho_2021-07_000.jpg'], '_pak_': ['11_pak_kahuta_2023-01_000.jpg'], '_deu_': ['03_deu_gronau_2022-04_000.jpg', '03_deu_gronau_2022-04_001.jpg', '03_deu_gronau_2022-04_002.jpg'], '_gbr_': ['02_gbr_capenhurst_2018-03_000.jpg', '02_gbr_capenhurst_2018-03_001.jpg', '02_gbr_capenhurst_2018-03_005.jpg', '02_gbr_capenhurst_2018-03_002.jpg', '02_gbr_capenhurst_2018-03_003.jpg', '02_gbr_capenhurst_2018-03_007.jpg', '02_gbr_capenhurst_2018-03_006.jpg', '02_gbr_capenhurst_2018-03_004.jpg'], '_chn_': ['08_chn_lanzhou_2022-11_000.jpg', '08_chn_lanzhou_2022-11_001.jpg', '08_chn_lanzhou_2022-11_002.jpg', '08_chn_lanzhou_2022-11_003.jpg', '08_chn_lanzhou_2022-11_004.jpg', '08_chn_lanzhou_2022-11_005.jpg', '07_chn_hanzhun_shaanxi_2021-11_000.jpg', '07_chn_hanzhun_shaanxi_2021-11_001.jpg', '09_chn_emeishan_2022-05_000.jpg', '09_chn_emeishan_2022-05_001.jpg'], '_usa_': ['12_usa_nef_2019-02_001.jpg', '12_usa_nef_2019-02_000.jpg'], '_nld_': ['10_nld_almelo_2021-05_002.jpg', '10_nld_almelo_2021-05_001.jpg', '10_nld_almelo_2021-05_000.jpg'], '_ind_': ['04_ind_ratnahalli_2023-05_000.jpg'], '_fra_': ['13_fra_georges_besse_two_here-com_000.jpg', '13_fra_georges_besse_two_here-com_001.jpg', '13_fra_georges_besse_two_here-com_002.jpg', '13_fra_georges_besse_two_here-com_003.jpg', '13_fra_georges_besse_two_here-com_004.jpg', '13_fra_georges_besse_two_here-com_005.jpg', '13_fra_georges_besse_two_here-com_006.jpg', '13_fra_georges_besse_two_here-com_007.jpg', '13_fra_georges_besse_two_here-com_008.jpg', '13_fra_georges_besse_two_here-com_009.jpg', '13_fra_georges_besse_two_here-com_010.jpg', '13_fra_georges_besse_two_here-com_011.jpg', '13_fra_georges_besse_two_here-com_012.jpg', '13_fra_georges_besse_two_here-com_013.jpg'], '_bra_': ['01_bra_resende_2023-08_02_000.jpg', '01_bra_resende_bing_03_000.jpg']}),
]


@pytest.fixture(params=ALL_DATA)
# Данные для всех данных теста сортировки
def all_data(request):
    return request.param


@pytest.fixture(params=[5])
# Данные для тестов сортировки с группировкой
def grouped_data(request):
    return ALL_DATA[request.param]


@pytest.fixture(params=[0, 1, 2, 3, 4])
# Даные для тестов сортировки  без группировки
def data_without_group(request):
    return ALL_DATA[request.param]


@pytest.fixture(params=GROUPING_DATA)
# Даные для тестов объединения и суммации
def group_and_sum_data(request):
    return request.param


@pytest.fixture(params=GROUPS_RE)
# Даные для тестов регулярных выражений
def groups_re(request):
    return request.param


def test_data_no_group(all_data):
    """Тестирование функции сортировки без группировки данных"""
    input_data, ratio, group, expected = all_data
    result = optimum_by_greed_with_group(
        input_data, ratio, group_pattern=group)
    assert result.keys() == expected.keys(), "Keys not match"
    assert len(result["train"]) + len(result["val"]
                                      ) == len(input_data), "Counts not match"
    assert result["ratio_summ"] == expected["ratio_summ"], "Ratios sum is not match"
    assert result["train"].keys(
    ) == expected["train"].keys(), "Train data is not match"
    assert result["val"].keys() == expected["val"].keys(
    ), "Vals data is not match"
    assert np.isclose(
        result["error"], expected["error"]), "Value of error is not match"


def test_get_group_objects(groups_re):
    """Тестирование образование групп с помощью 're'"""
    input_data, pattern, expected = groups_re
    result = get_group_objects(input_data.keys(), pattern)
    print(result)
    assert result == expected, "Groups not match"


def test_group_and_summ(group_and_sum_data):
    """Тестирование образование групп с помощью 're'"""
    input_data, pattern, pattern_type, expected_sum, expected_keys = group_and_sum_data
    result_sum, result_keys = group_data_by_pattern(input_data, pattern, pattern_type)
    assert result_sum == expected_sum, "Sums not match"
    assert result_keys == expected_keys, "Keys not match"

