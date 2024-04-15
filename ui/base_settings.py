from qdarktheme.qtpy.QtCore import Qt
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication, QMessageBox
from utils.settings_handler import AppSettings
from ui.base_custom_widgets import ButtonLineEdit
from ui.base_custom_widgets import EditWithButton
from random import randint
import os

current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class SettingsUI(QWidget):
    """
    Класс настройки
    """
    def __init__(self, parent=None):
        super().__init__()
        self.line_default_output_dir = None
        self.output_dir = 'Default output dir:'
        self.line_general_datasets_dir = None
        self.datasets_dir = 'Default datasets directory:'

        self.button_line = None
        self.tab_widget = None
        self.settings = None
        self.setup_ui()

    def setup_ui(self):
        # win - наш главный родительский контейнер
        #  └- layout - основной виджет QVBoxLayout, к которому мы добавляем другие виджеты
        #      ├- tab_widget - виджет со вкладками (страницами)
        #      |   ├- page_common - страница виджета с Общими настройками
        #      |   |   └- page_common_layout - QFormLayout на котором уже располагаются виджеты с настройками
        #      |   └- ...еще страница с другими настройками
        #      └- ...еще какой-нибудь еще виджет

        self.settings = AppSettings()  # настройки программы
        self.tab_widget = QTabWidget()  # создаём виджет со вкладками
        page_common = QWidget(self.tab_widget)  # создаём страницу
        page_common_layout = QFormLayout()  # страница общих настроек имеет расположение QGrid
        page_common.setLayout(page_common_layout)
        self.tab_widget.addTab(page_common, "Common settings")  # добавляем страницу

        font = self.tab_widget.font()
        font.setBold(True)
        #
        # self.tab_bar.fonts[0] = font
        # self.tab_bar.update()

        layout = QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.addWidget(self.tab_widget)  # ему добавляем виджет
        layout.addWidget(QPushButton("HelloWorld"))
        # layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        # self.tab_widget.setStyleSheet('font-size: 12px; font-weight: bold;')  # применяем стиль
        icons_dir = os.path.join(current_folder, "../icons/")  # каталог к иконкам

        # QLineEdit для хранения "верхнего каталога" датасетов
        self.line_general_datasets_dir = ButtonLineEdit(icons_dir + "glyph_folder.png",
                                                        caption="Select general directory for datasets",
                                                        editable=True, dir_only=True)
        self.line_general_datasets_dir.setText(self.settings.read_datasets_dir())  # устанавливаем сохраненное значение
        self.line_general_datasets_dir.textChanged.connect(
            lambda: self.settings.write_datasets_dir(self.line_general_datasets_dir.text()))  # автосохранение
        page_common_layout.addRow(self.output_dir, self.line_general_datasets_dir)  # добавляем виджет

        # QLineEdit для хранения выходных результатов
        self.line_default_output_dir = ButtonLineEdit(icons_dir + "glyph_folder.png",
                                                      caption="Select default output directory",
                                                      editable=True, dir_only=True)
        self.line_default_output_dir.setText(self.settings.read_default_output_dir())
        self.line_default_output_dir.textChanged.connect(
            lambda: self.settings.write_default_output_dir(self.line_default_output_dir.text()))
        page_common_layout.addRow(self.datasets_dir, self.line_default_output_dir)
