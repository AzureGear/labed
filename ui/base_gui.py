from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy import QtGui
from qdarktheme.qtpy import QtWidgets

from utils import config
from PyQt5 import QtWidgets
import qdarktheme
import sys
import os
from utils import APP_MIN_SIZE, UI_COLORS, AppSettings
from ui import SettingsUI, ViewDatasetUI, ExperimentUI, ProcessingUI, AutomationUI
from ui import new_icon, coloring_icon, AzAction

from qdarktheme.widget_gallery._ui.frame_ui import FrameUI
from qdarktheme.widget_gallery._ui.widgets_ui import WidgetsUI

the_color = UI_COLORS.get("sidepanel_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/

# стиль некоторых виджетов для темной темы
qss_dark = """
QTabWidget::tab-bar {
    left: 5px;
}

QTabBar {  
    font-weight: bold;  
}

QTabBar::tab:!selected { 
    font-weight: normal; 
    margin-bottom: -4px;
}

QTabBar::tab:selected {
    font: bold 12px;
}

QToolTip { 
    background-color: whitesmoke; 
    color: black; 
    border: lavender solid 1px;
}
"""

# стиль некоторых виджетов для светлой темы
qss_light = """
QTabWidget::tab-bar {
    left: 5px;
}

QTabBar {  
    font-weight: bold;  
}

QTabBar::tab:!selected { 
    font-weight: normal; 
    margin-bottom: -4px;
}

QTabBar::tab:selected {
    font: bold 12px;
}

QToolTip { 
    background-color: rgb(50,50,50); 
    color: whitesmoke; 
    border: black solid 1px;
}
"""


class _BaseGUI:
    def setup_ui(self, main_widget: QtWidgets.QMainWindow):
        # Actions для боковой панели
        self.actions_page_side_panel = (
            AzAction("Processing", "glyph_pickaxe", UI_COLORS.get("processing_color"), the_color),
            AzAction("Experiments", "glyph_flask", UI_COLORS.get("experiments_color"), the_color),
            AzAction("View datasets", "glyph_eye", UI_COLORS.get("datasets_color"), the_color),
            AzAction("Automation", "glyph_highlight", UI_COLORS.get("automation_color"), the_color),
            AzAction("Settings", "glyph_gear", UI_COLORS.get("settings_color"), the_color)
        )

        self.action_switch_theme = AzAction("Switch theme", "glyph_black-and-white", the_color, the_color)

        # Actions для меню
        self.action_exit = QtGui.QAction("Exit")
        self.actions_theme = [QtGui.QAction(theme, main_widget) for theme in ["dark", "light"]]
        self.action_help = (QtGui.QAction("Help"))

        # Создаем кнопки
        tool_btn_lang = QtWidgets.QToolButton()  # создаем кнопки

        # Выбор языка
        tool_btn_lang.setIcon(coloring_icon('glyph_language', the_color))  # кнопка выбора языка
        tool_btn_lang.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)  # со всплывающим меню
        self.actions_switch_lang = []  # перечень QActions для доступных переводов (сделаем динамическое меню)
        for file in os.listdir(os.path.join(current_folder, "../" + config.LOCALIZATION_FOLDER)):
            if file.endswith(".qm"):  # файлы локализаций *.qm
                only_file_name = os.path.splitext(file)[0]  # удаляем расширение
                self.actions_switch_lang.append(
                    QtGui.QAction(text=only_file_name))  # формируем набор QAction для локализаций
        tool_btn_lang.addActions(self.actions_switch_lang)  # передаем его кнопке

        # Группировка виджетов
        self.central_window = QtWidgets.QMainWindow()  # главный виджет
        self.stack_widget = QtWidgets.QStackedWidget()  # виджет с переменой окон
        sidepanel = QtWidgets.QToolBar("Панель режимов")  # левая панель режимов, всегда активная
        statusbar = QtWidgets.QStatusBar()  # статусная строка
        menubar = QtWidgets.QMenuBar()  # панель меню

        action_group_toolbar = QtGui.QActionGroup(main_widget)  # группа действий для панели режимов
        for action in self.actions_page_side_panel:
            action.setCheckable(True)
            action_group_toolbar.addAction(action)  # соединяем действия боковой панели в группу

        spacer = QtWidgets.QToolButton()  # пустая растяжка между иконками
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        spacer.setEnabled(False)
        # настройки панели режимов
        sidepanel.setMovable(False)
        sidepanel.addActions(self.actions_page_side_panel)
        sidepanel.addWidget(spacer)
        sidepanel.addAction(self.action_switch_theme)  # кнопка изменения режима
        sidepanel.addWidget(tool_btn_lang)
        sidepanel.toggleViewAction().setVisible(False)

        # Меню
        self.menu_file = QtWidgets.QMenu("&File")
        self.menu_file.addAction(self.action_exit)

        self.menu_view = QtWidgets.QMenu("&View")
        self.menu_view.addActions(self.actions_page_side_panel)

        self.menu_help = QtWidgets.QMenu("&Help")
        self.menu_help.addAction(self.action_help)

        menubar.addMenu(self.menu_file)
        menubar.addMenu(self.menu_view)
        menubar.addMenu(self.menu_help)

        # Layout
        self.ui_processing = ProcessingUI(self)  # виджет обработки
        self.ui_experiment = ExperimentUI(self)  # виджет экспериментов
        self.ui_viewdataset = ViewDatasetUI(self)  # виджет просмотра датасетов
        self.ui_automation = AutomationUI(self)  # виджет автоматизации
        self.ui_settings = SettingsUI(self)  # виджет настроек
        # создаём группу виджетов
        uis = [self.ui_processing, self.ui_experiment, self.ui_viewdataset, self.ui_automation, self.ui_settings]
        for ui in uis:
            self.stack_widget.addWidget(ui)  # все размещаем в Stack_widget
        self.central_window.setCentralWidget(self.stack_widget)  # центральный содержит QStackedWidget

        # настраиваем интерфейс
        main_widget.setCentralWidget(self.central_window)
        main_widget.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, sidepanel)
        main_widget.setMenuBar(menubar)
        main_widget.setStatusBar(statusbar)


