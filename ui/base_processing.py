from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, config
from ui import coloring_icon
import os

the_color = UI_COLORS.get("processing_color")
the_color_side = UI_COLORS.get("sidepanel_color")
current_folder = os.path.dirname(os.path.abspath(__file__))


# TODO: добавить флаг "Копировать изображения при объединении".
# TODO: соединить сигналы вывода сообщения

# ----------------------------------------------------------------------------------------------------------------------
class ProcessingUI(QtWidgets.QWidget):
    """
    Класс виджета QTabWidgget обработки данных, датасетов, проектов датасетов и т.п. Добавляет к себе страницы-вкладки
    различных способов обработки.
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал вывода сообщения

    def __init__(self, parent):
        super().__init__()
        self.crop_options = None
        self.settings = AppSettings()  # настройки программы
        self.merge_output_dir = ""
        layout = QtWidgets.QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        self.tab_widget = QtWidgets.QTabWidget()  # виджет со вкладками-страницами обработки
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))
        layout.addWidget(self.tab_widget)  # добавляем виджет со вкладками в расположение

        if config.UI_ENABLE.get("process", {}).get("merge", None):
            from ui import base_proc_merge
            self.add_tab("merge", base_proc_merge.TabMergeUI)
            self.tab_merge.signal_message.connect(self.retranslate_message)

        if config.UI_ENABLE.get("process", {}).get("slice", None):
            from ui import base_proc_slice
            self.add_tab("slice", base_proc_slice.TabSliceUI)
            self.tab_slice.signal_message.connect(self.retranslate_message)

        if config.UI_ENABLE.get("process", {}).get("attributes", None):
            from ui import base_proc_attrs
            self.add_tab("attributes", base_proc_attrs.TabAttributesUI)
            self.tab_attributes.signal_message.connect(self.retranslate_message)

        # Создание и настройка перечня виджетов-вкладок
        self.tab_geometry_setup()  # "Геометрия"

        ui_summ = [  # перечень: QWidget, "имя вкладки", "имя иконки", "подсказка"
            [self.ui_tab_geometry, "Geometry", "glyph_transform", "Изменение геометрии разметки"]]  # "Геометрия"

        for i, elem in enumerate(ui_summ):
            self.tab_widget.addTab(elem[0], coloring_icon(elem[2], the_color_side), elem[1])  # виджет, иконка, название
            # print("added tab: " + self.tab_widget.tabText(i))
            self.tab_widget.setTabToolTip(i, elem[3])

        # Загрузка последней активной вкладки "Обработки"
        self.tab_widget.setCurrentIndex(self.settings.read_ui_proc_page())

        # Signals
        self.tab_widget.currentChanged.connect(self.change_tab)  # изменение вкладки

    def retranslate_message(self, text):
        self.signal_message.emit(text)

    def add_tab(self, tab_name, tab_class):
        """Добавление вкладок с цветными иконками, где к"""
        tab = tab_class(self)
        self.tab_widget.addTab(tab, QtGui.QIcon(coloring_icon(f"glyph_{tab_name}", the_color_side)), tab.name)
        setattr(self, f"tab_{tab_name}", tab)

    @QtCore.pyqtSlot()
    def change_tab(self):  # сохранение последней активной вкладки "Обработки"
        self.settings.write_ui_proc_page(self.tab_widget.currentIndex())

    def tab_geometry_setup(self):  # настройка страницы "Геометрия"
        self.ui_tab_geometry = self.tab_basic_setup()

    def tab_basic_setup(self, complex=False):  # базовая настройка каждой страницы QTabWidget
        if complex:
            widget = QtWidgets.QMainWindow()
        else:
            widget = QtWidgets.QWidget()
            widget.layout = QtWidgets.QVBoxLayout(widget)  # не забываем указать ссылку на объект
        return widget

    def default_output_dir_change(self):
        # изменение в настройках выходного каталога
        if not self.tab_merge.merge_output_file_check.isChecked():
            self.merge_toggle_output_file()
        if not self.slice_output_file_check.isChecked():
            self.slice_toggle_output_file()

    def tr(self, text):
        return QtCore.QCoreApplication.translate("ProcessingUI", text)

    def translate_ui(self):
        # В самом виджете никакого перевода не требуется, он осуществляется в самих вкладках

        if config.UI_ENABLE.get("process", {}).get("merge", None):
            self.tab_merge.translate_ui()  # страница Объединения/конвертации

        if config.UI_ENABLE.get("process", {}).get("slice", None):
            self.tab_slice.translate_ui()  # страница Кадрирования

        if config.UI_ENABLE.get("process", {}).get("attributes", None):
            self.tab_attributes.translate_ui()  # страница Атрибутов


