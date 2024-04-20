from qdarktheme.qtpy.QtCore import Qt, QSize
from qdarktheme.qtpy.QtWidgets import QTabWidget, QVBoxLayout, QLabel, QWidget, QFormLayout, QCheckBox, \
    QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from qdarktheme.qtpy.QtGui import QIcon
from utils import AppSettings
from ui import AzButtonLineEdit, coloring_icon
from random import randint
from utils import UI_COLORS
import os

the_colors = UI_COLORS.get("settings_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class SettingsUI(QWidget):
    """
    Класс виджета настройки
    """
    def __init__(self, parent):
        super().__init__()
        self.line_general_datasets_dir = None
        self.line_default_output_dir = None
        self.output_dir = QLabel('Default output dir:')
        self.datasets_dir = QLabel('Default datasets directory:')
        self.chk_load_sub_dirs = QCheckBox('Load subdirectories, when use "Load image dir"')
        self.tab_widget = QTabWidget()  # создаём виджет со вкладками
        self.settings = None
        self.setup_ui()

    def setup_ui(self):
        # SettingsUI(QWidget) - наш главный родительский контейнер
        #  └- layout - основной виджет QVBoxLayout, к которому мы добавляем другие виджеты
        #      ├- tab_widget - виджет со вкладками (страницами)
        #      |   ├- page_common - страница виджета с Общими настройками
        #      |   |   └- page_common_layout - QFormLayout на котором уже располагаются сами виджеты с настройками
        #      |   └- ...еще страница с другими настройками
        #      └- ...еще какой-нибудь еще виджет

        self.settings = AppSettings()  # настройки программы
        icons_dir = os.path.join(current_folder, "../icons/")  # каталог к иконкам

        # Layout and Widgets
        page_common = QWidget(self.tab_widget)  # создаём страницу
        self.tab_widget.setIconSize(QSize(24, 24))
        page_common_layout = QFormLayout()  # страница общих настроек имеет расположение QGrid
        page_common.setLayout(page_common_layout)
        self.tab_widget.addTab(page_common, QIcon(coloring_icon("glyph_setups", the_colors)),
                               "Common settings")  # добавляем страницу
        layout = QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.addWidget(self.tab_widget)  # ему добавляем виджет
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу

        # QLineEdit для хранения "верхнего каталога" датасетов
        self.line_general_datasets_dir = AzButtonLineEdit("glyph_folder", the_colors,
                                                          caption="Select general directory for datasets",
                                                          editable=True, dir_only=True)
        self.line_general_datasets_dir.setText(self.settings.read_datasets_dir())  # устанавливаем сохраненное значение
        self.line_general_datasets_dir.textChanged.connect(
            lambda: self.settings.write_datasets_dir(self.line_general_datasets_dir.text()))  # автосохранение
        page_common_layout.addRow(self.output_dir, self.line_general_datasets_dir)  # добавляем виджет

        # QLineEdit для хранения выходных результатов
        self.line_default_output_dir = AzButtonLineEdit("glyph_folder", the_colors,
                                                        caption="Select default output directory",
                                                        editable=True, dir_only=True)
        self.line_default_output_dir.setText(self.settings.read_default_output_dir())
        self.line_default_output_dir.textChanged.connect(
            lambda: self.settings.write_default_output_dir(self.line_default_output_dir.text()))
        page_common_layout.addRow(self.datasets_dir, self.line_default_output_dir)

        # QCheckBox загружать ли подкаталоги при загрузке директории в Просмотре датасета
        self.chk_load_sub_dirs.setChecked(bool(self.settings.read_load_sub_dir()))
        self.chk_load_sub_dirs.stateChanged.connect(
            lambda: self.settings.write_load_sub_dir(int(self.chk_load_sub_dirs.isChecked())))
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.chk_load_sub_dirs)
        page_common_layout.addRow(hlayout)

