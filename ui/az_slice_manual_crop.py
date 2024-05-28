from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy import QtWidgets
from qdarktheme.qtpy import QtGui
import sys
from utils import AppSettings, UI_COLORS
from ui import AzImageViewer, AzAction, coloring_icon, AzFileDialog
import os
import re
import random

# import natsort

the_color = UI_COLORS.get("processing_color")
the_color2 = UI_COLORS.get("processing_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class AzManualSlice(QtWidgets.QMainWindow):
    """
    Класс виджета просмотра датасетов
    """
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        # по правилам pep8
        self.files_list = None
        self.slice_toolbar = None
        self.slice_actions = None
        self.files_dock = None
        
        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_widget()  # Настраиваем правую область: файлы
        self.current_data_list = []
        self.current_data_dir = ""
        self.current_file = None

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.files_dock)
        self.addToolBar(self.slice_toolbar)

    def setup_actions(self):  # перечень инструментов
        self.slice_actions = (
            QtGui.QAction(coloring_icon("glyph_folder", the_color), "Open"),  # открыть
            QtGui.QAction(coloring_icon("glyph_add", the_color), "New"),  # новый
            QtGui.QAction(coloring_icon("glyph_save", the_color), "Save"),  # сохранить
            QtGui.QAction(coloring_icon("glyph_time-save", the_color), "Autosave"),  # автосохранение
            QtGui.QAction(coloring_icon("glyph_crop", the_color), "Fit image"),  # изображение по размеру окна
            QtGui.QAction(coloring_icon("glyph_hand", the_color), "Hand"),  # перемещение по снимку
            QtGui.QAction(coloring_icon("glyph_point_add", the_color), "Add"),  # добавить метку
            QtGui.QAction(coloring_icon("glyph_point_move", the_color), "Move"),  # передвинуть метку
            QtGui.QAction(coloring_icon("glyph_point_remove", the_color), "Delete"),  # удалить метку
            QtGui.QAction(coloring_icon("glyph_resize", the_color), "Change crop size"),  # сменить размер кадрирования
            QtGui.QAction(coloring_icon("glyph_cutter", the_color), "Slice"))  # разрезать снимки
        self.slice_actions[3].setCheckable(True)  # у автосохранения делаем кнопку нажимания

    def setup_files_widget(self):
        # Настройка правого (по умолчанию) виджета для отображения перечня файлов датасета
        self.files_list = QtWidgets.QListWidget()
        # right_layout = QtWidgets.QVBoxLayout()
        # right_layout.setContentsMargins(0, 0, 0, 0)
        # right_layout.setSpacing(0)
        # right_layout.addWidget(self.files_list)
        # file_list_widget = QtWidgets.QWidget()
        # file_list_widget.setLayout(self.right_layout)
        self.files_dock = QtWidgets.QDockWidget("Files List")  # Контейнер для виджета QListWidget
        self.files_dock.setWidget(self.files_list)  # устанавливаем виджет перечня файлов
        self.files_list.itemSelectionChanged.connect(self.file_selection_changed)  # выбора файла в QWidgetList

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
        self.current_file = filename  # устанавливаем свойство текущего файла

        # !!!!!!
        # выбранный в окне файлов объект не загружен в активное окно и открыто хотя бы одно окно
        active_mdi = self.mdi.activeSubWindow()
        if active_mdi.windowTitle() != filename and len(self.mdi.subWindowList()) > 0:
            self.mdi_window_set_image(active_mdi, filename)

    def setup_toolbar(self):
        # Настройка панели инструментов
        self.slice_toolbar = QtWidgets.QToolBar("Manual visual cropping toolbar")  # панель инструментов кадрирования
        self.slice_toolbar.setIconSize(QtCore.QSize(30, 30))
        self.slice_toolbar.setFloatable(False)
        self.slice_toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        separator_placement = [3, 5, 8]  # места после которых добавляется сепаратор
        for i, action in enumerate(self.slice_actions):  # формируем панель инструментов
            self.slice_toolbar.addAction(action)
            if i in separator_placement:
                self.slice_toolbar.addSeparator()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AzManualSlice()
    window.show()
    sys.exit(app.exec())
