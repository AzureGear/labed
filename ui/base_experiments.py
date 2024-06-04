from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import AppSettings
from utils import UI_COLORS
import os

current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/

class ExperimentUI(QtWidgets.QWidget):
    """
    Класс Экспериментов
    """
    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # уменьшаем границу
        layout.addWidget(QtWidgets.QPushButton("Experiment"))

    def stack_layouts(self):
        """
        Собираем все layouts
        """
        self.mainLayout = QtWidgets.QVBoxLayout()