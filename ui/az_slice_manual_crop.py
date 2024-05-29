from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import sys
from utils import AppSettings, UI_COLORS, UI_AZ_SLICE_MANUAL
from ui import AzImageViewer, AzAction, coloring_icon, AzFileDialog, new_act

# import re
# import random
# import natsort
# current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/

the_color = UI_COLORS.get("processing_color")
the_color2 = UI_COLORS.get("processing_color")


class AzManualSlice(QtWidgets.QMainWindow):
    """
    Класс виджета просмотра изображений проекта JSON и установки точек для ручного разрезания
    """
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        # по правилам pep8
        self.image_widget = None
        self.slice_toolbar = QtWidgets.QToolBar("Manual visual cropping toolbar")  # панель инструментов кадрирования
        self.slice_actions = ()
        self.files_list = QtWidgets.QListWidget()  # Правый (по умолчанию) виджет для отображения перечня файлов

        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_widget()  # Настраиваем правую область: файлы
        self.current_data_list = []
        self.current_data_dir = ""
        self.current_file = None

        # перечень файлов текущего проекта
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.files_dock)

        # панель инструментов
        self.addToolBar(self.slice_toolbar)

        # элемент GUI с отображением текущего проекта хранения точек ручного кадрирования (ХТРК)
        self.top_dock = QtWidgets.QDockWidget("Visual manual cropping project name")  # контейнер для информации ХТРК
        self.label_info = QtWidgets.QLabel("Current manual project:")  # TODO: хранить имя проекта
        self.top_dock.setWidget(self.label_info)  # устанавливаем в контейнер QLabel
        self.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.top_dock)
        # self.top_dock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
        #                             QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.top_dock.setMaximumHeight(26)  # делаем "инфо о датасете"...
        self.top_dock.setMinimumHeight(25)  # ...без границ

        # главный виджет отображения изображения и точек
        self.image_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.image_widget)

        # Настроим все QDockWidgets для нашего main_win
        features = QtWidgets.QDockWidget.DockWidgetFeatures()  # features для док-виджетов
        for dock in ["top_dock", "files_dock"]:
            dock_settings = UI_AZ_SLICE_MANUAL.get(dock)  # храним их описание в config.py
            if not dock_settings[0]:  # 0 - show
                getattr(self, dock).setVisible(False)  # устанавливаем атрибуты напрямую
            if dock_settings[1]:  # 1 - closable
                features = features | QtWidgets.QDockWidget.DockWidgetClosable
            if dock_settings[2]:  # 2 - movable
                features = features | QtWidgets.QDockWidget.DockWidgetMovable
            if dock_settings[3]:  # 3 - floatable
                features = features | QtWidgets.QDockWidget.DockWidgetFloatable
            if dock_settings[4]:  # 4 - no_caption
                getattr(self, dock).setTitleBarWidget(QtWidgets.QWidget())
            if dock_settings[5]:  # 5 - no_actions - "close"
                getattr(self, dock).toggleViewAction().setVisible(False)
            getattr(self, dock).setFeatures(features)  # применяем настроенные атрибуты [1-3]

    def set_image(self, image):  # загрузка снимка для отображения
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            image_viewer = AzImageViewer()  # формируем контейнер
            image_viewer.set_pixmap(QtGui.QPixmap(image))  # помещаем туда изображение
            self.image_widget.setWidget(image_viewer)  # добавляем контейнер в окно QMdiSubWindow()
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def setup_actions(self):  # перечень инструментов
        self.slice_actions = (
            new_act(self, "Open", "glyph_folder", the_color, self.open_project),  # открыть
            new_act(self, "New", "glyph_add", the_color),  # новый
            new_act(self, "Save", "glyph_save", the_color, self.save),  # сохранить
            new_act(self, "Autosave", "glyph_time-save", the_color, self.autosave, True, True),  # автосохранение
            new_act(self, "Fit image", "glyph_crop", the_color),  # изображение по размеру окна
            new_act(self, "Hand", "glyph_hand", the_color, self.hand, True),  # перемещение по снимку
            new_act(self, "Add", "glyph_point_add", the_color, self.point_add, True),  # добавить метку
            new_act(self, "Move", "glyph_point_move", the_color, self.point_move, True),  # передвинуть метку
            new_act(self, "Delete", "glyph_point_remove", the_color, self.point_delete, True),  # удалить метку
            new_act(self, "Change crop size", "glyph_resize", the_color),  # сменить размер кадрирования
            new_act(self, "Slice", "glyph_cutter", the_color))  # разрезать снимки

    def hand(self):  # автосохранение
        pass

    def point_add(self):  # автосохранение
        pass

    def point_move(self):  # автосохранение
        pass

    def point_delete(self):  # автосохранение
        pass

    def open_project(self):  # сохранение

        self.signal_message.emit("Загружен проект '%s'" % project_name)

    def autosave(self):  # автосохранение
        pass

    def save(self):
        pass

    def setup_files_widget(self):
        # Настройка правого (по умолчанию) виджета для отображения перечня файлов датасета
        # right_layout = QtWidgets.QVBoxLayout()
        # right_layout.setContentsMargins(0, 0, 0, 0)
        # right_layout.setSpacing(0)
        # right_layout.addWidget(self.files_list)
        # file_list_widget = QtWidgets.QWidget()
        # file_list_widget.setLayout(self.right_layout)
        self.files_dock = QtWidgets.QDockWidget("Files List")  # Контейнер для виджета QListWidget
        self.files_dock.setWidget(self.files_list)  # устанавливаем виджет перечня файлов
        self.files_list.itemSelectionChanged.connect(self.file_selection_changed)  # выбора файла в QWidgetList

    # @QtCore.pyqtSlot()
    def file_selection_changed(self):  # метод смены файла
        items = self.files_list.selectedItems()
        if not items:
            return  # снимков не выбрано, выделение сброшено
        item = items[0]  # первый выделенный элемент
        index = self.current_data_list.index(str(item.text()))  # загрузку производим из current_data_list (!)
        file_to_load = self.current_data_list[index]
        self.load_file(file_to_load)

    def load_file(self, filename=None):  # загрузить для отображения новый графический файл
        if filename is None:  # файла нет
            return
        if self.current_file == filename:
            return
        self.current_file = filename  # устанавливаем свойство текущего файла
        self.set_image(filename)

    def setup_toolbar(self):
        # Настройка панели инструментов
        self.slice_toolbar.setIconSize(QtCore.QSize(30, 30))
        self.slice_toolbar.setFloatable(False)
        self.slice_toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        separator_placement = [3, 8]  # места после которых добавляется сепаратор
        for i, action in enumerate(self.slice_actions):  # формируем панель инструментов
            self.slice_toolbar.addAction(action)
            if i in separator_placement:
                self.slice_toolbar.addSeparator()
        group_acts = QtWidgets.QActionGroup(self)
        for i in range(5, 9):  # группировка, чтобы активно было только одной действие
            group_acts.addAction(self.slice_actions[i])

    # @QtCore.pyqtSlot()
    def change_input_data(self, image_list):
        print(image_list)

    # @QtCore.pyqtSlot()
    def slice_toggle_toolbar(self, int_code):
        """
        Настройка доступа к инструментам ручного кадрирования
        switch = 0, отключить всё; switch = 1, включить только первые два; 2 - включить все инструменты.
        """
        logic = False
        if int_code == 0:
            logic = False
        elif int_code == 2:
            logic = True
        for action in self.slice_actions:
            action.setEnabled(logic)
        if int_code == 1:
            self.slice_actions[0].setEnabled(True)
            self.slice_actions[1].setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AzManualSlice()
    window.show()
    sys.exit(app.exec())
