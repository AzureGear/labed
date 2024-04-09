# from PyQt5.QtWidgets import QApplication, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from qdarktheme.qtpy.QtCore import QDir, Qt, Slot, QTranslator
from qdarktheme.qtpy.QtGui import QAction, QActionGroup
from qdarktheme.qtpy.QtWidgets import QApplication, QToolBar, QToolButton, QWidget, QMainWindow, QStackedWidget, \
    QStatusBar, QMenuBar, QSizePolicy, QMessageBox, QLabel
from utils import config
from PyQt5 import QtWidgets
from utils.settings_handler import AppSettings
import qdarktheme
import sys
from ui import newIcon
from ui import DockUI
from qdarktheme.widget_gallery._ui.frame_ui import FrameUI
from qdarktheme.widget_gallery._ui.icons_ui import IconsUi
from qdarktheme.widget_gallery._ui.mdi_ui import MdiUI
from qdarktheme.widget_gallery._ui.widgets_ui import WidgetsUI


class _BaseGUI:
    """
    Настройка интерфейса
    """
    def setup_ui(self, main_widget: QMainWindow):
        # Actions для боковой панели
        self.actions_page = (
            QAction(newIcon("glyph_pickaxe"), 'Move to widgets'),
            QAction(newIcon("glyph_flask"), "Move to dock"),
            QAction(newIcon("glyph_eye"), "Move to frame"),
            QAction(newIcon("glyph_highlight"), "Move to mdi"),
            QAction(newIcon("glyph_gear"), "Settings")
        )
        self.action_switch_theme = QAction(newIcon("glyph_black-and-white"), "Switch theme")
        self.action_switch_theme.setCheckable(True)

        # Actions для меню
        self.action_enable = QAction(newIcon("glyph_upload"), "Enable")
        self.action_disable = QAction(newIcon("glyph_check"), "Disable")
        self.actions_theme = [QAction(theme, main_widget) for theme in ["dark", "light"]]
        self.action_open_folder = QAction(newIcon("glyph_check"), "Open folder dialog")
        self.action_open_color_dialog = QAction(newIcon("glyph_check"), "Open color dialog")
        self.action_open_font_dialog = QAction(newIcon("glyph_check"), "Open font dialog")
        self.action_help = (QAction("Help"))
        self.actions_message_box = (
            QAction(text="Open question dialog"),
            QAction(text="Open information dialog"),
            QAction(text="Open warning dialog"),
            QAction(text="Open critical dialog"),
        )

        # Создаем кнопки
        tool_btn_lang, tool_btn_theme, tool_btn_enable, tool_btn_disable, tool_btn_message_box = (
            QToolButton() for _ in range(5)  # создаем кнопки
        )

        # Выбор языка
        self.actions_switch_lang = (QAction(text="Russian"), QAction(text="English"))
        tool_btn_lang.setIcon(newIcon('glyph_language'))
        tool_btn_lang.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        tool_btn_lang.addActions(self.actions_switch_lang)

        # Группировка виджетов
        self.central_window = QMainWindow()  # главный виджет
        self.stack_widget = QStackedWidget()  # виджет с переменой окон
        self.toolbar = QToolBar("Панель инструментов")  # панель инструментов, кочующая между режимами
        sidepanel = QToolBar("Панель режимов")  # левая панель режимов, всегда активная
        statusbar = QStatusBar()  # статусная строка
        menubar = QMenuBar()  # панель меню

        # Добавляем в кочующее меню действия
        self.toolbar.addActions(
            (self.action_open_folder, self.action_open_color_dialog, self.action_open_font_dialog)
        )

        action_group_toolbar = QActionGroup(main_widget)  # группа действий для панели режимов
        for action in self.actions_page:
            action.setCheckable(True)
            action_group_toolbar.addAction(action)
        self.actions_page[0].setChecked(True)  # по умолчанию установлено первое действие и оно должно быть активно

        spacer = QToolButton()  # пустая растяжка между иконками
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        spacer.setEnabled(False)
        # настройки панели режимов
        sidepanel.setMovable(False)
        sidepanel.addActions(self.actions_page)
        sidepanel.addWidget(spacer)
        sidepanel.addAction(self.action_switch_theme)  # кнопка изменения режима
        sidepanel.addWidget(tool_btn_lang)

        # Menu
        menu_view = menubar.addMenu("&View")
        menu_view.addActions(self.actions_page)
        menu_toggle = menubar.addMenu("&Toggle")
        menu_toggle.addActions((self.action_enable, self.action_disable))
        menu_dialog = menubar.addMenu("&Dialog")
        menu_dialog.addActions(
            (self.action_open_folder, self.action_open_color_dialog, self.action_open_font_dialog)
        )
        menu_message_box = menu_dialog.addMenu("&Messages")
        menu_message_box.addActions(self.actions_message_box)
        menu_help = menubar.addMenu("&Help")
        menu_help.addAction(self.action_help)
        tool_btn_message_box.setMenu(menu_message_box)
        self.action_enable.setEnabled(False)  # TODO: ?

        # Layout
        for ui in (WidgetsUI, DockUI, FrameUI, MdiUI, IconsUi):
            container = QWidget()
            ui().setup_ui(container)
            self.stack_widget.addWidget(container)

        self.central_window.setCentralWidget(self.stack_widget)
        # self.central_window.addToolBar(self.toolbar)  # TODO: нужна ли мне эта панель?

        main_widget.setCentralWidget(self.central_window)
        main_widget.addToolBar(Qt.ToolBarArea.LeftToolBarArea, sidepanel)
        main_widget.setMenuBar(menubar)
        main_widget.setStatusBar(statusbar)

        statusbar.showMessage('Ready!')


