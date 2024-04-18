from qdarktheme.qtpy.QtCore import Qt, QSize
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication, QMessageBox
from qdarktheme.qtpy.QtGui import QIcon
from utils import AppSettings
from utils import UI_COLORS
import os

current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/

class ExperimentUI(QWidget):
    """
    Класс Экспериментов
    """
    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # уменьшаем границу
        layout.addWidget(QPushButton("Experiment"))

    def stack_layouts(self):
        """
        Собираем все layouts
        """
        self.mainLayout = QVBoxLayout()
        self.tabs = QTabWidget()