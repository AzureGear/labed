from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy.QtWidgets import QDockWidget, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QToolBox, QTabWidget, \
    QLabel
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
        self.ui_merge_label = QLabel("Объединение файлов разметки LabelMe в формат SAMA")
        self.ui_slicing_label = QLabel("Нарезка снимков заданного размера")
        self.ui_attributes_label = QLabel("Поиск и редактирование снимков по атрибутам разметки")
        self.ui_geometry_label = QLabel("Изменение геометрии разметки")
        icons_dir = os.path.join(current_folder, "../icons/")  # каталог к иконкам
        style = current_folder + "/tabwidget.qss"
        with open(style, "r") as fh:
            self.setStyleSheet(fh.read())
        captions_and_icons = {"Merge": "glyph_normalization",  # "Слияние"
                              "Slicing": "glyph_delete3",  # "Нарезка"
                              "Attributes": "glyph_search-file",  # "Атрибуты"
                              "Geometry": "glyph_donut-chart"}  # "Геометрия"

        self.ui_merge = QWidget()
        self.ui_merge.layout = QVBoxLayout(self.ui_merge)
        self.ui_merge.layout.addWidget(self.ui_merge_label)
        pal = self.ui_merge.palette()


        layout = QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу
        self.tab_widget = QTabWidget()  # виджет со вкладками-страницами обработки

        self.tab_widget.addTab(self.ui_merge, newIcon(captions_and_icons["Merge"]), captions_and_icons["Merge"])
        for caption in captions_and_icons:
            # print(caption, captions_and_icons[caption])
            self.tab_widget.addTab(QWidget(), newIcon(captions_and_icons[caption]), caption)
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))

        self.tab_widget.currentChanged.connect(self.changeTab)
        # colors = ('red', 'green', 'black', 'blue')
        # for i, color in enumerate(colors):
        #     self.tab_widget.addTab(QWidget(), 'Tab #{}'.format(i + 1))
        #     self.tab_widget.tabBar().setTabTextColor(i, QColor(color))
        layout.addWidget(self.tab_widget)

    def changeTab(self):
        print(str(self.tab_widget.currentIndex()))
        self.tab_widget.widget(self.tab_widget.currentIndex()).setStyleSheet('background: 255,255,255;')

    def page_Merge_setup(self):
        pass
