from PyQt5 import QtWidgets, QtGui, QtCore
from utils import format_time, helper, UI_COLORS
from ui import new_button, new_text, new_icon, AzSimpleModel
from itertools import combinations
from typing import Dict, Tuple
import numpy as np
import random
import copy
import time
import re

the_color = UI_COLORS.get("processing_color")

# ----------------------------------------------------------------------------------------------------------------------


class SortColWidget(QtWidgets.QWidget):
    signal_spin_changed = QtCore.pyqtSignal(float)  # сигнал изменения значений
    signal_state_changed = QtCore.pyqtSignal(
        bool)  # сигнал изменения состояния

    def __init__(self, checkbox_text, initial_value=0.0, enabled=True, color=None, parent=None):
        super().__init__(parent)

        self.checkbox_text = checkbox_text  # текст
        self.initial_value = initial_value  # начальное значение
        self.enabled = enabled  # состояние (вкл./выкл.)
        self.color = color  # цвет
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QHBoxLayout()

        self.checkbox = QtWidgets.QCheckBox(self.checkbox_text)
        # устанавливаем начальное состояние
        self.checkbox.setChecked(self.enabled)
        self.checkbox.stateChanged.connect(self.toggle_widgets)
        layout.addWidget(self.checkbox)

        self.spinbox = QtWidgets.QDoubleSpinBox()  # точность "0%"
        self.spinbox.setAccelerated(True)
        self.spinbox.setDecimals(0)  # устанавливаем необходимую точность
        self.spinbox.setRange(1, 100)  # устанавливаем диапазон от 0 до 100
        self.spinbox.setSuffix("%")  # суффикс
        self.spinbox.setValue(self.initial_value)  # начальное значение

        self.checkbox.setStyleSheet(f"QCheckBox {{ color: {self.color}; }}")
        self.spinbox.setStyleSheet(
            f"QDoubleSpinBox {{ color: {self.color}; }}")

        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        # Исходная настройка виджетов
        # исходное состояние виджетов
        self.toggle_widgets(self.checkbox.checkState())

        # Signals
        # Подключаем сигнал к изменению значений
        self.spinbox.valueChanged.connect(self.signal_spin_changed.emit)

    def toggle_widgets(self, state):
        """Переключение состояния виджета"""
        if state == QtCore.Qt.CheckState.Checked:
            self.spinbox.setEnabled(True)
        else:
            self.spinbox.setEnabled(False)
        self.signal_state_changed.emit(state)


