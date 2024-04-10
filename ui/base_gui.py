# from PyQt5.QtWidgets import QApplication, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from qdarktheme.qtpy.QtCore import QDir, Qt, Slot, QTranslator
from qdarktheme.qtpy.QtGui import QAction, QActionGroup
from qdarktheme.qtpy.QtWidgets import QApplication, QToolBar, QToolButton, QWidget, QMainWindow, QStackedWidget, \
    QStatusBar, QMenuBar, QSizePolicy, QMessageBox, QLabel, QMenu
from utils import config
from PyQt5 import QtWidgets
from utils.settings_handler import AppSettings
import qdarktheme
import sys
import os
from ui import newIcon
from ui import DockUI
from qdarktheme.widget_gallery._ui.frame_ui import FrameUI
from qdarktheme.widget_gallery._ui.icons_ui import IconsUi
from qdarktheme.widget_gallery._ui.mdi_ui import MdiUI
from qdarktheme.widget_gallery._ui.widgets_ui import WidgetsUI
from functools import partial

project_folder = os.path.dirname(os.path.abspath(__file__))  # начнём из каталога проекта

# TODO: добавить динамическое меню переводов в зависимости от количества файлов в TS
# TODO: добавить сохранение последней вкладки, добавить сохранение размера окна.


class _BaseGUI:
    """
    Настройка интерфейса
    """

    def setup_ui(self, main_widget: QMainWindow):

        # Actions для боковой панели
        self.create_actions()
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
        tool_btn_lang.setIcon(newIcon('glyph_language'))  # кнопка
        tool_btn_lang.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)  # со всплывающим меню
        self.actions_switch_lang = []
        # сделаем для него динамическое меню
        available_translation = []  # перечень доступных переводов
        for file in os.listdir(os.path.join(project_folder, "../" + config.LOCALIZATION_FOLDER)):
            if file.endswith(".qm"):  # файлы локализаций *.qm
                available_translation.append(file)  # формируем перечень локализаций
        print(available_translation)
        for file in available_translation:
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

        # Добавляем в кочующее меню действия
        self.toolbar.addActions(
            (self.action_open_folder, self.action_open_color_dialog, self.action_open_font_dialog)
        )

        action_group_toolbar = QActionGroup(main_widget)  # группа действий для панели режимов
        for action in self.actions_page:
            action.setCheckable(True)
            action_group_toolbar.addAction(action)

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
        self.menu_view = QMenu("&View")
        self.menu_view.addActions(self.actions_page)
        menubar.addMenu(self.menu_view)


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

        # self.fileMenu = QMenu("&Файл" if self.lang == 'RU' else "&File", self)
        # self.fileMenu.addAction(self.createNewProjectAct)
        # self.fileMenu.addAction(self.saveProjAsAct)
        # self.fileMenu.addSeparator()
        # self.menuBar().addMenu(self.fileMenu)
        # self.menuBar().addMenu(self.viewMenu)

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

    def create_actions(self):
        self.actions_page = (
            QAction(newIcon("glyph_pickaxe"), 'Processing'),
            QAction(newIcon("glyph_flask"), "Experiments"),
            QAction(newIcon("glyph_eye"), "View datasets"),
            QAction(newIcon("glyph_highlight"), "Move to mdi"),
            QAction(newIcon("glyph_gear"), "Settings")
        )


class BaseGUI(QMainWindow):
    """
    Базовый класс для взаимодействия с пользователем
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setWindowIcon(newIcon('digitalization'))
        self.width = 900
        self.height = int(0.628 * self.width)
        self.setMinimumWidth(300)
        self.setMinimumHeight(250)
        self.resize(self.width, self.height)
        # self.resizeEvent().connect(self.saveWindowPosition)

        self._ui = _BaseGUI()  # формируем приватные атрибуты
        self._ui.setup_ui(self)

        # Signals
        self._ui.action_help.triggered.connect(self.test_slot)
        self._ui.action_enable.triggered.connect(self.toggle_state)
        self._ui.action_enable.triggered.connect(self.toggle_state)
        self._ui.action_switch_theme.triggered.connect(self.change_theme)
        for action in self._ui.actions_switch_lang:  # соединяем смену языка
            action.triggered.connect(self.change_lang)
        for i, action in enumerate(self._ui.actions_page):
            action.setData(i)
            action.triggered.connect(self.change_page)

        # Локализация
        self.trans = QTranslator(self)  # переводчик
        self._retranslate_ui()  # переключение языка

        # Настройки по умолчанию и сохранённые настройки
        self._theme = self.settings.read_ui_theme()  # тема светлая
        qdarktheme.setup_theme(self._theme, 'sharp')  # стиль границ острый, можно и сглаженный: "rounded"
        if self._theme == "light": self._ui.action_switch_theme.setChecked(True)  # кнопка зажата
        self._ui.stack_widget.setCurrentIndex(self.settings.read_ui_stack_widget_cur_tab())   # загрузка вкладки
        self._ui.actions_page[self.settings.read_ui_stack_widget_cur_tab()].setChecked(True)  # активация вкладки
        last_lang = self.settings.read_lang()   # загрузка сохранённого языка
        for action in self._ui.actions_switch_lang:
            if action.text() == last_lang: action.trigger()  # меняем язык на сохранённый


    def preload_translations(self):
        self.menuRecentFiles.clear()
        recentFiles = []
        for fname in self.recentFiles:
            if fname not in self.filename and QtCore.QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.menuRecentFiles.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QtWidgets.QAction("&%d %s" % (i + 1, fname), self)
                action.setData(QtCore.QVariant(fname))
                action.triggered.connect(self.loadFile)
                self.menuRecentFiles.addAction(action)
        self.menuRecentFiles.addSeparator()
        self.menuRecentFiles.addAction(
            QtGui.QIcon(IMAGE_PATH + "button/clear.png"),
            QtWidgets.QApplication.translate("pychemqt", "Clear"),
            self.clearRecentFiles)


    def _retranslate_ui(self):
        # Перечень всех виджетов и объектов для которых будет выполняться локализация
        self._ui.action_help.setText(QtWidgets.QApplication.translate('BaseGUI', 'Help'))
        self._ui.actions_page[0].setText(QtWidgets.QApplication.translate('BaseGUI', 'Processing'))
        self._ui.actions_page[1].setText(QtWidgets.QApplication.translate('BaseGUI', 'Experiments'))
        self._ui.actions_page[2].setText(QtWidgets.QApplication.translate('BaseGUI', 'View datasets'))
        self._ui.actions_page[3].setText(QtWidgets.QApplication.translate('BaseGUI', 'Move to mdi'))
        self._ui.actions_page[4].setText(QtWidgets.QApplication.translate('BaseGUI', 'Settings'))
        self._ui.action_switch_theme.setText(QtWidgets.QApplication.translate('BaseGUI', 'Switch theme'))

        # Панель Меню
        self._ui.menu_view.setTitle(QtWidgets.QApplication.translate('BaseGUI', "View"))

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
        # if self.settings.read_lang() == action_name:
        #     return  # если выбора, как такового не произошло
        # else:
        if action_name:
            self.trans.load(os.path.join(project_folder, "../", config.LOCALIZATION_FOLDER, action_name))
            # загружаем перевод с таким же именем как и имя QAction
            QtWidgets.QApplication.instance().installTranslator(self.trans)
            self.settings.write_lang(action_name)  # записываем в настройки выбранный язык
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
    def test_slot(self):  # TODO: temp slot, del at release
        self.statusBar().showMessage(str(self.settings.read_ui_stack_widget_cur_tab()))

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
