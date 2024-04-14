from qdarktheme.qtpy.QtCore import Qt
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication
from utils.settings_handler import AppSettings
from ui import base_custom_widgets
from random import randint


class SettingsUI:
    """
    Класс настройки
    """

    def __init__(self):
        self.tab_widget = None
        self.settings = None

    def setup_ui(self, win: QWidget):
        # win - наш главный родительский контейнер
        #  └ layout - основной виджет QVBoxLayout, к которому мы добавляем другие виджеты
        #     ├- tab_widget - виджет со вкладками
        #     └-

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

        layout = QVBoxLayout(win)  # вертикальный класс с расположением элементов интерфейса, родитель - win
        layout.addWidget(self.tab_widget)  # ему добавляем виджет
        layout.addWidget(QPushButton("HelloWorld"))
        # layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        # self.tab_widget.setStyleSheet('font-size: 12px; font-weight: bold;')  # применяем стиль
        page_common_layout.addRow(
            'Default datasets directory:',
            base_custom_widgets.ButtonLineEdit(icon_file="F:/data_prj/labed/labed/icons/glyph_folder.png"))
        page_common_layout.addRow(
            'Email Address:',
            base_custom_widgets.ButtonLineEdit(icon_file="F:/data_prj/labed/labed/icons/glyph_folder.png"))

        #QDir d = QFileInfo(filePath).absoluteDir();
        #QString absolute = d.absolutePath();

        # page_common.setStyleSheet()
        # contact pane
        # contact_page = QWidget(self)
        # layout = QFormLayout()
        # contact_page.setLayout(layout)
        # layout.addRow('Phone Number:', QLineEdit(self))
        # layout.addRow('Email Address:', QLineEdit(self))

        # g_layout = QGridLayout(frame)
        # g_layout.addWidget(QPushButton("Push button"), 0, 0)
        # g_layout.addWidget(push_btn_flat, 0, 1)
        # g_layout.addWidget(QSpinBox(), 1, 0)
        # g_layout.addWidget(tool_btn, 1, 1)
        # g_layout.addWidget(QRadioButton("Radio button"), 2, 0)
        # g_layout.addWidget(QCheckBox("Check box"), 2, 1)
        # g_layout.addWidget(calender, 3, 0, 1, 2)
