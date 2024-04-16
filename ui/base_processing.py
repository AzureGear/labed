from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy.QtWidgets import QDockWidget, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QToolBox, QTabWidget, \
    QLabel, QSpacerItem, QSizePolicy
from qdarktheme.qtpy.QtGui import QColor
from utils.settings_handler import AppSettings
from ui import newIcon
import os

current_folder = os.path.dirname(os.path.abspath(__file__))


class ProcessingUI(QWidget):
    """
    Класс обработки датасетов
    """

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.ui_merge_label = QLabel()
        self.ui_slicing_label = QLabel()
        self.ui_attributes_label = QLabel()
        self.ui_geometry_label = QLabel()
        icons_dir = os.path.join(current_folder, "../icons/")  # каталог к иконкам
        style = current_folder + "/tabwidget.qss"
        with open(style, "r") as fh:
            self.setStyleSheet(fh.read())
        ui_summ = [["Merge", "glyph_merge", "Объединение файлов разметки LabelMe в формат SAMA"], # "Слияние"
                   ["Slicing", "glyph_cutter", "Нарезка снимков заданного размера"],  # "Нарезка"
                   ["Attributes", "glyph_search-file",
                    "Поиск и редактирование снимков по атрибутам разметки"],  # "Атрибуты"
                   ["Geometry", "glyph_transform", "Изменение геометрии разметки"]]  # "Геометрия"

        self.ui_merge = self.page_Merge_setup()
        self.ui_merge.layout = QVBoxLayout(self.ui_merge)
#        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
#        self.ui_merge.layout.addItem(self.vertical_spacer)

        layout = QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу
        self.tab_widget = QTabWidget()  # виджет со вкладками-страницами обработки
        self.tab_widget.addTab(self.ui_merge, newIcon(ui_summ[0][0]), ui_summ[0][1])

        for i, elem in enumerate(ui_summ):
            # print(elem[1])
            self.tab_widget.addTab(QWidget(), newIcon(elem[1]), elem[0])
            self.tab_widget.setTabToolTip(i, elem[2])
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))


        self.tab_widget.currentChanged.connect(self.changeTab)

        layout.addWidget(self.tab_widget)

    def changeTab(self):
        print(str(self.tab_widget.currentIndex()))
        # self.tab_widget.widget(self.tab_widget.currentIndex()).setStyleSheet('background: grey;')

    def page_Merge_setup(self):  # настройка страницы "Слияние"
        widget = QWidget()
        return widget
