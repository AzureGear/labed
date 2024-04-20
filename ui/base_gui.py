from qdarktheme.qtpy.QtCore import QDir, Qt, Slot, QTranslator
from qdarktheme.qtpy.QtGui import QAction, QActionGroup, QWindow, QColor, QPixmap, QIcon
from qdarktheme.qtpy.QtWidgets import QApplication, QToolBar, QToolButton, QWidget, QMainWindow, QStackedWidget, \
    QStatusBar, QMenuBar, QSizePolicy, QMessageBox, QLabel, QMenu
from utils import config
from PyQt5 import QtWidgets
import qdarktheme
import sys
import os
from ui import newIcon
from ui import DockUI, SettingsUI, ViewDatasetUI, ExperimentUI, ProcessingUI, AutomationUI
from qdarktheme.widget_gallery._ui.frame_ui import FrameUI
from utils import UI_COLORS, AppSettings
from ui import AzAction, coloring_icon

from qdarktheme.widget_gallery._ui.widgets_ui import WidgetsUI
the_color = UI_COLORS.get("sidepanel_color")

current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/

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
    def setup_ui(self, main_widget: QMainWindow):
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
        self.action_exit = QAction("Exit")
        self.actions_theme = [QAction(theme, main_widget) for theme in ["dark", "light"]]
        self.action_help = (QAction("Help"))

        # Создаем кнопки
        tool_btn_lang = QToolButton()  # создаем кнопки

        # Выбор языка
        tool_btn_lang.setIcon(coloring_icon('glyph_language', the_color))  # кнопка выбора языка
        tool_btn_lang.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)  # со всплывающим меню
        self.actions_switch_lang = []  # перечень QActions для доступных переводов (сделаем динамическое меню)
        for file in os.listdir(os.path.join(current_folder, "../" + config.LOCALIZATION_FOLDER)):
            if file.endswith(".qm"):  # файлы локализаций *.qm
                only_file_name = os.path.splitext(file)[0]  # удаляем расширение
                self.actions_switch_lang.append(QAction(text=only_file_name))  # формируем набор QAction для локализаций
        tool_btn_lang.addActions(self.actions_switch_lang)  # передаем его кнопке

        # Группировка виджетов
        self.central_window = QMainWindow()  # главный виджет
        self.stack_widget = QStackedWidget()  # виджет с переменой окон
        self.toolbar = QToolBar("Панель инструментов")  # панель инструментов, кочующая между режимами
        sidepanel = QToolBar("Панель режимов")  # левая панель режимов, всегда активная
        statusbar = QStatusBar()  # статусная строка
        menubar = QMenuBar()  # панель меню

        # Добавляем в кочующее меню действия *ОТКЛЮЧЕНО!
        self.toolbar.addActions((self.action_exit, self.action_help))

        action_group_toolbar = QActionGroup(main_widget)  # группа действий для панели режимов
        for action in self.actions_page_side_panel:
            action.setCheckable(True)
            action_group_toolbar.addAction(action)  # соединяем действия боковой панели в группу

        spacer = QToolButton()  # пустая растяжка между иконками
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        spacer.setEnabled(False)
        # настройки панели режимов
        sidepanel.setMovable(False)
        sidepanel.addActions(self.actions_page_side_panel)
        sidepanel.addWidget(spacer)
        sidepanel.addAction(self.action_switch_theme)  # кнопка изменения режима
        sidepanel.addWidget(tool_btn_lang)
        sidepanel.toggleViewAction().setVisible(False)

        # Меню
        self.menu_file = QMenu("&File")
        self.menu_file.addAction(self.action_exit)

        self.menu_view = QMenu("&View")
        self.menu_view.addActions(self.actions_page_side_panel)

        self.menu_help = QMenu("&Help")
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
        main_widget.addToolBar(Qt.ToolBarArea.LeftToolBarArea, sidepanel)
        main_widget.setMenuBar(menubar)
        main_widget.setStatusBar(statusbar)


