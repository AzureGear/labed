from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, config
from ui import new_act, new_button, coloring_icon, az_file_dialog, natural_order, AzButtonLineEdit, AzSpinBox, PageMNIST
import os

the_color = UI_COLORS.get("experiments_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class ExperimentUI(QtWidgets.QWidget):
    """
    Класс Экспериментов
    """

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.tab_widget = QtWidgets.QTabWidget()  # создаём виджет со вкладками
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        layout.addWidget(self.tab_widget)
        self.tab_mnist = PageMNIST(self)
        self.tab_widget.setIconSize(QtCore.QSize(20, 20))
        self.tab_widget.addTab(self.tab_mnist, QtGui.QIcon(coloring_icon("glyph_mnist", the_color)),
                               self.tab_mnist.name)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("ExperimentUI", text)

    def translate_ui(self):
        self.tab_widget.setTabText(0, self.tr(self.tab_mnist.name))
