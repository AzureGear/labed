from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import AppSettings, UI_COLORS, UI_AZ_SLICE_MANUAL, load, save, dn_crop
from ui import AzImageViewer, az_file_dialog, az_custom_dialog, new_act
import sys
import os

# ----------------------------------------------------------------------------------------------------------------------
# Структура файла хранения проекта точек Визуального ручного кадрирования (AzManualSlice):
# "filename" = "D:/data_sets/uranium enrichment/test_cut/crude_uranium_enrichment.json"
# "scan_size" = "1280"
#  "images" = { "125n_FRA_2019-09.jpg" : [ ], ... }
# 		                                  ├-  "check" : True|False
# 		                                  └-  "points" : { [x1, y1], [x2, y2], ... , [xN, yN] }

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
        self.current_image_file = None
        self.input_file = None
        self.slice_toolbar = QtWidgets.QToolBar("Manual visual cropping toolbar")  # панель инструментов кадрирования
        self.slice_actions = ()
        self.files_list = QtWidgets.QListWidget()  # Правый (по умолчанию) виджет для отображения перечня файлов

        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_widget()  # Настраиваем правую область: файлы
        self.current_data_dir = ""
        self.current_data_list = []

        # перечень файлов текущего проекта
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.files_dock)

        # панель инструментов
        self.addToolBar(self.slice_toolbar)

        # элемент GUI с отображением текущего проекта хранения точек ручного кадрирования (РК)
        self.top_dock = QtWidgets.QDockWidget("Visual manual cropping project name")  # контейнер для информации РК
        self.label_info = QtWidgets.QLabel("Current manual project:")
        self.label_file_path = QtWidgets.QLabel()  # виджет для отображения пути к текущему файлу РК
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.label_info)
        hlayout.addWidget(self.label_file_path)
        hlayout.addStretch(1)
        widget = QtWidgets.QWidget()
        widget.setLayout(hlayout)
        self.top_dock.setWidget(widget)  # устанавливаем в контейнер QLabel
        self.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.top_dock)
        # self.top_dock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
        #                             QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.top_dock.setMaximumHeight(34)  # делаем "инфо о датасете"...
        self.top_dock.setMinimumHeight(33)  # ...без границ

        # главный виджет отображения изображения и точек
        self.image_widget = AzImageViewer()
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
        # QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        # try:
        self.image_widget.set_pixmap(QtGui.QPixmap(image))  # помещаем туда изображение
        # graphicsView->fitInView(QRectF(0, 0, width, height), Qt.KeepAspectRatio)
        # self.image_widget = image_viewer  # добавляем контейнер в окно QMdiSubWindow() ### !!!
        # except Exception as e:
        #     QtWidgets.QApplication.restoreOverrideCursor()
        #     raise e
        #     print("Error {}".format(e.args[0]))
        # finally:
        #     QtWidgets.QApplication.restoreOverrideCursor()

    def update_input_data(self, dn_json_file: dn_crop.DNjson):
        if dn_json_file is None:  # файл проекта не содержит данных
            self.slice_toggle_toolbar(0)  # деактивируем панель инструментов
        else:
            self.input_file = dn_json_file
            # Автозагрузка проекта при его наличии
            check_file = self.input_file.FullNameJsonFile + "_mc"
            if os.path.exists(check_file):
                self.load_mc_file(check_file)  # загружаем найденный файл проекта РК
            else:
                self.slice_toggle_toolbar(1)  # частично активируем панель инструментов

    def setup_actions(self):  # перечень инструментов
        self.slice_actions = (
            new_act(self, "Open", "glyph_folder", the_color, self.project_open),  # открыть
            new_act(self, "New", "glyph_add", the_color, self.project_new),  # новый
            new_act(self, "Save", "glyph_save", the_color, self.save),  # сохранить
            new_act(self, "Autosave", "glyph_time-save", the_color, self.autosave, True, True),  # автосохранение
            new_act(self, "Fit image", "glyph_crop", the_color, self.fit_image),  # изображение по размеру окна
            new_act(self, "Hand", "glyph_hand", the_color, self.hand, True),  # перемещение по снимку
            new_act(self, "Add", "glyph_point_add", the_color, self.point_add, True),  # добавить метку
            new_act(self, "Move", "glyph_point_move", the_color, self.point_move, True),  # передвинуть метку
            new_act(self, "Delete", "glyph_point_remove", the_color, self.point_delete, True),  # удалить метку
            new_act(self, "Change crop size", "glyph_resize", the_color),  # сменить размер кадрирования
            new_act(self, "Slice", "glyph_cutter", the_color))  # разрезать снимки

    def fit_image(self):  # отобразить изображение целиком
        self.image_widget.fitInView(self.image_widget.pixmap_item, QtCore.Qt.KeepAspectRatio)

    def hand(self):  # движение ручкой
        pass

    def point_add(self):  # удалить точку
        pass

    def point_move(self):  # передвинуть точку
        pass

    def point_delete(self):  # добавить точку
        pass

    def project_new(self):  # создать новый проект
        if self.input_file is None:
            self.signal_message.emit("Отсутствует загруженный проект *.json")
            return
        check_file = self.input_file.FullNameJsonFile
        check_file += "_mc"
        if os.path.exists(check_file):
            dialog = az_custom_dialog("Ручное кадрирование", "Найден файл для выбранного проекта, загрузить его?",
                                      True, True, parent=self)
            if not dialog:  # здесь наоборот accept = 0, reject = 1
                self.load_mc_file(check_file)  # загружаем найденный файл проекта РК
        else:
            save(check_file, "")  # пустой файл  # TODO: сделать заглушку под пустой файл
            self.load_mc_file(check_file, "Создан проект ручного кадрирования '%s'")
            self.slice_toggle_toolbar(2)  # полностью активируем панель инструментов

    def project_open(self):  # открыть проект
        sel_file = az_file_dialog(self, "Загрузить существующий проект ручного кадрирования",
                                  self.settings.read_last_dir(), False,
                                  filter="Manual crop projects (*.json_mc)", initial_filter="json_mc (*.json_mc)")
        if sel_file is not None:
            if os.path.exists(sel_file[0]):
                self.load_mc_file(sel_file[0])

    def load_mc_file(self, path, message="Загружен проект ручного кадрирования '%s'"):  # загрузка данных для РК
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.label_file_path.setText("<b>" + path + "</b>")
            if self.input_file is None:
                return
            self.current_data_dir = self.input_file.DataDict["path_to_images"]

            # формируем и записываем в память перечень изображений
            self.current_data_list = [os.path.join(self.current_data_dir, image_name) for image_name in
                                      self.input_file.ImgsName]
            self.fill_files_list(self.input_file.ImgsName)  # заполняем только именами файлов
            self.signal_message.emit(message % path)
            self.slice_toggle_toolbar(2)  # полностью активируем панель инструментов
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def autosave(self):  # автосохранение
        pass

    def save(self):  # сохранение
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

    @QtCore.pyqtSlot()
    def file_selection_changed(self):  # метод смены файла
        items = self.files_list.selectedItems()
        if not items:
            return  # снимков не выбрано, выделение сброшено
        item = items[0]  # первый выделенный элемент
        if item.text() == self.current_image_file:
            print("Выбрано точно такое же изображение")
            return
        sel_indexes = [i.row() for i in self.files_list.selectedIndexes()]  # выделенные объекты
        index = sel_indexes[0]  # первый выделенный объект
        # new_file = str(os.path.join(self.current_data_dir, item.text()))
        # old_file = self.current_data_list[0]
        # print(new_file)
        # print(old_file)
        # if new_file == old_file:
        #     print("They a equals!")
        # print("current index: " + str(index))
        file_to_load = self.current_data_list[index]  # обращаемся к внутреннему списку объектов
        self.load_image_file(file_to_load)

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

    def slice_toggle_toolbar(self, int_code):
        """
        Настройка доступа к инструментам ручного кадрирования
        switch = 0, отключить всё; switch = 1, включить только первые два; 2 - включить все инструменты.
        """
        logic = False
        if int_code == 0:
            logic = False
            self.clear()
        elif int_code == 2:
            logic = True
        for action in self.slice_actions:
            action.setEnabled(logic)
        if int_code == 1:
            self.slice_actions[0].setEnabled(True)
            self.slice_actions[1].setEnabled(True)

    def clear(self):
        self.label_file_path.setText("")
        self.files_list.clear()

    def load_image_file(self, filename=None):  # загрузить для отображения новый графический файл
        if filename is None:  # файла нет
            return
        self.current_image_file = filename  # устанавливаем свойство текущего файла
        if not os.path.exists(filename):
            self.signal_message.emit(
                "Изображение было перемещено, либо в проекте указан некорректный путь: " + filename)
            return
        self.set_image(filename)

    def fill_files_list(self, filenames):  # формируем перечень из list'а для QListWidget
        for filename in filenames:
            item = QtWidgets.QListWidgetItem(filename)
            self.files_list.addItem(item)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AzManualSlice()
    window.show()
    sys.exit(app.exec())
