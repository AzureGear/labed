from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, config
from ui import coloring_icon
import os

the_color = UI_COLORS.get("processing_color")
the_color_side = UI_COLORS.get("sidepanel_color")
current_folder = os.path.dirname(os.path.abspath(__file__))


# TODO: добавить флаг "Копировать изображения при объединении".

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

        # добавляем страницы-вкладки
        if config.UI_ENABLE.get("process", {}).get("merge", None):
            from ui import base_proc_merge
            self.add_tab("merge", base_proc_merge.TabMergeUI)

        if config.UI_ENABLE.get("process", {}).get("slice", None):
            from ui import base_proc_slice
            self.add_tab("slice", base_proc_slice.TabSliceUI)

        if config.UI_ENABLE.get("process", {}).get("attributes", None):
            from ui import base_proc_attrs
            self.add_tab("attributes", base_proc_attrs.TabAttributesUI)

        if config.UI_ENABLE.get("process", {}).get("geometry", None):
            from ui import base_proc_geom
            self.add_tab("geometry", base_proc_geom.TabGeometryUI)

        # self.tab_widget.tab_attribute =

        # Активация последней активной с прошлого запуска
        self.tab_widget.setCurrentIndex(self.settings.read_ui_proc_page())

        # Signals
        self.tab_widget.currentChanged.connect(self.change_tab)  # изменение вкладки
        self.change_tab()  # запускаем, чтобы изменить цвет активной вкладки

    def default_output_dir_change(self):
        # TODO:  изменение в настройках выходного каталога
        if not self.tab_merge.merge_output_file_check.isChecked():
            self.merge_toggle_output_file()
        if not self.slice_output_file_check.isChecked():
            self.slice_toggle_output_file()

    def forward_signal(self, message):
        self.signal_message.emit(message)  # перенаправление сигналов

    def add_tab(self, tab_name, tab_class):
        """Добавление вкладок с цветными иконками"""
        tab = tab_class(parent=self, color_active=the_color, color_inactive=the_color_side)
        self.tab_widget.addTab(tab, tab.icon_inactive, tab.name)  # добавляем страницу-вкладку
        setattr(self, f"tab_{tab_name}", tab)  # добавляем имя объекта класса
        tab.signal_message.connect(self.forward_signal)  # добавляем сигнал в строку состояния

    @QtCore.pyqtSlot()
    def change_tab(self):  # сохранение последней активной вкладки "Обработки"
        c_i = self.tab_widget.currentIndex()
        self.settings.write_ui_proc_page(c_i)

        # изменение цвета иконки активной вкладки
        for i in range(self.tab_widget.count()):
            if i == c_i:  # активная вкладка
                self.tab_widget.setTabIcon(i, self.tab_widget.widget(i).icon_active)
            else:
                self.tab_widget.setTabIcon(i, self.tab_widget.widget(i).icon_inactive)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("ProcessingUI", text)

    def translate_ui(self):
        # В самом ProcessingUI основной перевод осуществляется для вкладок, добавленных к нему.
        i = 0  # мы же не знаем сколько вкладок разрешено активировать
        for key in config.UI_ENABLE.get("process", {}):  # проходим по всем объектам в нашем файле настроек
            if config.UI_ENABLE["process"][key]:  # если есть флаг True, то...
                getattr(self, f"tab_{key}", None).translate_ui()  # ...запускаем перевод
                self.tab_widget.setTabText(i, self.tr(getattr(self, f"tab_{key}", None).name))  # перевод заголовков
                self.tab_widget.setTabToolTip(i, self.tr(getattr(self, f"tab_{key}", None).tool_tip_title))  # подсказок
                pass
            i += 1
