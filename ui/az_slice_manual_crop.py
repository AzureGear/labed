from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import AppSettings, UI_COLORS, UI_AZ_SLICE_MANUAL, load, save, dn_crop, AzImageViewer, ViewState
from ui import az_file_dialog, az_custom_dialog, new_act, natural_order
import sys
import os

# current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/

the_color = UI_COLORS.get("processing_color")
the_color2 = UI_COLORS.get("processing_color")

# TODO: сделать чтобы класс Дениса MC вызывался как функция, которая бы обновляла данные, чтобы я мог просто обновить объект класса и проверить получение данных. Или нет, ведь файл может отличаться и выбран быть не тот, что пренадлежит JSNO'у...


class AzManualSlice(QtWidgets.QMainWindow):
    """
    Класс виджета просмотра изображений проекта JSON и установки точек для ручного разрезания
    """
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        # по правилам pep8
        self.files_dock = None
        self.slice_manual_size = None
        self.current_image_file = None
        self.input_file = None
        self.slice_toolbar = QtWidgets.QToolBar("Manual visual cropping toolbar")  # панель инструментов кадрирования
        self.slice_actions = ()
        self.files_list = QtWidgets.QListWidget()  # Правый (по умолчанию) виджет для отображения перечня файлов

        self.current_scan_size = self.settings.read_slice_crop_size()  # размер окна сканирования по умолчанию
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_widget()  # Настраиваем правую область: файлы
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
        self.top_dock.setMaximumHeight(33)  # делаем "инфо о датасете"...
        self.top_dock.setMinimumHeight(33)  # ...без границ

        # главный виджет отображения изображения и точек
        self.image_widget = AzImageViewer(self)
        self.image_widget.scan_size = self.current_scan_size
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

    def set_image(self, image):  # загрузка снимка и разметки для отображения
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.image_widget.set_pixmap(QtGui.QPixmap(image))  # помещаем туда изображение
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def update_input_data(self, dn_json_file: dn_crop.DNjson):
        """
        Обновление данных. Происходит при смене или загрузке оригинального проекта <name>.json
        в формате SAMA. Производит проверку на наличие файла с расширением <name>.json_mc и загружает его
        в случае успеха.
        """
        self.clear()  # очищаем все формы и переменные от использованных ранее данных
        if dn_json_file is None:  # новый файл проекта не содержит данных
            self.slice_toggle_toolbar(0)  # деактивируем панель инструментов
        else:
            self.input_file = dn_json_file  # устанавливаем ссылку на файл оригинального проекта
            # Автозагрузка проекта при его наличии
            check_file = self.input_file.FullNameJsonFile + "_mc"  # обнаружен файл РК
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
            new_act(self, "Change crop size", "glyph_resize", the_color, self.change_crop_size),
            # сменить размер кадрирования
            new_act(self, "Slice", "glyph_cutter", the_color))  # разрезать снимки

    def fit_image(self):  # отобразить изображение целиком
        self.image_widget.fitInView(self.image_widget.pixmap_item, QtCore.Qt.KeepAspectRatio)

    def hand(self):  # движение ручкой
        if self.image_widget.view_state != ViewState.hand_move:
            self.image_widget.set_view_state(ViewState.hand_move)
        else:
            self.slice_actions[5].setChecked(False)
            self.image_widget.set_view_state()

    def point_add(self):  # добавить точку
        if self.image_widget.view_state != ViewState.points_state:
            self.image_widget.set_view_state(ViewState.points_state)
        else:
            self.slice_actions[6].setChecked(False)
            self.image_widget.set_view_state()

    def point_move(self):  # передвинуть точку
        pass

    def point_delete(self):  # удалить точку
        import utils.az_graphic_view
        # self.image_widget.PyQt5.QtCore.QPointF(625.6515151515151, 1021.284090909091)

        point_mc = utils.az_graphic_view.AzPointWithRect(QtCore.QPointF(625.6515151515151, 1021.284090909091),
                                                         QtGui.QColor(QtCore.Qt.GlobalColor.yellow),
                                                         self.current_scan_size)
        print(point_mc.point)
        self.image_widget.scene().addItem(point_mc)  # добавляем объект на сцену

    def create_blank_file(self):  # создать новый пустой проект РК
        # --------------------------------------------------------------------------------------------------------------
        # Структура файла хранения проекта точек Визуального ручного кадрирования (AzManualSlice):
        # "filename" = "D:/data_sets/uranium enrichment/test_cut/crude_uranium_enrichment.json"
        # "scan_size" = "1280"
        #  "images" = { "125n_FRA_2019-09.jpg" : [ ], ... }
        # 		                                   └-  "points" : { [x1, y1], [x2, y2], ... , [xN, yN] }
        data = dict()
        data["filename"] = self.input_file.FullNameJsonFile
        data["path_to_images"] = self.input_file.DataDict["path_to_images"]
        data["scan_size"] = self.current_scan_size
        dict_images = dict()
        if self.input_file.ImgsName is not None:
            if len(self.input_file.ImgsName) > 0:
                for file in self.input_file.ImgsName:
                    dict_images[file] = None
        data["images"] = dict_images
        return data

    def project_new(self):  # создать новый проект
        if self.input_file is None:
            self.signal_message.emit("Отсутствует загруженный проект *.json")
            return
        check_file = self.input_file.FullNameJsonFile
        check_file += "_mc"
        if os.path.exists(check_file):
            dialog = az_custom_dialog("Ручное кадрирование", "Найден файл для выбранного проекта, загрузить его?", True,
                                      True, custom_button=True, custom_text="Пересоздать", parent=self)
            if dialog == 1:  # открыть найденный
                self.clear()
                self.load_mc_file(check_file)  # загружаем найденный файл проекта РК
            elif dialog == 4:  # пересоздать
                self.clear()
                save(check_file, self.create_blank_file())  # пересоздаём
                self.load_mc_file(check_file)
        else:  # файла не существует, значит...
            save(check_file, self.create_blank_file())  # ...создаём новый пустой файл
            self.load_mc_file(check_file, "Создан проект ручного кадрирования '%s'")

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
            self.clear()
            self.label_file_path.setText("<b>" + path + "</b>")
            if self.input_file is None:
                self.signal_message.emit("Ошибка загрузки")
                return
            original_json = self.input_file.FullNameJsonFile
            manual_crop_json = load(path)  # внутренний файл РК *.json_mc
            if manual_crop_json is None:  # ошибка загрузки
                self.signal_message.emit(f"Произошла ошибка при загрузке проекта ручного кадрирования: '{path}'")
                return
            if original_json != manual_crop_json["filename"]:
                if az_custom_dialog("Автозагрузка проекта ручного кадрирования", "Имена проектов оригинального JSON и \
                ручного кадрирования не совпадают. Продолжить загрузку?", True, True) == 2:
                    return
            current_data_dir = self.input_file.DataDict["path_to_images"]
            self.signal_message.emit(message % path)

            # формируем и записываем в память перечень изображений
            list_input = [os.path.join(current_data_dir, image_name) for image_name in
                          self.input_file.ImgsName]
            # TODO: сделать загрузку точек и настройку формы
            self.current_data_list = sorted(list_input, key=natural_order)  # сортируем
            self.fill_files_list(sorted(self.input_file.ImgsName, key=natural_order))  # заполняем только именами файлов
            self.signal_message.emit(message % path)
            self.slice_toggle_toolbar(3)  # полностью активируем панель инструментов на 3/4
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def autosave(self):  # автосохранение
        pass

    def save(self):  # сохранение
        pass

    def change_crop_size(self):  # смена размера окна сканирования:
        info = "Текущий размер окна сканирования: " + str(self.current_scan_size) + "\nВведите новое значение:"
        size, done = QtWidgets.QInputDialog.getInt(self, "Смена сканирующего разрешения", info, self.current_scan_size)
        if done:
            if size > 8000:
                size = 8000
            elif size < 16:
                size = 16
            self.slice_manual_size.setText(str(size))
            self.current_scan_size = size
            self.settings.write_slice_crop_size(size)
            self.image_widget.crop_scan_size_changed(size)
            # TODO: сделать функцию для обновления меток

    def setup_files_widget(self):
        # Настройка правого (по умолчанию) виджета для отображения перечня файлов датасета
        self.files_dock = QtWidgets.QDockWidget("Files List")  # Контейнер для виджета QListWidget
        self.files_dock.setWidget(self.files_list)  # устанавливаем виджет перечня файлов
        self.files_list.itemSelectionChanged.connect(self.file_selection_changed)  # выбора файла в QWidgetList

    @QtCore.pyqtSlot()
    def file_selection_changed(self):  # метод смены изображения
        items = self.files_list.selectedItems()
        if not items:
            return  # снимков не выбрано, выделение сброшено
        item = items[0]  # первый выделенный элемент
        if item.text() == self.current_image_file:
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
        if file_to_load is None:  # файла нет
            return
        self.current_image_file = file_to_load  # устанавливаем свойство текущего файла
        if not os.path.exists(file_to_load):
            self.signal_message.emit(
                "Изображение было перемещено, либо в проекте указан некорректный путь: " + file_to_load)
            return
        self.set_image(file_to_load)  # добавляем растровый файл для отображения
        # files_list файлов названия такие же как и в *.json, поэтому используем item.text()
        img_data = self.get_image_data(item.text())  # массив данных по названию файла
        shapes = img_data['shapes']
        for shape in shapes:  # просматриваем словарь "shapes"
            class_name = self.get_label_name(shape['cls_num'])
            colors = self.get_label_color(class_name)
            color = QtGui.QColor(colors[0], colors[1], colors[2])
            points = shape['points']
            # передаём на отрисовку: имя, цвет, точки
            self.image_widget.add_polygon_to_scene(class_name, color, points)

        if self.current_image_file:  # все добавлено и отображено, значит можно включать инструменты
            self.slice_toggle_toolbar(2)

    def setup_toolbar(self):
        # Настройка панели инструментов
        self.slice_toolbar.setIconSize(QtCore.QSize(30, 30))
        self.slice_manual_size = QtWidgets.QLabel(str(self.current_scan_size))
        self.slice_toolbar.setFloatable(False)
        self.slice_toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        separator_placement = [3, 8]  # места после которых добавляется сепаратор
        unique_sep = [9]  # место для добавления особенного виджета
        for i, action in enumerate(self.slice_actions):  # формируем панель инструментов
            self.slice_toolbar.addAction(action)
            if i in separator_placement:
                self.slice_toolbar.addSeparator()
            if i in unique_sep:
                self.slice_toolbar.addWidget(self.slice_manual_size)
                self.slice_toolbar.addSeparator()
        group_acts = QtWidgets.QActionGroup(self)
        for i in range(5, 9):  # группировка, чтобы активно было только одной действие
            group_acts.addAction(self.slice_actions[i])

    def slice_toggle_toolbar(self, int_code):
        """
        Настройка доступа к инструментам ручного кадрирования: int_code
        0 - отключить всё; 1 - включить только первые два; 2 - включить все инструменты;
        3 - включить всё кроме активных инструментов
        """
        diff_acts = []
        logic = False
        if int_code == 0:  # отключить все
            logic = False
        elif int_code == 1:  # включить только первые два
            logic = False
            diff_acts = [0, 1]
        elif int_code == 2:  # включить всю панель
            logic = True
        elif int_code == 3:  # выключить инструменты действий
            logic = True
            diff_acts = [4, 5, 6, 7, 8]  # выключаем actions под этими номерами
        for i, action in enumerate(self.slice_actions):
            if len(diff_acts) > 0:
                if i in diff_acts:
                    action.setEnabled(not logic)
                else:
                    action.setEnabled(logic)
            else:
                action.setEnabled(logic)

    def clear(self):
        self.image_widget.clear_scene()
        self.label_file_path.setText("")
        self.files_list.clear()

    def fill_files_list(self, filenames):  # формируем перечень из list'а для QListWidget
        for filename in filenames:
            item = QtWidgets.QListWidgetItem(filename)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.files_list.addItem(item)

    def get_image_data(self, image_name):
        return self.input_file.DataDict["images"].get(image_name, None)

    def get_label_name(self, cls_num):
        if cls_num < len(self.input_file.DataDict["labels"]):
            return self.input_file.DataDict["labels"][cls_num]

    def get_label_color(self, cls_name):  # извлечение цвета меток
        return self.input_file.DataDict["labels_color"].get(cls_name, None)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AzManualSlice()
    window.show()
    sys.exit(app.exec())
