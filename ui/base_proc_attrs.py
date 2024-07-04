from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, config
from utils.sama_project_handler import DatasetSAMAHandler
from ui import new_button, AzButtonLineEdit, coloring_icon, new_text, az_file_dialog, save_via_qtextstream
import shutil
import os

the_color = UI_COLORS.get("processing_color")


# todo: проверка при переименовании, что новое имя not in list[...]

class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    #     # загрузить проект+; экспорт+; сохранить палитру; применить палитру;

    # Инфо о датасете: количество снимков в датасете, количество меток, среднее ЛРМ.
    # Номер, имя класса, количество, частота встречаемости на изображении, проценты от общего, сбалансированность
    # класса, палитра
    # перечень действий: слить с классом, переименовать класс, удалить
    #
    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabAttributesUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Attributes"
        self.tool_tip_title = "Searching and editing dataset attributes"
        if color_active:
            self.icon_active = coloring_icon("glyph_attributes", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_attributes", color_inactive)

        # данные из проекта SAMA буду загружаться в DatasetSAMAHandler:
        self.sama_data = DatasetSAMAHandler("D:/data_sets/nuclear_power_stations/project.json")

        # данные из DatasetSAMAHandler будут отображаться в таблице:
        self.table_widget = AzTableAttributes()
        header = self.table_widget.horizontalHeader()  # настраиваем отображение столбцов
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        # Далее идет настройка ui
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
        self.dataset_info_lrm_desc = new_text(self, "Average LRM:", alignment="r")
        self.dataset_info_lrm_val = new_text(self, "0.62", bald=True)
        self.dataset_info_devi_lrm_desc = new_text(self, "Deviation LRM:", "peru", "r")
        self.dataset_info_devi_lrm_val = new_text(self, "0.22-0.89", "peru", bald=True)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
        hlay2 = QtWidgets.QHBoxLayout()
        # информация о датасете
        hlay2.addWidget(self.dataset_info_images_desc)
        hlay2.addWidget(self.dataset_info_images_val)
        hlay2.addWidget(self.dataset_info_labels_desc)
        hlay2.addWidget(self.dataset_info_labels_val)
        hlay2.addWidget(self.dataset_info_lrm_desc)
        hlay2.addWidget(self.dataset_info_lrm_val)
        hlay2.addWidget(self.dataset_info_devi_lrm_desc)
        hlay2.addWidget(self.dataset_info_devi_lrm_val)

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
        vlayout = QtWidgets.QVBoxLayout(self)  # главный Layout, наследуемый класс
        vlayout.addLayout(hlay_finish)  # добавляем ему расположение с кнопками и QLabel
        vlayout.addWidget(self.table_widget)
        wid.setLayout(vlayout)

    def attr_load_projects_data(self):
        if self.sama_data.correct_file:
            # TODO: сделать сохранение в реестр последнего успешного файла json
            pass
        print(self.sama_data.get_labels())
        print(self.sama_data.get_all_images_info())
        pass

    def attrs_copy_project(self):  # копирование проекта
        pass

    def attrs_save_palette(self):  # сохранение палитры
        pass

    def attrs_apply_palette(self):  # применение палитры
        pass

    def attrs_export(self):  # экспорт проекта
        file = az_file_dialog(self, self.tr("Export table data to text file"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="txt (*.txt)",
                              initial_filter="txt (*.txt)")
        if len(file) > 0:  # сохраняем в файл, при этом пропускаем определенные столбцы
            save_via_qtextstream(self.table_widget, file)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabAttributesUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes
        self.table_widget.translate_ui()
        self.label_project.setText(self.tr("Path to file project *.json:"))
        self.dataset_info_images_desc.setText(self.tr("Numbers of images: "))
        self.dataset_info_labels_desc.setText(self.tr("Numbers of labels: "))
        self.dataset_info_lrm_desc.setText(self.tr("Average LRM:"))
        self.dataset_info_devi_lrm_desc.setText(self.tr("Deviation LRM:"))


class AzTableAttributes(QtWidgets.QTableWidget):
    """
    Таблица для взаимодействия с QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, parent=None):
        super(AzTableAttributes, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setRowCount(5)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Test Column 1", "Test Column 2", "Test Column 3", "Actions"])
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # отключаем редактирование

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
            self.setCellWidget(row, 3, button)

        self.setSortingEnabled(True)  # Allow sorting in the table

    def show_context_menu(self, row):
        menu = QtWidgets.QMenu()

        rename_action = QtWidgets.QAction(QtGui.QIcon("icon_rename.png"), "Rename", menu)
        rename_action.triggered.connect(lambda ch, row=row: self.rename_item(row))
        menu.addAction(rename_action)

        delete_action = QtWidgets.QAction(QtGui.QIcon("icon_delete.png"), "Delete", menu)
        delete_action.triggered.connect(lambda ch, row=row: self.delete_item(row))
        menu.addAction(delete_action)

        pos = QtGui.QCursor.pos()
        menu.exec_(pos)

    def rename_item(self, row):
        text, ok = QtWidgets.QInputDialog.getText(self, "Rename Item", "Enter new name:")
        if ok and text:
            self.item(row, 0).setText(text)

    def delete_item(self, row):
        self.removeRow(row)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzTableAttributes", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes - AzTableAttributes
        self.setToolTip(self.tr("Data by classes (labels) of the dataset"))
        # Заголовки таблицы
        # TODO: headers


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TabAttributesUI()
    window.show()
    sys.exit(app.exec_())
