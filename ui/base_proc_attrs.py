from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper
from utils.sama_project_handler import DatasetSAMAHandler
from ui import new_button, AzButtonLineEdit, coloring_icon, new_text, az_file_dialog, save_via_qtextstream, new_act
import os

the_color = UI_COLORS.get("processing_color")


# ----------------------------------------------------------------------------------------------------------------------

# todo: проверка при переименовании, что новое имя not in list[...]

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

        # Настройка ui
        wid = QtWidgets.QWidget()
        self.setCentralWidget(wid)
        self.label_project = QtWidgets.QLabel("Path to file project *.json:")
        self.file_json = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Load dataset SAMA project"),
                                          read_only=True, dir_only=False, filter=self.tr("Projects files (*.json)"),
                                          on_button_clicked_callback=self.attr_load_projects_data,
                                          initial_filter="json (*.json)")

        self.dataset_info_images_desc = new_text(self, "Numbers of images: ", alignment="r")
        self.dataset_info_images_val = new_text(self, "13", bald=True)
        self.dataset_info_labels_desc = new_text(self, "Numbers of labels: ", "indianred", "r")
        self.dataset_info_labels_val = new_text(self, "42", "indianred", bald=True)
        self.dataset_info_lrm_desc = new_text(self, "Average GSD:", alignment="r")
        self.dataset_info_lrm_val = new_text(self, "0.62", bald=True)
        self.dataset_info_devi_lrm_desc = new_text(self, "Deviation GSD:", "peru", "r")
        self.dataset_info_devi_lrm_val = new_text(self, "0.22-0.89", "peru", bald=True)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
        hlay2 = QtWidgets.QHBoxLayout()
        hlay2.setSpacing(0)

        # информация о датасете: количество снимков в датасете, количество меток, среднее ЛРМ, девиация ЛРМ
        hlay2.addWidget(self.dataset_info_images_desc)
        hlay2.addWidget(self.dataset_info_images_val)
        hlay2.addWidget(self.dataset_info_labels_desc)
        hlay2.addWidget(self.dataset_info_labels_val)
        hlay2.addWidget(self.dataset_info_lrm_desc)
        hlay2.addWidget(self.dataset_info_lrm_val)
        hlay2.addWidget(self.dataset_info_devi_lrm_desc)
        hlay2.addWidget(self.dataset_info_devi_lrm_val)

        #  Перечень действий с файлом проекта: копия+; экспорт+; сохранить палитру+; применить палитру+;
        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addLayout(hlay)
        vlay2.addLayout(hlay2)
        self.btn_copy = new_button(self, "tb", icon="glyph_duplicate", slot=self.attrs_copy_project, color=the_color,
                                   icon_size=28, tooltip=self.tr("Make copy of current project"))
        self.btn_export = new_button(self, "tb", icon="glyph_check_all", slot=self.attrs_export, color=the_color,
                                     icon_size=28, tooltip=self.tr("Export current project info"))
        self.btn_save_palette = new_button(self, "tb", icon="glyph_palette", slot=self.attrs_save_palette,
                                           color=the_color,
                                           icon_size=28, tooltip=self.tr("Save palette from current project"))
        self.btn_apply_palette = new_button(self, "tb", icon="glyph_paint_brush", slot=self.attrs_apply_palette,
                                            color=the_color,
                                            icon_size=28, tooltip=self.tr("Apply palette for current project"))
        hlay3 = QtWidgets.QHBoxLayout()
        hlay3.addSpacing(50)
        hlay3.addWidget(self.btn_copy)
        hlay3.addWidget(self.btn_save_palette)
        hlay3.addWidget(self.btn_apply_palette)
        hlay3.addWidget(self.btn_export)
        hlay_finish = QtWidgets.QHBoxLayout()
        hlay_finish.addLayout(vlay2)
        hlay_finish.addLayout(hlay3)

        self.current_file = None  # текущий файл

        # данные из проекта SAMA будут загружаться в DatasetSAMAHandler
        self.sama_data = DatasetSAMAHandler()  # делаем изначально пустым
        if os.path.exists(self.settings.read_attributes_input()):  # смотрим есть ли в реестре использованный файл
            self.load_project(self.settings.read_attributes_input())  # пробуем его загрузить

        # данные из DatasetSAMAHandler будут отображаться в таблице

        self.headers = ("Label name", "Number of\nlabels", "Frequency of\nappearance\non the image",
                        "Percentage\nof total\nlabels", "Balance", "Color", "Action")
        # (имя класса, количество объектов, частота встречаемости на изображении, проценты от общего, сбалансированность
        # класса, палитра, действия)

        self.table_widget = AzTableAttributes(headers=self.headers, special_cols={6: "color", 7: "action"})
        header = self.table_widget.horizontalHeader()  # настраиваем отображение столбцов
        for column in range(self.table_widget.columnCount()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # первый столбец доминантный

        # итоговая настройка ui
        vlayout = QtWidgets.QVBoxLayout(self)  # главный Layout, наследуемый класс
        vlayout.addLayout(hlay_finish)  # добавляем ему расположение с кнопками и QLabel
        vlayout.addWidget(self.table_widget)
        wid.setLayout(vlayout)

        # Signals
        self.table_widget.signal_message.connect(self.forward_signal)

    def forward_signal(self, message):
        self.signal_message.emit(message)  # перенаправление сигналов

    def attr_actions_disable(self, message):
        self.current_file = None
        self.signal_message.emit(message)
        self.toggle_tool_buttons(False)

    def toggle_tool_buttons(self, b):
        buttons = self.findChildren(QtWidgets.QToolButton)
        for button in buttons:
            button.setEnabled(b)
        self.file_json.button.setEnabled(True)

    def attr_load_projects_data(self):
        if len(self.file_json.text()) < 5:  # недостойно внимания
            return
        self.load_project(self.file_json.text())

    def load_project(self, filename):
        self.sama_data.load(filename)
        print("flag: " + str(self.sama_data.is_correct_file))
        if not self.sama_data.is_correct_file:
            self.attr_actions_disable(
                self.tr("Выбранный файл не является корректным либо не содержит необходимых данных"))
            self.file_json.clear()
            return
        # Все загружено и всё корректно, поэтому записываем его в реестр
        self.file_json.setText(filename)
        self.current_file = filename
        self.settings.write_attributes_input(filename)
        self.toggle_tool_buttons(True)
        self.signal_message.emit(self.tr(f"Loaded project file: {filename}"))
        print(filename)
        print(self.sama_data.get_labels())

    def attrs_copy_project(self):  # копирование проекта
        file = az_file_dialog(self, self.tr("Make copy project file and load it"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="json (*.json)",
                              initial_filter="json (*.json)")
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

    def attrs_export(self):  # экспорт проекта
        file = az_file_dialog(self, self.tr("Export table data to text file"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="txt (*.txt)",
                              initial_filter="txt (*.txt)")
        if len(file) > 0:  # сохраняем в файл, при этом пропускаем определенные столбцы
            if save_via_qtextstream(self.table_widget, file):
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
    Таблица для взаимодействия с QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, headers=("Column 1", "Column 2", "Actions"), special_cols={2: "colors"}, data=None, parent=None):

        super(AzTableAttributes, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)  # заголовки
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # отключаем редактирование

        # настраиваем особые столбцы
        self.special_cols = {2: "colors"}

        self.setRowCount(5)
        items = [["Item 1", "A", "20"],
                 ["Item 2", "C", "15"],
                 ["Item 3", "B", "18"],
                 ["Item 4", "D", "10"],
                 ["Item 5", "E", "5"]]

        for row, item in enumerate(items):
            for col, text in enumerate(item):
                new_item = QtWidgets.QTableWidgetItem(text)
                self.setItem(row, col, new_item)

            button = QtWidgets.QPushButton("...")
            button.clicked.connect(lambda ch, row=row: self.show_context_menu(row))
            self.setCellWidget(row, 6, button)

            button2 = QtWidgets.QToolButton()
            button2.setAutoRaise(True)
            button2.setStyleSheet("QToolButton { background-color: rgb(255, 0, 0); }")
            button2.clicked.connect(lambda ch, btn=button2: self.change_color(btn))
            self.setCellWidget(row, 5, button2)

    def change_color(self, button):
        color = QtWidgets.QColorDialog.getColor(button.palette().color(button.backgroundRole()))
        if color.isValid():
            button.setStyleSheet(
                f"QToolButton {{ background-color: rgb({color.red()}, {color.green()}, {color.blue()}); }}")

    def show_context_menu(self, row):
        menu = QtWidgets.QMenu()

        rename_act = new_act(self, self.tr("Rename"), "glyph_signature", the_color, self.label_rename,
                                tip=self.tr("Rename current label"))
        rename_act.triggered.connect(lambda ch, row=row: self.label_rename(row))

        delete_act = new_act(self, self.tr("Delete"), "glyph_delete2", the_color, self.label_delete,
                                tip=self.tr("Delete current label"))
        delete_act.triggered.connect(lambda ch, row=row: self.label_delete(row))

        merge_act = new_act(self, self.tr("Merge"), "glyph_merge", the_color, self.label_merge,
                                tip=self.tr("Merge current label to other label"))
        merge_act.triggered.connect(lambda ch, row=row: self.label_delete(row))

        menu.addAction(rename_act)
        menu.addAction(merge_act)
        menu.addAction(delete_act)
        pos = QtGui.QCursor.pos()
        menu.exec_(pos)

    def create_table(self):
        self.table = QTableWidget(len(self.labels), 2)
        for i, label in enumerate(self.labels):
            item = CustomItem(label)
            self.table.setItem(i, 0, item)

            labels = [""]
            self.crete_combo(i, 1, labels, is_active=False)

        self.table.setColumnWidth(0, self.col_width)
        self.table.setColumnWidth(1, self.col_width)
        self.table.setHorizontalHeaderLabels(list(self.headers))
        self.table.cellClicked.connect(self.cell_changed)

    def label_rename(self, row):
        """ Перечень действий переименовать класс"""
        text, ok = QtWidgets.QInputDialog.getText(self, self.tr("Rename Label"), self.tr("Enter new name:"))
        # TODO: rename
        if ok and text:
            self.item(row, 0).setText(text)
        self.signal_message.emit(self.tr(f"Объекты с меткой {row} переименованы в класс {row}"))

    def label_delete(self, row):
        """ Перечень действий: удалить метку"""
        # TODO: remove
        self.signal_message.emit(self.tr(f"Объекты с меткой {row} удалены"))

    def label_merge(self, row):
        """ Перечень действий: слить с другой меткой"""
        # TODO: merge
        self.signal_message.emit(self.tr(f"Объединение объектов меток {row} и {row}"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzTableAttributes", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes - AzTableAttributes
        self.setToolTip(self.tr("Data by classes (labels) of the dataset"))
        # Заголовки таблицы
        # TODO: headers


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TabAttributesUI()
    window.show()
    sys.exit(app.exec_())
