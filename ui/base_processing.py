from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy import QtWidgets
from qdarktheme.qtpy import QtGui
from utils import AppSettings, UI_COLORS, UI_OUTPUT_TYPES
from ui import coloring_icon, AzButtonLineEdit, AzFileDialog
import os
import json

the_color = UI_COLORS.get("processing_color")
the_color_side = UI_COLORS.get("sidepanel_color")
current_folder = os.path.dirname(os.path.abspath(__file__))


class ProcessingUI(QtWidgets.QWidget):
    """
    Класс виджета обработки датасетов
    """

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        layout = QtWidgets.QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу
        self.tab_widget = QtWidgets.QTabWidget()  # виджет со вкладками-страницами обработки
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))
        self.tab_widget.currentChanged.connect(self.change_tab)
        layout.addWidget(self.tab_widget)

        # Создание и настройка перечня виджетов-вкладок
        self.tab_merge_setup()
        self.tab_slicing_setup()
        self.tab_attributes_setup()
        self.tab_geometry_setup()

        ui_summ = [  # перечень: QWidget, "имя вкладки", "имя иконки", "подсказка"
            [self.ui_tab_merge, "Merge", "glyph_merge", "Объединение файлов разметки в формат SAMA"],  # "Слияние"
            [self.ui_tab_slicing, "Slicing", "glyph_cutter", "Нарезка снимков заданного размера"],  # "Нарезка"
            [self.ui_tab_attributes, "Attributes", "glyph_search-file",
             "Поиск и редактирование снимков по атрибутам разметки"],  # "Атрибуты"
            [self.ui_tab_geometry, "Geometry", "glyph_transform", "Изменение геометрии разметки"]]  # "Геометрия"

        for i, elem in enumerate(ui_summ):
            self.tab_widget.addTab(elem[0], coloring_icon(elem[2], the_color_side), elem[1])  # виджет, иконка, название
            # print("added tab: " + self.tab_widget.tabText(i))
            self.tab_widget.setTabToolTip(i, elem[3])

    def change_tab(self):
        pass
        # print(str(self.tab_widget.currentIndex()))

    def tab_merge_setup(self):  # настройка страницы "Слияние"
        self.ui_tab_merge = self.tab_basic_setup(complex=True)  # создаём "сложный" виджет
        # Действия для страницы
        self.merge_actions = (
            QtGui.QAction(coloring_icon("glyph_add", the_color), "Add project files", triggered=self.merge_add_files),
            QtGui.QAction(coloring_icon("glyph_delete3", the_color), "Remove project files",
                          triggered=self.merge_remove_files),
            QtGui.QAction(coloring_icon("glyph_delete2", the_color), "Clear list", triggered=self.merge_clear),
            QtGui.QAction(coloring_icon("glyph_merge", the_color), "Merge selected files",
                          triggered=self.merge_combine),
            QtGui.QAction(coloring_icon("glyph_folder_more", the_color), "Open output dir",
                          triggered=self.merge_open_output))
        self.merge_output_label = QtWidgets.QLabel("Output type:")
        self.merge_output_list = QtWidgets.QComboBox()  # список выходных данных
        self.merge_output_list.addItems(UI_OUTPUT_TYPES)  # перечень вариантов для списка
        self.merge_files_list = QtWidgets.QListWidget()  # перечень добавляемых файлов
        self.merge_files_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.merge_label = QtWidgets.QLabel()  # предпросмоторщик файлов
        self.merge_preview_data = QtWidgets.QScrollArea()  # контейнер для предпросмоторщика файлов
        self.merge_preview_data.setWidget(self.merge_label)
        split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)  # создаём разделитель
        split.addWidget(self.merge_files_list)  # куда помещаем перечень файлов...
        split.addWidget(self.merge_preview_data)  # ...и просмоторщик этих файлов
        split.setChildrenCollapsible(False)  # отключаем полное сворачивание виджетов внутри разделителя

        self.merge_cust_path_box = QtWidgets.QGroupBox("Use different from default dir for output")
        self.merge_cust_path_box.setCheckable(True)
        self.merge_output_line = AzButtonLineEdit("glyph_folder", the_color, caption="Select output dir",
                                                  read_only=False, dir_only=False)
        self.merge_cust_path_box.toggled.connect(self.merge_cust_path_box_toggled)
        self.merge_cust_path_box.setChecked(False)
        self.merge_files_list.itemSelectionChanged.connect(self.merge_selection_files_change)

        layout_in = QtWidgets.QHBoxLayout()
        layout_in.addWidget(self.merge_output_line)
        self.merge_cust_path_box.setLayout(layout_in)

        widg = QtWidgets.QWidget()
        widg.setLayout(layout_in)

        # Настройка панели инструментов
        self.merge_toolbar = QtWidgets.QToolBar("Toolbar for merging project files")  # панель инструментов для слияния
        self.merge_toolbar.setIconSize(QtCore.QSize(30, 30))
        self.merge_toolbar.setFloatable(False)
        self.merge_toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        self.merge_toolbar.addAction(self.merge_actions[0])  # добавить
        self.merge_toolbar.addAction(self.merge_actions[1])  # удалить
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addAction(self.merge_actions[2])  # очистить
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addWidget(self.merge_output_label)
        self.merge_toolbar.addWidget(self.merge_output_list)  # выходной тип
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addAction(self.merge_actions[3])  # объединить проекты и конвертировать
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addWidget(widg)
        # self.merge_toolbar.addWidget(self.merge_output_line)
        self.merge_toolbar.addAction(self.merge_actions[4])  # открыть выходной каталог

        # line_layout = QtWidgets.QVBoxLayout()
        # line_layout.addWidget(self.merge_output_line)

        vlayout = QtWidgets.QVBoxLayout()  # контейнер QVBoxLayout()
        # vlayout.addWidget(self.merge_cust_path_box)
        vlayout.addWidget(split)  # добавляем область с разделением
        wid = QtWidgets.QWidget()  # создаём виджет-контейнер...
        wid.setLayout(vlayout)  # куда помещаем vlayout (поскольку Central Widget может быть только QWidget)
        self.ui_tab_merge.addToolBar(self.merge_toolbar)  # добавляем панель меню
        self.ui_tab_merge.setCentralWidget(wid)  # устанавливаем главный виджет старицы "Слияние"
        self.merge_toggle_instruments()

    def merge_cust_path_box_toggled(self):
        if not self.merge_cust_path_box.isChecked():
            self.merge_output_line.setText(self.settings.read_default_output_dir())

    def merge_selection_files_change(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            print("hello!")
            # filenames = self.search_for_images(path)  # получаем перечень всех доступных изображений
            # self.current_data_list = filenames  # сохраняем его в памяти
            # self.fill_files_list(filenames)
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        pass

    def tab_slicing_setup(self):  # настройка страницы "Нарезка"
        self.ui_tab_slicing = self.tab_basic_setup()

    def tab_attributes_setup(self):  # настройка страницы "Атрибуты"
        self.ui_tab_attributes = self.tab_basic_setup()

    def tab_geometry_setup(self):  # настройка страницы "Геометрия"
        self.ui_tab_geometry = self.tab_basic_setup()

    def merge_toggle_instruments(self):  # включает/отключает инструменты
        enable = False
        self.merge_actions[3].setEnabled(enable)  # по умолчанию объединение выключим
        if self.merge_files_list.count() > 0:
            enable = True
        self.merge_actions[1].setEnabled(enable)
        self.merge_actions[2].setEnabled(enable)
        if len(self.merge_files_list.selectedItems()) > 0:  # файлы выбраны, можно попробовать объединить
            self.merge_actions[3].setEnabled(True)

    def tab_basic_setup(self, complex=False):  # базовая настройка каждой страницы QTabWidget
        if complex:
            widget = QtWidgets.QMainWindow()
        else:
            widget = QtWidgets.QWidget()
            widget.layout = QtWidgets.QVBoxLayout(widget)  # не забываем указать ссылку на объект
        return widget

    def merge_add_files(self):
        sel_files = AzFileDialog(self, "Select project files to add", self.settings.read_last_dir(), False,
                                 filter="LabelMe projects (*.json)", initial_filter="json (*.json)")
        print(sel_files)
        if sel_files:
            self.merge_fill_files(sel_files)
            self.merge_toggle_instruments()

    def merge_fill_files(self, filenames):
        for filename in filenames:
            item = QtWidgets.QListWidgetItem(filename)
            self.merge_files_list.addItem(item)

    def merge_remove_files(self):
        if self.merge_files_list.count() <= 0:
            return
        sel_items = self.merge_files_list.selectedItems()
        if len(sel_items) <= 0:
            return
        for item in sel_items:
            self.merge_files_list.removeItemWidget(item)
        self.merge_toggle_instruments

    def merge_clear(self):
        self.merge_files_list.clear()
        self.merge_toggle_instruments

    def merge_combine(self):
        self.merge_files_list.clearSelection()
        # TODO: сигнал об успехе

    def merge_open_output(self):
        pass