class BaseGUI(QtWidgets.QMainWindow):
    """
    Базовый класс для взаимодействия с пользователем
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setWindowIcon(new_icon('digitalization'))
        self._ui = _BaseGUI()  # настройка интерфейса и создание приватных атрибуты
        self._ui.setup_ui(self)

        # Signals
        self._ui.action_exit.triggered.connect(self.slot_exit)  # выход из программы
        self._ui.action_help.triggered.connect(self.test_slot)
        self._ui.action_switch_theme.triggered.connect(self.change_theme)
        self._ui.ui_processing.signal_message.connect(self.show_statusbar_msg)  # вкладка Обработка
        self._ui.ui_viewdataset.signal_message.connect(self.show_statusbar_msg)  # вкладка Просмотр данных
        for action in self._ui.actions_switch_lang:  # соединяем смену языка
            action.triggered.connect(self.change_lang)
        for i, action in enumerate(self._ui.actions_page_side_panel):
            action.setData(i)
            action.triggered.connect(self.change_page)

        # Локализация
        self.trans = QtCore.QTranslator(self)  # переводчик
        self._retranslate_ui()  # переключение языка

        # Настройки по умолчанию и сохранённые настройки
        self._theme = self.settings.read_ui_theme()  # тема светлая

        # стиль границ острый, можно и сглаженный: "rounded"
        qdarktheme.setup_theme(self._theme, 'sharp',
                               additional_qss=qss_light if self._theme == "dark" else qss_dark)
        if self._theme == "light": self._ui.action_switch_theme.setChecked(True)  # кнопка зажата
        self._ui.stack_widget.setCurrentIndex(self.settings.read_ui_stack_widget_cur_tab())  # загрузка вкладки
        # активация сохранённой по нумеру вкладки
        self._ui.actions_page_side_panel[self.settings.read_ui_stack_widget_cur_tab()].setChecked(True)
        last_lang = self.settings.read_lang()  # загрузка сохранённого языка
        for action in self._ui.actions_switch_lang:
            if action.text() == last_lang: action.trigger()  # меняем язык на сохранённый
        self.setMinimumWidth(APP_MIN_SIZE.get("HEIGHT"))
        self.setMinimumHeight(APP_MIN_SIZE.get("HEIGHT") * APP_MIN_SIZE.get("WIDTH"))

        position, size, state = self.settings.read_ui_position()
        self.resize(size)
        self.move(position)
        self.setWindowState(QtCore.Qt.WindowState(state))

    def closeEvent(self, event):
        self.settings.write_ui_position(self.pos(), self.size(), self.windowState())

    def _retranslate_ui(self):
        # Перечень всех виджетов и объектов для которых будет выполняться локализация
        _tr = QtWidgets.QApplication.translate  # не работает при использовании сокращения перевод не выполняется
        self._ui.actions_page_side_panel[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'Processing'))
        self._ui.actions_page_side_panel[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Experiments'))
        self._ui.actions_page_side_panel[2].setText(QtWidgets.QApplication.translate('BaseGUI', 'View datasets'))
        self._ui.actions_page_side_panel[3].setText(QtWidgets.QApplication.translate('BaseGUI', 'Move to mdi'))
        self._ui.actions_page_side_panel[4].setText(QtWidgets.QApplication.translate('BaseGUI', 'Settings'))
        self._ui.action_switch_theme.setText(QtWidgets.QApplication.translate('BaseGUI', 'Switch theme'))
        self._ui.action_help.setText(QtWidgets.QApplication.translate('BaseGUI', 'Help'))
        self._ui.action_exit.setText(QtWidgets.QApplication.translate('BaseGUI', 'Exit'))

        # Панель Меню
        self._ui.menu_file.setTitle(QtWidgets.QApplication.translate('BaseGUI', "&File"))
        self._ui.menu_view.setTitle(QtWidgets.QApplication.translate('BaseGUI', "&View"))
        self._ui.menu_help.setTitle(QtWidgets.QApplication.translate('BaseGUI', "&Help"))

        # QStackWidgets
        # Processing
        pc = self._ui.ui_processing
        pc.tab_widget.setTabText(0, QtWidgets.QApplication.translate('BaseGUI', "Merge"))
        pc.tab_widget.setTabText(1, QtWidgets.QApplication.translate('BaseGUI', "Slicing"))
        pc.tab_widget.setTabText(2, QtWidgets.QApplication.translate('BaseGUI', "Attributes"))
        pc.tab_widget.setTabText(3, QtWidgets.QApplication.translate('BaseGUI', "Geometry"))
        # Processing - Merge
        pc.merge_actions[0].setText(QtWidgets.QApplication.translate('BaseGUI', "Add files"))
        pc.merge_actions[1].setText(QtWidgets.QApplication.translate('BaseGUI', "Remove files"))
        pc.merge_actions[2].setText(QtWidgets.QApplication.translate('BaseGUI', "Select all"))
        pc.merge_actions[3].setText(QtWidgets.QApplication.translate('BaseGUI', "Clear list"))
        pc.merge_actions[4].setText(QtWidgets.QApplication.translate('BaseGUI', "Merge selected files"))
        pc.merge_actions[5].setText(QtWidgets.QApplication.translate('BaseGUI', "Open output folder"))
        pc.merge_output_label.setText(QtWidgets.QApplication.translate('BaseGUI', "Output type:"))
        pc.merge_output_file_check.setText("Set user output file path other than default:")
        pc.merge_toolbar.setWindowTitle(
            QtWidgets.QApplication.translate('BaseGUI', "Toolbar for merging project files"))
        # Processing - Cutting Images (crop)
        pc.slice_input_file_label.setText("Path to file project *.json:")
        pc.slice_output_file_check.setText("Set user output file path other than default:")
        pc.slice_scan_size_label.setText("Scan size:")
        pc.slice_overlap_window_label.setText("Scanning window overlap percentage:")
        pc.slice_overlap_pols_default_label.setText("Default overlap percentage for classes:")

        # Baseview
        bv = self._ui.ui_viewdataset
        bv.tb_info_dataset.setText(QtWidgets.QApplication.translate('BaseGUI', ' Info'))
        bv.tb_load_preset.setText(QtWidgets.QApplication.translate('BaseGUI', 'Load preset dataset'))
        bv.actions_load[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'Load last data'))
        bv.actions_load[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Load dir'))
        bv.actions_load[2].setText(QtWidgets.QApplication.translate('BaseGUI', 'Load dataset'))
        bv.action_load_presets.setText(QtWidgets.QApplication.translate('BaseGUI', 'Load preset dataset'))
        bv.actions_show_data[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'One window'))
        bv.actions_show_data[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Add window'))
        bv.actions_show_data[2].setText(QtWidgets.QApplication.translate('BaseGUI', '4x windows'))
        bv.actions_show_data[3].setText(QtWidgets.QApplication.translate('BaseGUI', '16x windows'))
        bv.actions_adjust[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'Tiled'))
        bv.actions_adjust[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Cascade'))
        bv.actions_adjust[2].setText(QtWidgets.QApplication.translate('BaseGUI', 'Disable layout'))
        bv.actions_labels[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'Show labels'))
        bv.actions_labels[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Show filenames'))
        bv.actions_control_images[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'Preview'))
        bv.actions_control_images[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Next'))
        bv.action_shuffle_data.setText(QtWidgets.QApplication.translate('BaseGUI', 'Shuffle data'))
        bv.files_search.setPlaceholderText(QtWidgets.QApplication.translate('BaseGUI', 'Filter files'))
        bv.files_dock.setWindowTitle(QtWidgets.QApplication.translate('BaseGUI', 'Files List'))

        # Settings
        st = self._ui.ui_settings
        st.output_dir.setText(QtWidgets.QApplication.translate('BaseGUI', 'Default output dir:'))
        st.datasets_dir.setText(QtWidgets.QApplication.translate('BaseGUI', 'Default datasets directory:'))
        st.tab_widget.setTabText(0, QtWidgets.QApplication.translate('BaseGUI', 'Common settings'))
        st.chk_load_sub_dirs.setText(
            QtWidgets.QApplication.translate('BaseGUI', 'Load subdirectories, when use "Load image dir"'))

    def show_statusbar_msg(self, msg):
        self.statusBar().showMessage(msg)

    def changeEvent(self, event):
        # перегружаем функцию для возможности перевода "на лету"
        if event.type() == QtCore.QEvent.LanguageChange:
            self._retranslate_ui()  # что именно переводим
        super(BaseGUI, self).changeEvent(event)

    def setExampleGUI(self):
        # creating label
        self.label = QtWidgets.QLabel(self)

        # loading image
        self.pixmap = QtGui.QPixmap("../test.jpg")

        # adding image to label
        self.label.setPixmap(self.pixmap)

        # Optional, resize label to image size
        self.label.resize(self.pixmap.width(),
                          self.pixmap.height())

    @QtCore.Slot()
    # Смена языка
    def change_lang(self):
        action_name: str = self.sender().text()
        # if self.settings.read_lang() == action_name:
        #     return  # если выбора, как такового не произошло
        # else:
        if action_name:
            self.trans.load(os.path.join(current_folder, "../", config.LOCALIZATION_FOLDER, action_name))
            # загружаем перевод с таким же именем как и имя QAction
            QtWidgets.QApplication.instance().installTranslator(self.trans)
            self.settings.write_lang(action_name)  # записываем в настройки выбранный язык
            self.statusBar().showMessage(action_name)

    @QtCore.Slot()
    # Смена темы
    def change_theme(self):
        current_theme = ""
        if self._ui.action_switch_theme.isChecked():
            self._theme = self._ui.actions_theme[1].text()  # зажатая кнопка темы
            current_theme = "☀"
        else:
            self._theme = self._ui.actions_theme[0].text()  # неактивная кнопка темы
            current_theme = "☾"
        qdarktheme.setup_theme(self._theme, "sharp", additional_qss=qss_light if self._theme == "dark" else qss_dark)
        self.settings.write_ui_theme(self._theme)  # сохраняем настройки темы
        self.statusBar().showMessage(current_theme)  # извещаем пользователя

    @QtCore.Slot()
    # Смена виджетов для панели режимов
    def change_page(self, index=None):
        if not index:
            action = self.sender()
            if isinstance(action, QtWidgets.QAction):
                index = action.data()
                self._ui.stack_widget.setCurrentIndex(index)
                self.settings.write_ui_stack_widget_cur_tab(index)
                self.statusBar().showMessage(action.text())
            else:
                self._ui.stack_widget.setCurrentIndex(index)

    @QtCore.Slot()
    # Аккуратный выход
    def slot_exit(self):
        self.close()  # вызываем закрытие приложения

    @QtCore.Slot()
    # Тестовый слот
    def test_slot(self):
        self.statusBar().showMessage(str(self.settings.read_ui_stack_widget_cur_tab()))


if __name__ == '__main__':
    App = QtWidgets.QApplication(sys.argv)  # создаем приложение
    window = BaseGUI()
    window.setWindowTitle("BaseGUI")
    window.show()
    sys.exit(App.exec_())