class BaseGUI(QMainWindow):
    """
    Базовый класс для взаимодействия с пользователем
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setWindowIcon(newIcon('digitalization'))
        self._ui = _BaseGUI()  # настройка интерфейса и создание приватных атрибуты
        self._ui.setup_ui(self)

        # Signals
        self._ui.action_exit.triggered.connect(self.slot_exit)  # выход из программы
        self._ui.action_help.triggered.connect(self.test_slot)
        self._ui.action_switch_theme.triggered.connect(self.change_theme)
        for action in self._ui.actions_switch_lang:  # соединяем смену языка
            action.triggered.connect(self.change_lang)
        for i, action in enumerate(self._ui.actions_page_side_panel):
            action.setData(i)
            action.triggered.connect(self.change_page)

        # Локализация
        self.trans = QTranslator(self)  # переводчик
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
        self.setMinimumWidth(300)
        self.setMinimumHeight(250)

        position, size, state = self.settings.read_ui_position()
        self.resize(size)
        self.move(position)
        self.setWindowState(Qt.WindowState(state))

    def closeEvent(self, event):
        self.settings.write_ui_position(self.pos(), self.size(), self.windowState())

    def _retranslate_ui(self):
        # Перечень всех виджетов и объектов для которых будет выполняться локализация
        _tr = QApplication.translate
        self._ui.actions_page_side_panel[0].setText(_tr('BaseGUI', 'Processing'))
        self._ui.actions_page_side_panel[1].setText(_tr('BaseGUI', 'Experiments'))
        self._ui.actions_page_side_panel[2].setText(_tr('BaseGUI', 'View datasets'))
        self._ui.actions_page_side_panel[3].setText(_tr('BaseGUI', 'Move to mdi'))
        self._ui.actions_page_side_panel[4].setText(_tr('BaseGUI', 'Settings'))
        self._ui.action_switch_theme.setText(_tr('BaseGUI', 'Switch theme'))
        self._ui.action_help.setText(_tr('BaseGUI', 'Help'))
        self._ui.action_exit.setText(_tr('BaseGUI', 'Exit'))

        # Панель Меню
        self._ui.menu_file.setTitle(_tr('BaseGUI', "&File"))
        self._ui.menu_view.setTitle(_tr('BaseGUI', "&View"))
        self._ui.menu_help.setTitle(_tr('BaseGUI', "&Help"))

        # QStackWidgets
        # Processing
        self._ui.ui_processing.tab_widget.setTabText(0, _tr('BaseGUI', "Merge"))
        self._ui.ui_processing.tab_widget.setTabText(0, _tr('BaseGUI', "Slicing"))
        self._ui.ui_processing.tab_widget.setTabText(0, _tr('BaseGUI', "Attributes"))
        self._ui.ui_processing.tab_widget.setTabText(0, _tr('BaseGUI', "Geometry"))

        # Settings
        self._ui.ui_settings.output_dir.setText(_tr('BaseGUI', 'Default output dir:'))
        self._ui.ui_settings.datasets_dir.setText(_tr('BaseGUI', 'Default datasets directory:'))
        self._ui.ui_settings.tab_widget.setTabText(0, _tr('BaseGUI', 'Common settings'))

    def changeEvent(self, event):
        # перегружаем функцию для возможности перевода "на лету"
        if event.type() == qdarktheme.qtpy.QtCore.QEvent.LanguageChange:
            self._retranslate_ui()  # что именно переводим
        super(BaseGUI, self).changeEvent(event)

    def setExampleGUI(self):
        # creating label
        self.label = QLabel(self)

        # loading image
        self.pixmap = QPixmap("../test.jpg")

        # adding image to label
        self.label.setPixmap(self.pixmap)

        # Optional, resize label to image size
        self.label.resize(self.pixmap.width(),
                          self.pixmap.height())

    @Slot()
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

    @Slot()
    # Смена темы
    def change_theme(self):
        if self._ui.action_switch_theme.isChecked():
            self._theme = self._ui.actions_theme[1].text()  # зажатая кнопка темы
        else:
            self._theme = self._ui.actions_theme[0].text()  # неактивная кнопка темы
        qdarktheme.setup_theme(self._theme, "sharp", additional_qss=qss_light if self._theme == "dark"else qss_dark)
        self.settings.write_ui_theme(self._theme)  # сохраняем настройки темы
        self.statusBar().showMessage(self._theme)  # извещаем пользователя

    @Slot()
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

    @Slot()
    # Аккуратный выход
    def slot_exit(self):
        self.close()  # вызываем закрытие приложения

    @Slot()
    # Тестовый слот
    def test_slot(self):
        self.statusBar().showMessage(str(self.settings.read_ui_stack_widget_cur_tab()))


if __name__ == '__main__':
    App = QApplication(sys.argv)  # создаем приложение
    window = BaseGUI()
    window.setWindowTitle("BaseGUI")
    window.show()
    sys.exit(App.exec_())