class BaseGUI(QMainWindow):
    """
    Базовый класс для взаимодействия с пользователем
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()   # настройки программы
        self.setWindowIcon(newIcon('digitalization'))
        self.width = 900
        self.height = int(0.628 * self.width)
        self.setMinimumWidth(300)
        self.setMinimumHeight(250)
        self.resize(self.width, self.height)
        # self.resizeEvent().connect(self.saveWindowPosition)

        self._ui = _BaseGUI()  # формируем приватные атрибуты и передаём язык
        self._ui.setup_ui(self)

        # Настройки по умолчанию
        # тема ui
        self._theme = self.settings.read_ui_theme()  # по умолчанию будет тема светлая
        if self._theme == "light": self._ui.action_switch_theme.setChecked(True)  # кнопка зажата
        # последняя панель
        # self._ui. = self.settings.read_ui_stack_widget_cur_tab()

        # Signals
        self._ui.action_help.triggered.connect(self.test_slot)
        self._ui.action_enable.triggered.connect(self.toggle_state)
        self._ui.action_enable.triggered.connect(self.toggle_state)
        self._ui.action_switch_theme.triggered.connect(self.change_theme)
        for action in self._ui.actions_switch_lang:
            action.triggered.connect(self.change_lang)  # соединяем смену языка
        for action in self._ui.actions_page:
            action.triggered.connect(self.change_page)  # соединяем смену виджета со сменными окнами
        qdarktheme.setup_theme(self._theme, 'sharp')  # стиль границ острый, можно и сглаженный: "rounded"

        # Локализация
        self.trans = QTranslator(self)  # переводчик
        self._retranslate_ui()  # выполняем переключение языка

    def _retranslate_ui(self):
        # Перечень всех виджетов и объектов для которых необходима локализация
        self._ui.action_help.setText(QtWidgets.QApplication.translate('BaseGUI', 'Help'))
        self._ui.action_switch_theme.setText(QtWidgets.QApplication.translate('BaseGUI', 'Switch'))
        for action in self._ui.actions_switch_lang:
            pass
            #action.setText(QtWidgets.QApplication.translate('BaseGUI', 'Hello, World'))

    def changeEvent(self, event):
        if event.type() == qdarktheme.qtpy.QtCore.QEvent.LanguageChange:
            self._retranslate_ui()
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
        if self.settings.read_lang() == action_name:
            return # если выбора, как такового не произошло
        else:
            self.trans.load("F:/data_prj/lab_ed/ui/l10n/" + action_name)  # загружаем перевод с таким же именем как и имя QAction
            QtWidgets.QApplication.instance().installTranslator(self.trans)
            #_app = QApplication.instance()  # получаем экземпляр приложения
            #_app.installTranslator(self.trans)
            self.settings.write_lang(action_name)   # записываем в настройки выбранный язык
            self.statusBar().showMessage(action_name)

    @Slot()
    def saveWindowPosition(self, size):
        pass

    @Slot()
    # Смена темы
    def change_theme(self):
        if self._ui.action_switch_theme.isChecked():
            self._theme = self._ui.actions_theme[1].text()  # зажатая кнопка темы
        else:
            self._theme = self._ui.actions_theme[0].text()  # неактивная кнопка темы
        qdarktheme.setup_theme(self._theme, "sharp")
        self.settings.write_ui_theme(self._theme)  # сохраняем настройки темы
        self.statusBar().showMessage(self._theme)  # извещаем пользователя

    @Slot()
    # Смена виджетов для панели режимов
    def change_page(self):
        action_name: str = self.sender().text()  # type: ignore
        if "widgets" in action_name:
            index = 0
        elif "dock" in action_name:
            index = 1
        elif "frame" in action_name:
            index = 2
        elif "mdi" in action_name:
            index = 3
        else:
            index = 4
        self._ui.stack_widget.setCurrentIndex(index)
        self.statusBar().showMessage(action_name)

    @Slot()
    def test_slot(self):  # TODO: temp slot, del at release
        self.statusBar().showMessage(self.settings.read_lang())

    @Slot()
    def toggle_state(self):  # TODO: delete?
        # принимаем от объекта пославшего сигнал
        state: str = self.sender().text()  # type: ignore
        self._ui.central_window.centralWidget().setEnabled(state == "Enable")
        self._ui.toolbar.setEnabled(state == "Enable")
        self._ui.action_enable.setEnabled(state == "Disable")
        self._ui.action_disable.setEnabled(state == "Enable")
        self.statusBar().showMessage(state)


if __name__ == '__main__':
    App = QApplication(sys.argv)  # создаем приложение
    window = BaseGUI()
    window.setWindowTitle("BaseGUI")
    window.show()
    sys.exit(App.exec_())
