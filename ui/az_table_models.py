from PyQt5 import QtWidgets, QtGui, QtCore
from ui import new_act, new_button, set_widgets_and_layouts_margins, AzInputDialog, az_custom_dialog
from utils import config, DatasetSAMAHandler
import copy


class AzTableAttributes(QtWidgets.QTableWidget):
    """
    Таблица для взаимодействия с общей статистикой данных проекта SAMA *.json:
    headers - перечень заголовков (может быть переводимым, если translate_headers = True*), *пока не реализовано
    special_cols - словарь особых столбцов: ключ - номер столбца, значение - acton или color; может быть None, следует
        помнить, что нумерация идет с 0.
    data - данные для таблицы, если тип данных DatasetSAMAHandler, то записываются в self.my_data.
    Пример: tb = AzTableAttributes(headers=self.headers, special_cols={5: "color", 6: "action"},data=None, parent=self)
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    signal_data_changed = QtCore.pyqtSignal(str)  # сигнал об изменении в данных

    def __init__(self, headers=None, special_cols=None, data=None, parent=None,
                 translate_headers=False, current_file=None, color=QtGui.QColor.red, row_h=16):
        # создать заголовки, построить ячейки, заполнить данными, заполнить особыми столбцами
        super(AzTableAttributes, self).__init__(parent)
        self.row_h = row_h  # высота строк по умолчанию
        self.color = color  # устанавливаем переданный цвет
        self.col_color = None  # столбец цвета
        self.current_file = current_file
        self.special_cols = special_cols
        self.translate_headers = translate_headers  # надобность перевода
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)  # заголовки
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # выделение построчно
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # отключаем редактирование
        self.setSortingEnabled(True)  # включаем сортировку
        self.setAlternatingRowColors(True)  # включаем чередование цветов
        self.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.Alignment(QtCore.Qt.TextFlag.TextWordWrap))

    def clear_table(self):  # простая очистка таблицы
        self.setRowCount(0)

    def set_special_cols(self):  # установка особых типов столбцов: action - меню; color - цвет;
        for column, item_type in self.special_cols.items():
            if item_type == "color":
                for row in range(self.rowCount()):
                    self.setCellWidget(row, column, self.add_color_button())
            elif item_type == "action":
                for row in range(self.rowCount()):
                    self.setCellWidget(row, column, self.add_action_button())

    def add_action_button(self):  # добавление кнопки меню
        act_button = new_button(self, "tb", icon="glyph_menu", color=self.color, tooltip=self.tr("Select action"),
                                icon_size=14)
        act_button.clicked.connect(self.show_context_menu)
        # act_button.clicked.connect(lambda ch, row=row: self.show_context_menu(row))
        return act_button

    def add_color_button(self):  # добавление цветной кнопки выбора цвета
        color_button = new_button(self, "tb", tooltip=self.tr("Select color"))
        color_button.setStyleSheet("QToolButton { background-color: rgb(0, 0, 0); }")  # по умолчанию черного цвета
        color_button.clicked.connect(self.change_color)
        # color_button.clicked.connect(lambda ch, btn=color_button, row=row: self.change_color(btn, row))
        return color_button

    def show_context_menu(self):
        """Дополнительное меню действий с именами меток/классами"""
        button = self.sender()  # определяем от кого пришёл сигнал
        index = self.indexAt(button.pos())  # вот и индекс (проклятье, часа четыре потратил на эти 3 строчки!)
        row = index.row()

        menu = QtWidgets.QMenu()
        rename_act = new_act(self, self.tr(f"Rename"), "glyph_signature", self.color,
                             tip=self.tr("Rename current label"))
        rename_act.triggered.connect(lambda ch, the_row=row: self.label_rename(row))

        delete_act = new_act(self, self.tr("Delete"), "glyph_delete2", self.color, tip=self.tr("Delete current label"))
        delete_act.triggered.connect(lambda ch, the_row=row: self.label_delete(row))

        merge_act = new_act(self, self.tr("Merge"), "glyph_merge", self.color,
                            tip=self.tr("Merge current label to other label"))
        merge_act.triggered.connect(lambda ch, the_row=row: self.label_merge(row))

        acts = [rename_act, merge_act, delete_act]  # перечень наших действий
        menu.addActions(acts)

        pos = QtGui.QCursor.pos()
        menu.exec_(pos)

    def load_table_data(self, data):
        self.clear_table()
        if isinstance(data, DatasetSAMAHandler):  # установка данных SAMA, если они переданы
            self.my_data = data
            self.horizontalHeader().setFixedHeight(36)  # для SAMA
            self.load_sama_data()
        else:
            # заглушка на другие типы данных
            pass

    def load_sama_data(self):
        labels = self.my_data.get_labels()
        self.setRowCount(len(labels))  # число строк
        self.col_color = None  # по умолчанию "цветного" столбца нет

        # устанавливаем особые столбцы
        if self.special_cols is not None and self.my_data is not None:  # в конец, т.к. изначально установим цвет
            self.set_special_cols()
            self.col_color = next((k for k, v in self.special_cols.items() if v == "color"), None)  # номер столбца

        stat = self.my_data.calc_stat()  # рассчитываем статистику
        self.setSortingEnabled(False)  # обязательно отключить сортировку, иначе случится дичь
        for row, name in enumerate(labels):
            if self.col_color:  # заполнение кнопки цветом
                color_tuple = self.my_data.get_label_color(name)
                color = QtGui.QColor(*color_tuple)
                button = self.cellWidget(row, self.col_color)
                button.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
            # имя класса/метки
            self.add_item_text(row, 0, name, QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            self.add_item_number(row, 1, stat[name]['count'])  # количество объектов/меток
            self.add_item_number(row, 2, stat[name]['frequency'], 1)  # частота встречаемости на изображении
            self.add_item_number(row, 3, stat[name]['percent'], 2)  # проценты от общего
            self.add_item_number(row, 4, stat[name]['size']['mean'], 1)  # средний размер
            self.add_item_number(row, 5, stat[name]['size']['std'], 1)  # СКО размера
        self.setSortingEnabled(True)
        for row in range(self.rowCount()):  # выравниваем высоту
            self.setRowHeight(row, self.row_h)

    def add_item_text(self, row, col, text,
                      align=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter):
        """ Установка текстовых значений.
        row - строка, col - столбце,  text - текстовое значение, align - расположение значения по
        горизонтали | вертикали типа "Qt.AlignmentFlag"
        """
        item = QtWidgets.QTableWidgetItem(text)
        item.setTextAlignment(align)
        self.setItem(row, col, item)

    def add_item_number(self, row, col, number, acc=0,
                        align=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter):
        """ Установка числовых значений.
        row - строка, col - столбце, number - отображаемое число, acc - знаки с точностью после запятой
        align - расположение значения по горизонтали | вертикали типа "Qt.AlignmentFlag"
        """
        item = QtWidgets.QTableWidgetItem()
        item.setData(QtCore.Qt.ItemDataRole.EditRole, round(float(number), acc))
        item.setTextAlignment(align)
        self.setItem(row, col, item)

    def fill_column(self, col, text_data):  # заполнение столбца данными
        for row, text in enumerate(text_data):
            new_item = QtWidgets.QTableWidgetItem(text)
            self.setItem(row, col, new_item)

    def change_color(self):  # изменение цвета
        button = self.sender()  # определяем от кого пришёл сигнал
        index = self.indexAt(button.pos())
        row = index.row()
        name = self.item(row, 0).text()

        if self.col_color is None:
            return
        button = self.cellWidget(row, self.col_color)  # узнаем по какой кнопке щелкнули
        if button is None:
            self.signal_message.emit(self.tr("Something goes wrong. Can't assign a button"))
            return
        color_dialog = QtWidgets.QColorDialog(self)  # создаём и настраиваем диалог цвета
        color_dialog.setWindowTitle(self.tr("Select label color"))
        color_dialog.setCurrentColor(button.palette().color(button.backgroundRole()))  # начальный цвет
        result = color_dialog.exec_()  # запускаем
        if result != QtWidgets.QDialog.Accepted:
            return
        color = color_dialog.selectedColor()
        if color.isValid():
            button.setStyleSheet(
                f"QToolButton {{ background-color: rgb({color.red()}, {color.green()}, {color.blue()}); }}")
        self.my_data.set_label_color(name, [color.red(), color.green(), color.blue()])  # устанавливаем цвет и в данных
        self.signal_message.emit(
            self.tr(f"Label '{name}' color was changed to 'rgb({color.red()}, {color.green()}, {color.blue()})'"))
        self.signal_data_changed.emit(self.tr(f"Label color was changed to 'rgb({color.red()}, {color.green()}, "
                                              f"{color.blue()})'"))

    def label_rename(self, row):
        """ Перечень действий: переименовать класс"""
        names = self.my_data.get_labels()  # набор исходных имён
        current_name = self.item(row, 0).text()
        if current_name not in names:
            self.signal_message.emit(self.tr("Something goes wrong. Check input data."))
        dialog = AzInputDialog(self, 1, [self.tr("Enter new label name:")], input_type=[0],
                               window_title=f"Rename label '{self.item(row, 0).text()}'",
                               cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные

        # проверки
        if result is None:
            return
        if len(result) < 1:
            return
        if result[0] in names:
            self.signal_message.emit(
                self.tr(f"The specified name '{result[0]}' is present in the dataset, rename was canceled."))
            return
        self.my_data.change_name(current_name, result[0])
        self.item(row, 0).setText(result[0])
        self.signal_message.emit(self.tr(f"Objects with label '{current_name}' was renamed to '{result[0]}'"))
        self.signal_data_changed.emit(self.tr(f"Objects with label '{current_name}' was renamed to '{result[0]}'"))

    def label_delete(self, row):
        """ Перечень действий: удалить метку"""
        name = self.item(row, 0).text()
        dialog = az_custom_dialog(self.tr("Label deleting"),
                                  self.tr(f"Are you sure you want to delete all objects related to label '{name}'?"),
                                  parent=self)
        if dialog != 1:  # если не "утверждение", то выходим
            return

        if not self.my_data.filename:  # ошибка, дальше даже не стоит продолжать
            self.signal_message.emit(self.tr("Something goes wrong."))
            return
        self.my_data.delete_data_by_class_name(name)  # удаляем данные
        self.removeRow(row)
        self.signal_message.emit(self.tr(f"Objects with label '{name}' was deleted"))
        self.signal_data_changed.emit(self.tr(f"Objects with label '{name}' was deleted"))

    def label_merge(self, row):
        """Перечень действий: слить с другой меткой"""
        if self.my_data is None:
            return
        name = self.item(row, 0).text()  # имя текущей метки
        names = copy.copy(self.my_data.get_labels())  # имена всех меток
        if len(names) < 2:
            self.signal_message.emit(self.tr("There are not enough labels for merging."))
            return
        names.remove(name)  # сделать копию! ибо будет удаление

        dialog = AzInputDialog(self, 1, [self.tr(f"Select the label {name} to merge with:")],
                               self.tr("Merge labels"), input_type=[1],
                               combo_inputs=[names], cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные
        if result is None:
            return
        if len(result) < 1:
            return
        self.my_data.change_data_class_from_to(name, result[0])
        self.removeRow(row)
        self.signal_message.emit(self.tr(f"Merged object with labels '{name}' to '{result[0]}'"))
        self.signal_data_changed.emit(self.tr(f"Merged object with labels '{name}' to '{result[0]}'"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzTableAttributes", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes - AzTableAttributes
        self.setToolTip(self.tr("Data by classes (labels) of the dataset"))
        # Заголовки таблицы
        if self.translate_headers:
            pass
        # TODO: headers


# ----------------------------------------------------------------------------------------------------------------------

class AzSortTable(QtWidgets.QWidget):
    """Testestet"""

    def __init__(self, color, sort_type="train", parent=None, row_h=16, table_headers=["Images"]):
        super().__init__(parent)
        self.table_headers = table_headers
        self.row_h = row_h  # высота строк по умолчанию
        self.sort_type = sort_type  # строковое значение типа таблицы
        # Выбираем заголовок
        if sort_type == "train":
            self.ti_label = QtWidgets.QLabel(self.tr("Train table:"))
        elif sort_type == "val":
            self.ti_label = QtWidgets.QLabel(self.tr("Val table:"))
        elif sort_type == "test":
            self.ti_label = QtWidgets.QLabel(self.tr("Test table:"))

        # добавление
        self.ti_tb_sort_add_to = new_button(self, "tb", sort_type, "glyph_add2", color=color,
                                            tooltip=self.tr(f"Add image to {sort_type}"),
                                            icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)
        # добавление группы объектов
        self.ti_tb_sort_add_group_to = new_button(self, "tb", sort_type, "glyph_add_multi", color=color,
                                                  tooltip=self.tr(f"Add group to {sort_type}"),
                                                  icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)
        # удаление
        self.ti_tb_sort_remove_from = new_button(self, "tb", sort_type, "glyph_delete4", color=color,
                                                 tooltip=self.tr(f"Remove selected images from {sort_type}"),
                                                 icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        self.ti_tb_sort_remove_group_from = new_button(self, "tb", sort_type, "glyph_delete_multi", color=color,
                                                       tooltip=self.tr(f"Remove group from {sort_type}"),
                                                       icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        # создаем таблицу QTableView
        self.table_view = QtWidgets.QTableView()

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # горизонтальный спейсер

        h_lay = QtWidgets.QHBoxLayout()
        h_lay.addWidget(self.ti_label)
        h_lay.addWidget(self.ti_tb_sort_add_to)
        h_lay.addWidget(self.ti_tb_sort_add_group_to)
        h_lay.addWidget(spacer)
        h_lay.addWidget(self.ti_tb_sort_remove_group_from)
        h_lay.addWidget(self.ti_tb_sort_remove_from)
        h_lay.setSpacing(0)

        # итоговая настройка компоновки
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(0)
        layout.addLayout(h_lay)
        layout.addWidget(self.table_view, 1)  # делаем доминантным
        self.setLayout(layout)

        # Создаем базовую модель данных в которую помещаем исходные данные
        self.init_sort_models(self.table_headers, [])

        # Разрешаем выделение строк
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QTableView.SelectionMode.MultiSelection)
        self.align_rows_and_cols()  # высота строк и ширина столбцов единообразна

    def init_sort_models(self, headers=["Images"], data=[["aaa"], ["bbb"]]):
        self.core_model = AzSimpleModel(data, headers)  # с тестовыми данными
        self.model = QtCore.QSortFilterProxyModel()  # создаём второстепенную модель, которая позволяет сортировку
        self.model.setSourceModel(self.core_model)
        # Устанавливаем модель данных для QTableView
        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)  # включаем сортировку

    def align_rows_and_cols(self, resize=QtWidgets.QHeaderView.ResizeMode.Stretch):
        """Выравнивание всех строк и столбцов таблицы исходя из данных модели."""
        if self.model.columnCount() > 0:  # для столбцов
            header = self.table_view.horizontalHeader()
            for col in range(self.model.columnCount()):
                header.setSectionResizeMode(col, resize)
        if self.model.rowCount() > 0:  # для строк
            for row in range(self.model.rowCount()):  # выравниваем высоту
                self.table_view.setRowHeight(row, self.row_h)

    def set_sort_data_with_model(self, table_view, data):
        # TODO: подключить сортировку
        """Создание модели для таблиц сортировки и установка в table_view, выравнивание строк"""
        # обязательно конвертируем просто список в список списков
        data = [[item] for item in data]
        if len(data) < 1:
            model = AzTableModel()
        else:
            model = AzTableModel(data, ["images"])  # заголовок всего один "images"

        proxyModel = QtCore.QSortFilterProxyModel()  # используем для включения сортировки
        proxyModel.setSourceModel(model)
        table_view.setSortingEnabled(True)

        table_view.setModel(proxyModel)
        if table_view.model().columnCount() > 0:
            table_view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        if table_view.model().rowCount() > 0:
            for row in range(model.rowCount()):  # выравниваем высоту
                table_view.setRowHeight(row, self.row_h)


# ----------------------------------------------------------------------------------------------------------------------

class AzSimpleModel(QtCore.QAbstractTableModel):
    """Перезагруженный абстрактный класс для взаимодействия с QTableView. Поддерживает только обновление данных целиком
    через 'setData' и сортировку"""

    def __init__(self, data=None, headers=None):
        super().__init__()
        if headers is None:
            headers = []
        if data is None:
            data = []
        self._data = data
        self._headers = headers

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()
            value = self._data[row][column]
            return value

    def setData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self._data:
            return len(self._data)
        else:
            return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self._data:
            return len(self._data[0])
        else:
            return 0

    # def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
    #     if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
    #         if section < len(self._headers):
    #             return self._headers[section]
    #         else:
    #             return ""

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
        return section + 1


# ----------------------------------------------------------------------------------------------------------------------


class AzTableModel(QtCore.QAbstractTableModel):
    """
    Модель для отображения табличных данных, принимает лист листов [[x1, y1], [x2, y2]... ]
    Все методы "перегруженные" для минимального функционала. Настроена на внесение значений от 0 до 95 для
    редактируемого столбца (метод setData).
    vertical data - подписи для строк
    no_row_captions - не ставить названия у строк
    """

    def __init__(self, data=None, header_data=None, edit_column=None, parent=None, vertical_data=None,
                 no_rows_captions=False):
        super(AzTableModel, self).__init__(parent)
        self._data = data
        self._header_data = header_data
        self._vertical_data = vertical_data
        self._no_rows_captions = no_rows_captions
        self.edit_col = edit_column
        if self._data is None:
            self._header_data = [["no data available"]]

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
                return self._data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == QtCore.Qt.ItemDataRole.EditRole:
            if value > 95:  # если есть возможность редактирования
                value = 95
            elif value < 0:
                value = 0
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                if section < len(self._header_data):
                    return self._header_data[section]
                else:
                    return ""
            if orientation == QtCore.Qt.Orientation.Vertical:
                if self._vertical_data:
                    return str(self._vertical_data[section])
        if self._no_rows_captions:
            return None
        else:
            return section + 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        # Количество строк = всего элементов списка списков [[x1, y1], [x2, y2] ... >>[xN, yN]<< ]
        if self._data:
            return len(self._data)
        else:
            return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        # Количество столбцов = элементов внутреннего списка [[x1, >>y1<<], [x2, y2] ... [xN, yN]]
        if self._data:
            return len(self._data[0])
        else:
            return 0

    def flags(self, index: QtCore.QModelIndex):
        # Set ItemIsSelectable flag by default
        flag = super().flags(index)
        flag |= QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        if self.edit_col is not None:
            if index.column() == int(self.edit_col):
                flag |= QtCore.Qt.ItemFlag.ItemIsEditable
        return flag

    # def flags(self, index: QtCore.QModelIndex):
    #     # варианты возвращаемого флага:
    #     # ItemIsEditable | ItemIsEnabled | ItemIsSelectable
    #     flag = super().flags(index)
    #     if self.edit_col is not None:
    #         if index.column() == int(self.edit_col):
    #             flag |= QtCore.Qt.ItemFlag.ItemIsEditable
    #     else:
    #         flag |= QtCore.Qt.ItemFlag.ItemIsSelectable
    #     return flag  # type: ignore
