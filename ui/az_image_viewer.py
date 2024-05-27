from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy import QtWidgets
from qdarktheme.qtpy import QtGui
from utils import AppSettings, UI_COLORS
from ui import AzImageViewer, AzAction, coloring_icon, AzFileDialog
import os
import re
import random
# import natsort

the_color = UI_COLORS.get("processing_color")
the_color2 = UI_COLORS.get("processing_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class AzImageViewer(QtWidgets.QMainWindow):
    """
    Класс виджета просмотра датасетов
    """
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_and_labels()  # Настраиваем левую область: файлы, метки
        self.current_data_list = []
        self.current_data_dir = ""
        self.current_file = None
