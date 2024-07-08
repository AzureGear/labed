from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, DEFAULT_DATASET_USAGE, helper
from ui import AzButtonLineEdit, coloring_icon
import os

the_colors = UI_COLORS.get("settings_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class SettingsUI(QtWidgets.QWidget):
    """
    Класс виджета настройки
    """
    signal_default_dir_change = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.line_general_datasets_dir = None
        self.line_default_output_dir = None
        self.datasets_dir = QtWidgets.QLabel('Default datasets directory:')
        self.output_dir = QtWidgets.QLabel('Default output dir:')
        self.chk_load_sub_dirs = QtWidgets.QCheckBox('Load subdirectories, when use "Load image dir"')
        self.tab_widget = QtWidgets.QTabWidget()  # создаём виджет со вкладками
        self.setup_ui()
        # Определяем доступные датасеты
        self.check_default_datasets()

    def setup_ui(self):
        # SettingsUI(QWidget) - наш главный родительский контейнер
        #  └- layout - основной виджет QVBoxLayout, к которому мы добавляем другие виджеты
        #      ├- tab_widget - виджет со вкладками (страницами)
        #      |   ├- page_common - страница виджета с Общими настройками
        #      |   |   └- page_common_layout - QFormLayout на котором уже располагаются сами виджеты с настройками
        #      |   └- ...еще страница с другими настройками
        #      └- ...еще какой-нибудь еще виджет

        # Layout and Widgets
        page_common = QtWidgets.QWidget(self.tab_widget)  # создаём страницу
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))
        page_common_layout = QtWidgets.QFormLayout()  # страница общих настроек имеет расположение QGrid
        page_common.setLayout(page_common_layout)
        self.tab_widget.addTab(page_common, coloring_icon("glyph_setups", the_colors),
                               "Common settings")  # добавляем страницу
        layout = QtWidgets.QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.addWidget(self.tab_widget)  # ему добавляем виджет
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу

        # QLineEdit для хранения "верхнего каталога" датасетов
        self.line_general_datasets_dir = AzButtonLineEdit("glyph_folder", the_colors,
                                                          caption="Select general directory for datasets",
                                                          read_only=True, dir_only=True)
        self.line_general_datasets_dir.setText(self.settings.read_datasets_dir())  # устанавливаем сохраненное значение
        self.line_general_datasets_dir.textChanged.connect(
            lambda: self.settings.write_datasets_dir(self.line_general_datasets_dir.text()))  # смена датасета
        self.line_general_datasets_dir.textChanged.connect(self.check_default_datasets)
        page_common_layout.addRow(self.datasets_dir, self.line_general_datasets_dir)  # добавляем виджет

        # QLineEdit для хранения выходных результатов
        self.line_default_output_dir = AzButtonLineEdit("glyph_folder", the_colors,
                                                        caption="Select default output directory",
                                                        read_only=True, dir_only=True)
        self.line_default_output_dir.setText(self.settings.read_default_output_dir())
        self.line_default_output_dir.textChanged.connect(
            lambda: self.settings.write_default_output_dir(self.line_default_output_dir.text()))
        self.line_default_output_dir.textChanged.connect(lambda: self.signal_default_dir_change.emit(True))

        page_common_layout.addRow(self.output_dir, self.line_default_output_dir)

        # QCheckBox загружать ли подкаталоги при загрузке директории в Просмотре датасета
        self.chk_load_sub_dirs.setChecked(bool(self.settings.read_load_sub_dir()))
        self.chk_load_sub_dirs.stateChanged.connect(
            lambda: self.settings.write_load_sub_dir(int(self.chk_load_sub_dirs.isChecked())))
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.chk_load_sub_dirs)
        page_common_layout.addRow(hlayout)

    def check_default_datasets(self):  # проверка и запись данных о доступных датасетах
        init_dir = self.settings.read_datasets_dir()
        if not helper.check_file(init_dir):
            return
        if not DEFAULT_DATASET_USAGE.get("MNIST", {}).get("check", None):
            return
        mnist = os.path.join(init_dir, DEFAULT_DATASET_USAGE.get("MNIST", {}).get("path", None))
        if helper.check_file(mnist):
            self.settings.write_dataset_mnist(mnist)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("SettingsUI", text)

    def translate_ui(self):
        self.output_dir.setText(self.tr('Default output dir:'))
        self.datasets_dir.setText(self.tr('Default datasets directory:'))
        self.tab_widget.setTabText(0, self.tr('Common settings'))
        self.chk_load_sub_dirs.setText(self.tr('Load subdirectories, when use "Load image dir"'))