# ----------------------------------------------------------------------------------------------------------------------
class ColorBarWidget(QtWidgets.QWidget):
    """Виджет индикатор соотношения в виде полоски заполненности"""

    def __init__(self, line_thickness, lines=None, font_size=10):
        super().__init__()
        self.line_thickness = line_thickness
        self.lines = lines
        self.font_size = font_size
        self.setMinimumHeight(line_thickness + font_size * 3)

    def update_values(self, lines):
        self.lines = lines
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # максимальную длина линии с учетом отступов (10 пикселей слева и 50 справа)
        max_length = self.width() - 60
        x_pos = 10

        if not self.lines:
            return

        summ = 0
        for length_percent, color, text in self.lines:  # рисуем линии и текст
            summ += int(length_percent)
            length = int(max_length * length_percent / 100)
            the_color = QtGui.QColor(color)
            pen = QtGui.QPen(the_color, self.line_thickness)
            painter.setPen(pen)
            painter.drawLine(x_pos, self.height() // 2, x_pos +
                             length, self.height() // 2)  # линия

            # добавляем текст над линией
            font = QtGui.QFont("Tahoma", self.font_size)
            painter.setFont(font)
            painter.setPen(the_color)  # цвет текста как у линии
            text_width = painter.fontMetrics().width(text)
            text_x = x_pos + (length - text_width) // 2
            text_y = self.height() // 2 - self.line_thickness - \
                1  # учитываем смещение вверх
            text2_y = self.height() // 2 + self.line_thickness + self.font_size + 1
            painter.drawText(text_x, text_y, text)
            painter.drawText(text_x, text2_y, str(int(length_percent)) + "%")
            painter.setPen(QtGui.QColor("grey"))

            x_pos += length

        painter.drawText(self.width() - 37, self.height() //
                         2 + self.font_size // 2, str(summ) + "%")

        if summ == 100:  # если получено 100%, то рисуем красивую рамку
            painter.setPen(QtGui.QPen(QtGui.QColor("green"),
                           2, QtCore.Qt.PenStyle.DotLine))
            painter.drawRect(0, 0, self.width() - 40, self.minimumHeight())
            painter.drawText(self.width() - 37, self.height() //
                             2 + self.font_size // 2, "100%")


# ----------------------------------------------------------------------------------------------------------------------
class AzSortingDatasetDialog(QtWidgets.QDialog):
    """
    Диалоговое окно для автоматизированной сортировки датасета
    """

    def __init__(self, data, parent=None, window_title="Smart dataset sorting", ):
        super().__init__(parent)
        # self.setStyleSheet("QWidget { border: 1px solid red; }")
        self.setWindowTitle(window_title)
        # фиксированные размеры для размещения кастомных виджетов
        self.setFixedSize(600, 330)
        self.setWindowFlag(QtCore.Qt.WindowType.Tool)
        self.data = data
        self.setup_ui()

        self.result = {}  # выходные данные
        self.sort_cols = {}  # размер и наименование групп сортировки
        self.update_sort_cols()  # заполняем self.sort_cols

    def setup_ui(self):
        """Настройка интерфейса"""
        # Создаем кнопки
        self.button_cancel = new_button(
            self, "pb", self.tr("Cancel"), slot=self.reject)
        self.button_ok = new_button(
            self, "pb", self.tr("OK"), slot=self.accept)
        self.button_ok.setEnabled(False)  # по умолчанию отключаем
        self.button_sort = new_button(
            self, "pb", self.tr("Сортировать"), slot=self.exec_sort)

        # Объекты с общим именем рассматриваются как группа данных
        self.chk_group_sort = QtWidgets.QCheckBox(
            self.tr(
                "Objects with a common name are considered as a data group (use group pattern):"),
            self)
        # по умолчанию используем шаблон двойного подчеркивания
        self.group_sort_pattern = QtWidgets.QLineEdit(self)
        self.group_sort_pattern.setEnabled(False)
        self.group_sort_pattern.setText(
            helper.PATTERNS.get("double_underscore"))
        self.chk_group_sort.stateChanged.connect(
            lambda state: self.group_sort_pattern.setEnabled(state == QtCore.Qt.CheckState.Checked))

        self.table_view = QtWidgets.QTableView()
        self.sort_info = new_text(self)
        self.btn_status = new_button(self, "tb", icon="circle_grey", color=None, icon_size=16,
                                     tooltip=self.tr("Sorting results"))
        self.button_cancel.setMinimumWidth(100)
        self.button_ok.setMinimumWidth(100)

        self.sort_widgets = []  # виджеты сортировки
        widgets = [("train", 70, UI_COLORS.get("train_color")),
                   ("val", 15, UI_COLORS.get("val_color")),
                   ("test", 15, UI_COLORS.get("test_color"))]

        sort_lay = QtWidgets.QHBoxLayout()  # компоновщик виджетов сортировки

        for name, value, color in widgets:
            widget = SortColWidget(
                checkbox_text=name, initial_value=value, color=color)
            # сигнал обновления при изменении значений
            widget.signal_spin_changed.connect(self.check_values)
            # сигнал обновления при изменении состояния
            widget.signal_state_changed.connect(self.check_values)
            self.sort_widgets.append(widget)
            sort_lay.addWidget(widget)

        sort_lay.addWidget(self.button_sort)

        # Индикатор соотношения в виде полоски заполненности (train, val, test)
        values_labels_colors = [(widget.spinbox.value(), widget.color, widget.checkbox_text) for widget in
                                self.sort_widgets]
        self.color_bar = ColorBarWidget(5, values_labels_colors)

        # компоновщик для учета группировки объектов и его шаблона
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.chk_group_sort)
        hlay.addWidget(self.group_sort_pattern)
        hlay.addSpacing(40)

        button_layout = QtWidgets.QHBoxLayout()  # компоновщик для кнопок
        button_layout.addStretch(1)
        button_layout.addWidget(self.button_ok)
        button_layout.addWidget(self.button_cancel)

        hlay_info = QtWidgets.QHBoxLayout()  # компоновщик индикатора и информации
        hlay_info.addWidget(self.btn_status)
        hlay_info.addWidget(self.sort_info, 1)

        self.layout = QtWidgets.QVBoxLayout()  # основной компоновщик
        self.layout.addLayout(sort_lay)
        self.layout.addLayout(hlay)
        self.layout.addWidget(self.color_bar)
        self.layout.addLayout(hlay_info)
        self.layout.addWidget(self.table_view)
        self.layout.addStretch(1)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def exec_sort(self):
        """Выполнение сортировки"""
        start_time = time.time()

        self.result = {}  # очищаем от прошлых результатов
        if self.chk_group_sort.isChecked():  # определяем требуется ли группировка
            pattern = self.group_sort_pattern.text()
        else:
            pattern = None
        cols = len(self.sort_cols)  # количество выборок

        names = list(self.sort_cols.keys())
        # приводим к виду 82% = 0.82
        ratios = [val / 100 for val in self.sort_cols.values()]
        # stats = {"ratios": ratios, "names": names, "pattern": pattern}  # статистика для вывода

        if cols == 1:
            result = optimum_by_greed_with_group(self.data, ratios[0], names=[names[0], "other"],
                                                 group_pattern=pattern)
            gr1, gr2 = calc_ratio(
                result['ratio_summ'][0], result['ratio_summ'][1])
            self.result[names[0]] = {"data": result[names[0]].values(
            ), "ratio": gr1, "img": result[names[0]].keys()}

        elif cols == 2:
            result = optimum_by_greed_with_group(self.data, ratios[0], names=[names[0], names[1]],
                                                 group_pattern=pattern)
            gr1, gr2 = calc_ratio(
                result['ratio_summ'][0], result['ratio_summ'][1])

            self.result[names[0]] = {"data": result[names[0]].values(
            ), "ratio": gr1, "img": result[names[0]].keys()}
            self.result[names[1]] = {"data": result[names[1]].values(
            ), "ratio": gr2, "img": result[names[1]].keys()}

        elif cols == 3:
            result = optimum_by_greed_with_group(self.data, ratios[0], names=[names[0], "combined"],
                                                 group_pattern=pattern)
            gr1, gr2_3 = calc_ratio(
                result['ratio_summ'][0], result['ratio_summ'][1])

            corrected_ratio = round(
                ratios[1] * 100 / (100 - ratios[0] * 100), 2)  # корректируем значение в %
            result2 = optimum_by_greed_with_group(result["combined"], corrected_ratio,
                                                  names=[names[1], names[2]], group_pattern=pattern)
            gr2, gr3 = calc_ratio(
                result2['ratio_summ'][0], result2['ratio_summ'][1])

            # пересчитываем проценты с учетом исходного соотношения
            for i, perc in enumerate(gr2_3):
                gr2[i] = gr2[i] * perc / 100
                gr3[i] = 100 - gr2[i] - gr1[i]

            self.result[names[0]] = {"data": result[names[0]].values(
            ), "ratio": gr1, "img": result[names[0]].keys()}
            self.result[names[1]] = {"data": result2[names[1]].values(
            ), "ratio": gr2, "img": result2[names[1]].keys()}
            self.result[names[2]] = {"data": result2[names[2]].values(
            ), "ratio": gr3, "img": result2[names[2]].keys()}

        end_time = time.time()

        # информация о результате расчета
        text = (f"Обработано строк: {len(self.data.keys())}; "
                f"занятое время: {format_time(end_time - start_time, 'ru')}, "
                f"величина расхождения: {result['error']:.1f}")
        headers = ["Выборка", "records"]  # заголовки таблицы результатов
        headers.extend(f"cls{i:02d}" for i in range(
            1, len(self.result[names[0]]['ratio']) + 1))

        data = []  # данные для отображения
        for name, res_dict in self.result.items():
            row = [name, len(res_dict['data'])] + [round(rat, 0)
                                                   for rat in res_dict['ratio']]
            data.append(row)

        model = AzSimpleModel(data, headers)
        self.table_view.setModel(model)
        header = self.table_view.horizontalHeader()
        for col in range(model.columnCount()):  # выравниваем столбцы
            header.setSectionResizeMode(
                col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        if len(self.result) > 0:
            self.btn_status.setIcon(new_icon("circle_green"))

        self.sort_info.setText(text)  # отображаем сообщение
        if len(self.result) > 0:
            self.button_ok.setEnabled(True)

    def update_sort_cols(self):
        """Формируем перечень групп сортировки"""
        self.sort_cols = {widget.checkbox.text(): widget.spinbox.value() for widget in self.sort_widgets if
                          widget.checkbox.isChecked()}
        if len(self.sort_cols) < 1:  # отключаем кнопки или...
            self.button_sort.setEnabled(False)
        else:  # ...включаем кнопки
            self.button_sort.setEnabled(True)

    def check_values(self):
        """Проверка значений перед отправкой на отрисовку"""
        summ = sum(widget.spinbox.value(
        ) for widget in self.sort_widgets if widget.checkbox.isChecked())  # общая сумма
        # количество объектов
        active_numbers = sum(
            1 for widget in self.sort_widgets if widget.checkbox.isChecked())
        [widget.spinbox.setMaximum(100 - active_numbers + 1)
         for widget in self.sort_widgets]  # изменяем максимум

        if summ > 100:  # сумма начала превышать 100, следует это скорректировать
            sender_spinbox = self.sender().spinbox  # определяем отправителя сигнала
            sender_value = sender_spinbox.value()
            excess = summ - 100  # размер превышения

            for widget in self.sort_widgets:
                if widget.spinbox is not sender_spinbox:
                    if widget.checkbox.isChecked() and widget.spinbox.value() > 1:
                        new_value = widget.spinbox.value() - excess
                        widget.spinbox.setValue(max(1, new_value))
                        break

            sender_spinbox.setValue(sender_value)

        self.update_sort_cols()  # обновляем внутренние значения групп сортировки
        self.update_color_bar()  # обновляем виджет-индикатор соотношения

    def update_color_bar(self):
        """Обновление индикатора соотношения при изменении состояния или значения"""
        values_labels_colors = [(widget.spinbox.value(), widget.color, widget.checkbox_text) for widget in
                                self.sort_widgets if widget.checkbox.isChecked()]  # с учетом флага отметки
        self.color_bar.update_values(values_labels_colors)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzSortingDatasetDialog", text)

    def translate_ui(self):  # переводим диалог
        # Processing - Attributes - Smart Sorting
        self.table_widget.translate_ui()


# ----------------------------------------------------------------------------------------------------------------------
def get_group_objects(data_for_group, pattern=helper.PATTERNS.get("double_underscore")):
    """Разбиение на группы объектов по заданному паттерну. Принимает данные 
     (data_for_group) и шаблон разбиения (pattern). Возвращает список 
    с перечнем успешно найденных наименований групп.

    Example: пусть имеется словарь family = {"dad": [], "br0ther": [], "pet": [], "f1sh": []} 
     get_group_objects(family, '\d'), функция вернет ['0', '1']"""

    objects = set()
    for item in data_for_group:
        match = re.search(pattern, item)
        if match:
            objects.add(match.group(0))
    return objects


def calc_ratio(train_ratio, val_ratio):
    """Расчет и вывод статистики для выборок"""
    if len(train_ratio) != len(val_ratio):
        raise ValueError("Списки должны быть одинаковой длины")
    # на 0 делить нельзя, поэтому вводим правило, и считаем сумму/столбец для train и val
    train_percentages = [(t / (t + v)) * 100 if (t + v) !=
                         0 else 0 for t, v in zip(train_ratio, val_ratio)]
    val_percentages = [(v / (t + v)) * 100 if (t + v) !=
                       0 else 0 for t, v in zip(train_ratio, val_ratio)]
    return train_percentages, val_percentages


def check_key(key, pattern_type, group):
    if pattern_type == "start":
        return key.startswith(group)
    else:
        return re.search(group, key)
    

def group_data_by_pattern(data: dict, pattern: str, pattern_type: str) -> Tuple[Dict, Dict]:
    """
    Объединение данных и суммация их значений по заданному шаблону.
    Example. Принимаем словарь типа {"bar": [3, 2, 0, 3], "bond": [1, 3, 1, 1], "cell": [2, 0, 0, 3]}, с шаблоном
    типа r"^." и поиском типа "start" получаем словарь новых значений { "b": [4, 5, 1, 4], "c": [2, 0, 0, 3]} 
    и словарь связанных ключей {"b": ["bar", "bond"], "c":["cell"]}
    """
    if not data:
        raise ValueError("Отсутствуют исходные данные")

    groups = get_group_objects(data.keys(), pattern)
    if not groups:
        raise ValueError("По заданному шаблону ничего не найдено")

    melted_data = copy.deepcopy(data)  # делаем копию словаря
    group_data, group_keys = {}, {}  # создаем словари новых данных и ключей к ним
    _, n = next(iter(melted_data.items()))
    if n:
        n = len(n) # узнаем размерность
    else:
        raise ValueError("Исходные данные некоректны")

    for group in groups:
        key_records = []  # связанные значения
        keys_to_remove = []  # список ключей для удаления
        summ_for_group = np.zeros(n, dtype=int)  # сумма для группы

        # для изображений: key - имя изображения
        for key, val in melted_data.items():
            if check_key(key, pattern_type, group):
                key_records.append(key)
                summ_for_group += np.array(val)
                keys_to_remove.append(key)

        if len(key_records) > 0: # для этой группы найдены данные
            group_data[group] = summ_for_group.tolist()  # преобразуем в лист
            group_keys[group] = key_records
            for key in keys_to_remove:  # удаляем ключи из словаря
                melted_data.pop(key, None)

    return group_data, group_keys


def optimum_by_greed_with_group(data: dict, ratio: float = 0.8, names: list[str, str] = ["train", "val"],
                                group_pattern=None, group_beih="start") -> dict:
    """Поиск оптимального разбиения на основе жадного алгоритма. Возвращает словарь 
     с именами групп и соответствующим им данным; суммарным значением соотношений; 
    значением ошибки.

    Args: 
        data: словарь исходных данных типа  
         {"dad": [5, 7], "sister": [2, 3], "mom": [2, 5]}
        names: названия групп, по умолчанию "train", "val"
        ratio: размер отношения для первой группы ("train") в долях (от 1 до 0; 70% = 0.7)
        group_pattern: шаблон образования групп; если None то группировка не используется,
        group_beih: тип формирования групп: "start" - поиск сначала строки или "re" - классический 
         поиск, (!) при его использованнии следует учитывать формирование set() и образование последовательных 
        групп.

    Return:
        (dict) словарь результатов, типа 
         {train:{"mom":[2, 5], "sister":[2, 3]}, val:{"dad":[5, 7]}, ratio:[[4, 8], [5, 7]], error: 3.5}
     """
    if group_pattern:  # есть необходимость использования групп
        group_data, group_links = group_data_by_pattern(
            data, group_pattern, group_beih)  # упаковываем данные
        if not group_data:
            print("Группировка по заданным параметрам не выполнена.")
            return None
        data_array = np.array(list(group_data.values()))
        keys = list(group_data.keys())
    else:
        # преобразуем в массив numpy для оптимизации
        data_array = np.array(list(data.values()))
        keys = list(data.keys())  # сохраняем список ключей

    total_sums = np.sum(data_array, axis=0)  # сумма каждой колонки
    train_score = total_sums * ratio  # рассчитываем идеальное соотношение
    train_keys, val_keys = [], []  # ключи для выходных данных

    sums = np.sum(data_array, axis=1)  # считаем суммы строк
    sorted_idx = np.argsort(sums)[::-1]  # сортируем данные через индексы
    # нулевые матрицы для сумм
    train_sums, val_sums = np.zeros(data_array.shape[1], dtype=int), np.zeros(
        data_array.shape[1], dtype=int)

    for i in sorted_idx:  # используем жадный алгоритм для разбиения данных на отсортированных индексах
        row = data_array[i]
        if all(train_sums + row <= train_score):
            # индексы отсортированы, но сами значения верные
            train_keys.append(keys[i])
            train_sums += row
        else:
            val_keys.append(keys[i])
            val_sums += row

    error = calculate_error(train_sums, val_sums, ratio)  # величина ошибки

    result = {}  # словарь выходных данных
    if group_pattern:  # если были использованы группы
        # имеем набор данных train и val, которые надо распаковать
        unpack_train, unpack_val = {}, {}
        print("train:", train_keys)
        print("val:", val_keys)
        for group in train_keys:  # просматриваем список групп: '022_AUT', '030_BEL'...)
            # смотрим словарь связей: {'022_AUT': "aut_01.jpg", "aut_02.jpg", ... }
            for item in group_links[group]:
                unpack_train[item] = data[item]
        for group in val_keys:
            for item in group_links[group]:
                unpack_val[item] = data[item]
        result[names[0]] = unpack_train
        result[names[1]] = unpack_val

    else:  # простой вариант
        # списки для выходных данных train и val...
        train_dict = {key: data[key] for key in train_keys if key in data}
        # ...строим по ключам через исходные "data"
        val_dict = {key: data[key] for key in val_keys if key in data}
        result[names[0]] = train_dict
        result[names[1]] = val_dict

    # не пробуем оптимизацию, слишком затратно
    #  optimization_swap(result[names[0]], result[names[1]], ratio, error)

    result["ratio_summ"] = [train_sums.tolist(), val_sums.tolist()]  # итоговое
    result["error"] = error  # значение ошибки
    return result


def calculate_error(train_sums, val_sums, ratio):
    """Расчет величины ошибки производится как модуль разницы между train и val суммами всех столбцов"""
    return np.sum(np.abs(train_sums * (1 - ratio) - val_sums * ratio))


# ----------------------------------------------------------------------------------------------------------------------
# Функции показавшие неудовлетворительную вычислительную стоимость
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
                    new_train, new_val = move_rows(
                        array_train.copy(), array_val.copy(), train_indices)
                    # ...теперь (при необходимости перемещаем строки из val в train)
                    new_train, new_val = move_rows(
                        new_val, new_train, val_indices)

                    # Считаем суммы по столбцам и ошибку
                    train_sums, val_sums = np.sum(
                        new_train, axis=0), np.sum(new_val, axis=0)
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
