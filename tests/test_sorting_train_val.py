import utils.helper as helper
from ui.az_proc_sorting import optimum_by_greed_with_group
import numpy as np
import pytest

INPUT_DICTS = {"small": {"dad": [3, 2, 0, 3], "sister": [1, 3, 1, 1], "mama": [2, 0, 0, 3], "brother": [2, 3, 1, 3],
                         "pet": [0, 2, 1, 2], "grandpa": [1, 1, 2, 3], "fish": [1, 0, 3, 3]},
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

# Структура данных теста: (исходный словарь, параметр функции ratio, параметр группировки, {ожидаемый результат})
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
]


# Данные для тестов с группировкой
@pytest.fixture(params=ALL_DATA)
def all_test_data(request):
    return request.param


# Даные для тестов без группировки
@pytest.fixture(params=[0, 1, 2])
def test_data_without_group(request):
    return ALL_DATA[request.param]


def test_data(test_data_without_group):
    input_data, ratio, group, expected = test_data_without_group
    result = optimum_by_greed_with_group(input_data, ratio, group_pattern=group)
    print(result)
    assert result.keys() == expected.keys(), "Keys not match"
    assert len(result["train"]) + len(result["val"]
                                      ) == len(input_data), "Counts not match"
    assert result["ratio_summ"] == expected["ratio_summ"]
    assert result["train"].keys() == expected["train"].keys()
    assert result["val"].keys() == expected["val"].keys()
    assert np.isclose(
        result["error"], expected["error"]), "Value of error is not match"
