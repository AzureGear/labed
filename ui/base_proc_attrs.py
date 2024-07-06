from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper, config
from utils.sama_project_handler import DatasetSAMAHandler
from ui import new_button, AzButtonLineEdit, coloring_icon, new_text, az_file_dialog, save_via_qtextstream, new_act, \
    AzInputDialog, az_custom_dialog
import os

the_color = UI_COLORS.get("processing_color")


# ----------------------------------------------------------------------------------------------------------------------

class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabAttributesUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Attributes"
        self.tool_tip_title = "Searching and editing dataset attributes"
        if color_active:
            self.icon_active = coloring_icon("glyph_attributes", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_attributes", color_inactive)

        self.current_file = None  # текущий файл

        # Настройка ui
        wid = QtWidgets.QWidget()
        self.setCentralWidget(wid)
        self.label_project = QtWidgets.QLabel("Path to file project *.json:")
        self.file_json = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Load dataset SAMA project"),
                                          read_only=True, dir_only=False, filter=self.tr("Projects files (*.json)"),
                                          on_button_clicked_callback=self.attr_load_projects_data,
                                          initial_filter="json (*.json)")

        self.dataset_info_images_desc = new_text(self, "Count of images: ", alignment="r")
        self.dataset_info_images_val = new_text(self, "-", bald=False)
        self.dataset_info_labels_desc = new_text(self, "Count of labels: ", "indianred", "r")
        self.dataset_info_labels_val = new_text(self, "-", "indianred", bald=False)
        self.dataset_info_lrm_desc = new_text(self, "Average GSD:", alignment="r")
        self.dataset_info_lrm_val = new_text(self, "-", bald=False)
        self.dataset_info_devi_lrm_desc = new_text(self, "Deviation GSD:", "peru", "r")
        self.dataset_info_devi_lrm_val = new_text(self, "-", "peru", bald=False)
        self.labels_dataset_info = [self.dataset_info_images_desc, self.dataset_info_labels_desc,
                                    self.dataset_info_lrm_desc, self.dataset_info_devi_lrm_desc]
        self.labels_dataset_val = [self.dataset_info_images_val, self.dataset_info_labels_val,
                                   self.dataset_info_lrm_val, self.dataset_info_devi_lrm_val]

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
        hlay2 = QtWidgets.QHBoxLayout()
        hlay2.setSpacing(0)

        # информация о датасете: количество снимков в датасете, количество меток, среднее ЛРМ, девиация ЛРМ
        for i in range(4):
            hlay2.addWidget(self.labels_dataset_info[i])
            hlay2.addWidget(self.labels_dataset_val[i])

        #  Перечень действий с файлом проекта: копия+; экспорт+; сохранить палитру+; применить палитру+;
        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addLayout(hlay)
        vlay2.addLayout(hlay2)
        self.btn_copy = new_button(self, "tb", icon="glyph_duplicate", slot=self.attrs_copy_project, color=the_color,
                                   icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                   tooltip=self.tr("Make copy of current project"))
        self.btn_export = new_button(self, "tb", icon="glyph_check_all", slot=self.attrs_export, color=the_color,
                                     icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                     tooltip=self.tr("Export current project info"))
        self.btn_save_palette = new_button(self, "tb", icon="glyph_palette", slot=self.attrs_save_palette,
                                           color=the_color,
                                           icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                           tooltip=self.tr("Save palette from current project"))
        self.btn_apply_palette = new_button(self, "tb", icon="glyph_paint_brush", slot=self.attrs_apply_palette,
                                            color=the_color,
                                            icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                            tooltip=self.tr("Apply palette for current project"))
        self.common_buttons = [self.btn_copy, self.btn_save_palette, self.btn_apply_palette, self.btn_export]
        hlay3 = QtWidgets.QHBoxLayout()
        hlay3.addSpacing(50)
        for button in self.common_buttons:
            hlay3.addWidget(button)
        hlay_finish = QtWidgets.QHBoxLayout()
        hlay_finish.addLayout(vlay2)
        hlay_finish.addLayout(hlay3)

        # заголовок для таблицы
        self.headers = (
            self.tr("Label name"), self.tr("Number of\nlabels"), self.tr("Frequency of\nappearance\non the image"),
            self.tr("Percentage\nof total\nlabels"), self.tr("Averange\narea,\npixels"), self.tr('SD of area,\npixels'),
            self.tr("Balance"), self.tr("Color"), self.tr("Action"))
        # (имя класса, количество объектов, частота встречаемости на изображении, проценты от общего, средний размер, сбалансированность
        # класса, палитра, действия)

        # данные из проекта SAMA будут загружаться в DatasetSAMAHandler
        self.sama_data = DatasetSAMAHandler()  # делаем изначально пустым

        # данные из DatasetSAMAHandler будут отображаться в таблице
        self.table_widget = AzTableAttributes(headers=self.headers, special_cols={7: "color", 8: "action"},
                                              data=None, parent=self)  # и таблица тоже пустая
        header = self.table_widget.horizontalHeader()  # настраиваем отображение столбцов
        for column in range(self.table_widget.columnCount()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # первый столбец доминантный

        # смотрим, есть ли в реестре файл, который запускали прошлый раз?
        if os.path.exists(self.settings.read_attributes_input()):
            self.load_project(self.settings.read_attributes_input())  # пробуем его загрузить
        else:  # файла нет, тогда ограничиваем функционал
            self.toggle_tool_buttons(False)

        # итоговая настройка ui
        vlayout = QtWidgets.QVBoxLayout(self)  # главный Layout, наследуемый класс
        vlayout.addLayout(hlay_finish)  # добавляем ему расположение с кнопками и QLabel
        vlayout.addWidget(self.table_widget)
        wid.setLayout(vlayout)

        # Signals
        self.table_widget.signal_message.connect(self.forward_signal)
        self.table_widget.signal_reload.connect(self.reload_project)

    def forward_signal(self, message):  # перенаправление сигналов
        self.signal_message.emit(message)

    def reload_project(self, b):
        if b:
            self.load_project(self.current_file)

    def attr_actions_disable(self, message):  # сброс всех форм при загрузке, а также отключение инструментов
        self.current_file = None
        self.toggle_tool_buttons(False)
        self.clear_dataset_info()
        self.table_widget.clear_table()
        self.signal_message.emit(message)

    def clear_dataset_info(self):
        for label in self.labels_dataset_val:
            label.setText("-")

    def toggle_tool_buttons(self, b):  # отключаем инструменты для датасета
        for button in self.common_buttons:
            button.setEnabled(b)

    def attr_load_projects_data(self):
        if len(self.file_json.text()) < 5:  # недостойно внимания
            return
        self.load_project(self.file_json.text())

    def load_project(self, filename):  # загрузка проекта
        self.sama_data.load(filename)
        if not self.sama_data.is_correct_file:
            self.attr_actions_disable(
                self.tr("Выбранный файл не является корректным либо не содержит необходимых данных"))
            self.file_json.clear()
            return

        # Все загружено и всё корректно, поэтому записываем его в реестр и начинаем процедуру загрузки
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        self.file_json.setText(filename)
        self.current_file = filename
        self.settings.write_attributes_input(filename)
        self.toggle_tool_buttons(True)
        self.load_dataset_info()  # загружаем общее инфо о датасете
        self.table_widget.load_table_data(self.sama_data)  # обновляем данные для таблицы
        self.signal_message.emit(self.tr(f"Loaded project file: {filename}"))
        QtWidgets.QApplication.restoreOverrideCursor()

    def load_dataset_info(self):  # общая информация о датасете
        self.dataset_info_labels_val.setText(str(len(self.sama_data.data["labels"])))
        self.dataset_info_images_val.setText(str(self.sama_data.get_images_num()))

        # рассчитаем ЛРМ
        min_lrm = float('inf')
        max_lrm = float('-inf')
        no_lrm = 0
        all_count = 0
        summ = 0
        count = 0

        for image in self.sama_data.data["images"]:
            res = self.sama_data.get_image_lrm(image)
            if res is not None:
                min_lrm = min(min_lrm, res)
                max_lrm = max(max_lrm, res)
                summ += res
                count += 1
            else:
                no_lrm += 1  # изображений без ЛРМ
            all_count += 1

        if all_count != no_lrm:
            # округляем всё с точностью до 2 знаков после запятой
            self.dataset_info_devi_lrm_val.setText(f"{round(min_lrm, 2):.2f}-{round(max_lrm, 2):.2f}")
            self.dataset_info_lrm_val.setText(f"{round(summ / count, 2):.2f}")

    def attrs_copy_project(self):  # копирование проекта
        file = az_file_dialog(self, self.tr("Make copy project file and load it"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="json (*.json)",
                              initial_filter="json (*.json)")
        if file is None:
            return
        if len(file) < 1:  # если всё в порядке...
            return
        # ...копируем и загружаем
        import shutil
        shutil.copyfile(self.current_file, file)
        self.load_project(file)

    def attrs_save_palette(self):  # сохранение палитры
        """Извлечь и сохранить палитру из проекта SAMA"""
        json = helper.load(self.file_json.text())
        colors = json["labels_color"]
        data = dict()
        data["labels_color"] = colors
        file = az_file_dialog(self, self.tr("Save project SAMA *.json palette"), self.settings.read_last_dir(),
                              dir_only=False, file_to_save=True, filter="Palette (*.palette)",
                              initial_filter="palette (*.palette)")
        if len(file) > 0:
            helper.save(file, data, 'w+')  # сохраняем файл как палитру
        self.signal_message.emit(self.tr(f"Palette saved to: &{file}"))

    def attrs_apply_palette(self):  # применение палитры
        """Применить палитру к файлу проекта SAMA"""
        # загружаем файл с палитрой
        sel_file = az_file_dialog(self, self.tr("Apply palette file to current project"), self.settings.read_last_dir(),
                                  dir_only=False, filter="Palette (*.palette)", initial_filter="palette (*.palette)")
        if not helper.check_file(sel_file[0]):
            return
        palette = helper.load(sel_file[0])
        colors = palette["labels_color"]  # выгружаем цвета палитры
        json = helper.load(self.current_file)
        input_colors = json["labels_color"]

        # обходим ключи
        for color in input_colors:
            if color in colors:  # такой цвет есть в нашей палитре
                input_colors[color] = colors[color]
        json["labels_color"] = input_colors
        helper.save(self.current_file, json, "w+")
        self.load_project(self.current_file)  # перезагружаем файл, чтобы поменялась палитра

    def attrs_export(self):
        """ Экспорт табличных данных проекта SAMA в текстовый файл """
        file = az_file_dialog(self, self.tr("Export table data to text file"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="txt (*.txt)",
                              initial_filter="txt (*.txt)")
        if len(file) > 0:  # сохраняем в файл, при этом пропускаем определенные столбцы
            if save_via_qtextstream(self.table_widget, file, [6]):
                self.signal_message.emit(self.tr(f"Table data export to: {file}"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabAttributesUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes
        self.table_widget.translate_ui()
        self.label_project.setText(self.tr("Path to file project *.json:"))
        self.dataset_info_images_desc.setText(self.tr("Numbers of images: "))
        self.dataset_info_labels_desc.setText(self.tr("Numbers of labels: "))
        self.dataset_info_lrm_desc.setText(self.tr("Average GSD:"))
        self.dataset_info_devi_lrm_desc.setText(self.tr("Deviation GSD:"))
        self.btn_copy.setToolTip(self.tr("Make copy of current project"))
        self.btn_export.setToolTip(self.tr("Export current project info"))
        self.btn_save_palette.setToolTip(self.tr("Save palette from current project"))
        self.btn_apply_palette.setToolTip(self.tr("Apply palette for current project"))


# ----------------------------------------------------------------------------------------------------------------------

class AzTableAttributes(QtWidgets.QTableWidget):
    """
    Таблица для взаимодействия с QTabWidget для работы с MNIST:
    headers - перечень заголовков (может быть переводимым, если translate_headers = True).
    special_cols - словарь особых столбцов: ключ - номер столбца, значение - acton или color; может быть None, следует
        помнить, что нумерация идет с 0.
    data - данные для таблицы, если тип данных DatasetSAMAHandler, то записываются в self.my_data.
    Пример: tb = AzTableAttributes(headers=self.headers, special_cols={5: "color", 6: "action"},data=None, parent=self)
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    signal_reload = QtCore.pyqtSignal(bool)  # сигнал для перезагрузки данных

    def __init__(self, headers=("Column 1", "Column 2", "Actions"), special_cols=None, data=None, parent=None,
                 translate_headers=False, current_file=None):
        # создать заголовки, построить ячейки, заполнить данными, заполнить особыми столбцами
        super(AzTableAttributes, self).__init__(parent)
        self.current_file = current_file
        self.special_cols = special_cols
        self.translate_headers = translate_headers  # надобность перевода
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)  # заголовки
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # выделение построчно
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # отключаем редактирование
        self.setSortingEnabled(True)  # включаем сортировку
        self.setAlternatingRowColors(True)  # включаем чередование цветов
        self.my_data = data  # по умолчанию данных нет
        self.clear_table()
        if data is not None:
            self.load_table_data(data)

    def clear_table(self):  # простая очистка таблицы
        self.setRowCount(0)

    def set_special_cols(self):  # установка особых типов столбцов: action - меню; color - цвет;
        for column, item_type in self.special_cols.items():
            if item_type == "color":
                for row in range(self.rowCount()):
                    self.setCellWidget(row, column, self.add_color_button(row))
            elif item_type == "action":
                for row in range(self.rowCount()):
                    self.setCellWidget(row, column, self.add_action_button(row))

    def add_action_button(self, row):  # добавление кнопки меню
        act_button = new_button(self, "tb", icon="glyph_menu", color=the_color, tooltip=self.tr("Select action"),
                                icon_size=14)
        act_button.setAutoRaise(True)
        act_button.clicked.connect(lambda ch, row=row: self.show_context_menu(row))
        return act_button

    def add_color_button(self, row):  # добавление цветной кнопки выбора цвета
        color_button = new_button(self, "tb", tooltip=self.tr("Select color"))
        color_button.setStyleSheet("QToolButton { background-color: rgb(0, 0, 0); }")  # по умолчанию черного цвета
        color_button.clicked.connect(lambda ch, btn=color_button, row=row: self.change_color(btn, row))
        return color_button

    def load_table_data(self, data):
        self.clear_table()
        if isinstance(data, DatasetSAMAHandler):  # установка данных SAMA, если они переданы
            self.my_data = data
            self.load_sama_data()
        else:
            # заглушка на другие типы данных
            pass

    def load_sama_data(self):
        labels = self.my_data.get_labels()
        self.setRowCount(len(labels))  # число строк
        col_color = None  # по умолчанию "цветного" столбца нет

        # устанавливаем особые столбцы
        if self.special_cols is not None and self.my_data is not None:  # в конец, т.к. изначально установим цвет
            self.set_special_cols()
            col_color = next((k for k, v in self.special_cols.items() if v == "color"), None)  # номер столбца

        stat = self.my_data.calc_stat()  # рассчитываем статистику

        for row, name in enumerate(labels):
            if col_color:  # заполнение кнопки цветом
                color_tuple = self.my_data.get_label_color(name)
                color = QtGui.QColor(*color_tuple)
                button = self.cellWidget(row, col_color)
                button.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
            self.add_item_text(row, 0, name)  # имя класса/метки
            self.add_item_number(row, 1, stat[name]['count'])  # количество объектов/меток
            self.add_item_number(row, 2, stat[name]['frequency'], 1)  # частота встречаемости на изображении
            self.add_item_number(row, 3, stat[name]['percent'], 2)  # проценты от общего
            self.add_item_number(row, 4, stat[name]['size']['mean'], 1)  # средний размер
            self.add_item_number(row, 5, stat[name]['size']['std'], 1)  # СКО размера

    def add_item_text(self, row, col, text):  # устанавливаем текстовое значение
        item = QtWidgets.QTableWidgetItem(text)
        # item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.setItem(row, col, item)

    def add_item_number(self, row, col, number, acc=0):  # устанавливаем числовое значение
        item = QtWidgets.QTableWidgetItem()
        item.setData(QtCore.Qt.EditRole, round(float(number), acc))
        self.setItem(row, col, item)

    def fill_column(self, col, text_data):  # заполнение столбца данными
        for row, text in enumerate(text_data):
            new_item = QtWidgets.QTableWidgetItem(text)
            self.setItem(row, col, new_item)

    def change_color(self, button, row):
        color = QtWidgets.QColorDialog.getColor(button.palette().color(button.backgroundRole()), self,
                                                self.tr("Select label color"))
        self.selectRow(row)
        # parent = window, title = "Окно выбора цвета",
        #                          options = QtWidgets.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            button.setStyleSheet(
                f"QToolButton {{ background-color: rgb({color.red()}, {color.green()}, {color.blue()}); }}")

    def show_context_menu(self, row):
        """Дополнительное меню действий с именами меток/классами"""
        menu = QtWidgets.QMenu()
        self.selectRow(row)
        rename_act = new_act(self, self.tr("Rename"), "glyph_signature", the_color, tip=self.tr("Rename current label"))
        rename_act.triggered.connect(lambda ch, the_row=row: self.label_rename(row))

        delete_act = new_act(self, self.tr("Delete"), "glyph_delete2", the_color, tip=self.tr("Delete current label"))
        delete_act.triggered.connect(lambda ch, the_row=row: self.label_delete(row))

        merge_act = new_act(self, self.tr("Merge"), "glyph_merge", the_color,
                            tip=self.tr("Merge current label to other label"))
        merge_act.triggered.connect(lambda ch, the_row=row: self.label_merge(row))

        acts = [rename_act, merge_act, delete_act]
        menu.addActions(acts)
        pos = QtGui.QCursor.pos()
        menu.exec_(pos)

    def label_rename(self, row):
        """ Перечень действий: переименовать класс"""
        current_names = self.my_data.get_labels()
        print(current_names)
        dialog = AzInputDialog(self, 1, [self.tr("Enter new label name:")], "Rename label", input_type=[0],
                               cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные
        if result[0] in current_names:
            self.signal_message.emit(
                self.tr(f"The specified name '{result[0]}' is present in the dataset, rename was canceled."))
            return
        if result is not None:
            self.item(row, 0).setText(result[0])
            self.signal_message.emit(self.tr(f"Objects with label '{row}' was renamed to '{result[0]}'"))
            # TODO: self.save data

    def label_delete(self, row):
        """ Перечень действий: удалить метку"""
        dialog = az_custom_dialog(self.tr("Label deleting"),
                                  (self.tr("Are you sure you want to delete all objects related to this label?")), True,
                                  True, parent=self)
        if dialog != 1:  # если не "утверждение", то выходим
            return
        name = self.item(row, 0).text()
        print(name)  # delete_data_by_class_number
        self.my_data.delete_data_by_class_name(name)
        self.my_data.save(self.parent().current_file)
        self.signal_reload.emit(True)
        self.signal_message.emit(self.tr(f"Objects with label '{name}' was deleted"))

    def label_merge(self, row):
        """ Перечень действий: слить с другой меткой"""
        # TODO: merge
        names = ["John", "Mary", "Bob", "Alice"]
        if self.my_data is None:
            return
        names = self.my_data.get_labels()
        print(self.item(row, 0))
        # names.remove(self.item(row,0))
        dialog = AzInputDialog(self, 1, [self.tr("Select the label to merge with:")], "Merge labels", input_type=[1],
                               combo_inputs=[names], cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные
        self.signal_message.emit(self.tr(f"Merged object with labels {row} и {result[0]}"))

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

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TabAttributesUI()
    window.show()
    sys.exit(app.exec_())
