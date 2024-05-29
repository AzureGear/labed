from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import AppSettings, UI_COLORS, UI_BASE_VIEW
from ui import AzImageViewer, new_act, coloring_icon, AzFileDialog
import os
import re
import random

# import natsort

the_color = UI_COLORS.get("datasets_color")
the_color2 = UI_COLORS.get("datasets_change_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class ViewDatasetUI(QtWidgets.QWidget):
    """
    Класс виджета просмотра датасетов
    """
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_and_labels()  # Настраиваем левую область: файлы, метки
        self.current_data_list = []
        self.current_data_dir = ""
        self.current_file = None

        main_win = QtWidgets.QMainWindow()  # главное окно виджетов
        self.image_viewer = AzImageViewer()  # класс QGraphicView, который предназначен для отрисовки графической сцены
        self.label_info = QtWidgets.QLabel("Информация о датасете:")  # за отображение информации будет отвечать QLabel
        self.label_info.setMaximumHeight(28)
        self.label_info.setWordWrap(True)  # устанавливаем перенос по словам

        self.top_dock = QtWidgets.QDockWidget("")  # контейнер для информации о датасете
        self.top_dock.setWidget(self.label_info)  # устанавливаем в контейнер QLabel
        self.tb_info_dataset.clicked.connect(self.show_info)  # соединяем с выводом инфо о датасете
        self.toggle_instruments()

        # Настроим все QDockWidgets для нашего main_win
        features = QtWidgets.QDockWidget.DockWidgetFeatures()  # features для док-виджетов
        for dock in ["top_dock", "files_dock"]:
            dock_settings = UI_BASE_VIEW.get(dock)  # храним их описание в config.py
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

        self.top_dock.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                    QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.top_dock.setMaximumHeight(28)  # делаем "инфо о датасете"...
        self.top_dock.setMinimumHeight(28)  # ...без границ
        main_win.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.top_dock)
        main_win.addToolBar(self.toolbar)
        main_win.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.files_dock)

        self.mdi = QtWidgets.QMdiArea()  # класс для данных (изображения, подписи, графики и т.п.)
        main_win.setCentralWidget(self.mdi)
        layout = QtWidgets.QVBoxLayout(self)  # главный QLayout на виджете
        layout.setContentsMargins(4, 4, 4, 4)  # визуально граница на 1 пиксель меньше для состыковки с другими
        layout.addWidget(main_win)  # добавляем наш QMainWindow

    @QtCore.pyqtSlot()
    def show_info(self):
        if self.tb_info_dataset.isChecked():
            self.top_dock.setHidden(False)
        else:
            self.top_dock.setHidden(True)

    def open_image(self, image_name):  # загрузить изображение
        self.image_viewer.set_pixmap(QtGui.QPixmap(image_name))
        self.image_viewer.fitInView(self.image_viewer.pixmap_item, QtCore.Qt.KeepAspectRatio)

    def setup_files_and_labels(self):
        # Настройка правого (по умолчанию) виджета для отображения перечня файлов датасета
        self.files_list = QtWidgets.QListWidget()
        self.files_search = QtWidgets.QLineEdit()  # строка поиска файлов
        self.files_search.setPlaceholderText("Filter files")
        self.files_search.textChanged.connect(self.file_search_changed)
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        # right_layout.addWidget(QLabel("Dataset/dir files:"))
        right_layout.addWidget(self.files_search)
        right_layout.addWidget(self.files_list)
        file_list_widget = QtWidgets.QWidget()
        file_list_widget.setLayout(right_layout)
        self.files_dock = QtWidgets.QDockWidget("Files List")  # Контейнер для виджета QListWidget
        self.files_dock.setWidget(file_list_widget)  # устанавливаем виджет перечня файлов
        self.files_list.itemSelectionChanged.connect(self.file_selection_changed)  # выбора файла в QWidgetList
        # fileListLayout = QtWidgets.QVBoxLayout()

    def toggle_instruments(self):  # включить/выключить инструменты при загрузке данных
        if self.current_data_dir and self.files_list.count() > 0:
            self.set_instrument(self.tb_info_dataset, True)
            self.set_instrument(self.actions_show_data, True)
            self.set_instrument(self.actions_labels, True)
            self.set_instrument(self.actions_control_images, True)
            self.set_instrument(self.action_shuffle_data, True)
        else:  # нет ни проекта, ни данных
            self.set_instrument(self.tb_info_dataset, False)
            self.set_instrument(self.actions_show_data, False)
            self.set_instrument(self.actions_labels, False)
            self.set_instrument(self.actions_control_images, False)
            self.set_instrument(self.action_shuffle_data, False)

    def set_instrument(self, item, b):
        if isinstance(item, QtWidgets.QAction) or isinstance(item, QtWidgets.QToolButton):
            item.setEnabled(b)
        elif isinstance(item, tuple):  # если набор, то вызываем себя рекурсивно
            for obj in item:
                self.set_instrument(obj, b)

    @QtCore.pyqtSlot()
    def open_project(self):  # загрузить датасет
        pass
        # os.scandir(folderPath)
        #
        # for root, dirs, files in os.walk(folderPath):
        #     for file in files:
        #         if file.lower().endswith(tuple(types)):
        #             relativePath = os.path.normpath(os.path.join(root, file))
        #             images.append(relativePath)
        # # images = natsort.os_sorted(images)
        # return images

    @QtCore.pyqtSlot()
    def open_last_data(self):  # загрузка последних использованных данных
        last_data = self.settings.read_last_load_data()
        if self.current_data_dir == last_data:
            self.signal_message.emit("Текущие данные являются последними использованными")
            return
        if last_data and os.path.exists(last_data):
            self.open_dir(dir_path=last_data, no_dialog=True)  # загружаем данные без диалогов
        else:
            self.signal_message.emit("Использованные ранее данные отсутствуют")

    @QtCore.pyqtSlot()
    def open_dir(self, _value=False, dir_path=None, no_dialog=False):  # загрузить каталог изображений
        sel_dir = None  # каталог с данными по умолчанию
        if no_dialog:
            sel_dir = dir_path
        else:
            last_dir = self.settings.read_last_dir()  # вспоминаем прошлый открытый каталог
            using_folder = current_folder
            if last_dir and os.path.exists(last_dir):
                using_folder = last_dir
            # каталог с данными получаем через диалог
            sel_dir = AzFileDialog(self, "Select directory to load images", using_folder, True)
        if sel_dir:
            self.settings.write_last_load_data(sel_dir)  # сохраняем последние добавленные данные
            self.prepear_for_load()  # подготавливаем: закрываем SubWindows, очищаем все
            self.import_dir_images(sel_dir)  # импортируем изображения
            self.current_data_dir = sel_dir  # устанавливаем текущий каталог
            self.set_dataset_info(sel_dir)  # обновляем информацию о датасете
            if self.files_list.count() > 0:  # в датасете хотя бы 1 изображение
                self.files_list.setCurrentRow(0)  # если первый раз открыли датасет - загружаем первое изображение
            self.mdi_add_window()  # добавляем окно
            self.toggle_instruments()  # обновляем доступ к инструментам

    def prepear_for_load(self):
        self.files_search.clear()  # очищаем поисковую строку
        self.current_data_list.clear()
        self.current_file = None  # устанавливаем текущий файл
        self.current_data_dir = None
        self.mdi.closeAllSubWindows()  # закрываем все предыдущие окна
        self.files_list.clear()  # очищаем перечень файлов

    def set_dataset_info(self, path):
        # str = "%s - %s" % (index, name)
        str_info = "Каталог датасета: {}\nКоличество объектов: {}".format(path, str(self.files_list.count()))
        # print('Sum of {} and 2 is {}'.format(i, add_partials[i - 1](2)))
        self.label_info.setText(str_info)

    def import_dir_images(self, path):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            filenames = self.search_for_images(path)  # получаем перечень всех доступных изображений
            self.current_data_list = filenames  # сохраняем его в памяти
            self.fill_files_list(filenames)
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()

    def fill_files_list(self, filenames):  # формируем перечень из list'а для QListWidget
        for filename in filenames:
            item = QtWidgets.QListWidgetItem(filename)
            self.files_list.addItem(item)

    def search_for_images(self, path):  # формирование перечня загружаемых изображений
        deep = self.settings.read_load_sub_dir()
        # используем только поддерживаемые QImageReader расширения
        types = [".%s" % fmt.data().decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()]
        images = []  # перечень возвращаемых изображений
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(tuple(types)):
                    relative_path = os.path.normpath(os.path.join(root, file))
                    images.append(relative_path)
            if not deep:  # если в настройках не отмечен поиск по субдиректориям
                return
        # images = natsort.os_sorted(images)
        return images

    @QtCore.pyqtSlot()
    def file_search_changed(self):
        self.files_list.clear()  # очищаем список
        self.files_list.clearSelection()  # убираем выделение
        if len(self.current_data_list) <= 0:  # в датасете нет данных
            return
        if len(self.files_search.text()) <= 0:  # если текста нет возвращаем исходный список
            self.fill_files_list(self.current_data_list)
            return
        pattern = self.files_search.text()  # устанавливаем шаблон поиска
        filtered = [s for s in self.current_data_list if re.findall(pattern, s, re.IGNORECASE)]  # отфильтровываем
        if len(filtered) > 0:  # если найденных результатов
            self.fill_files_list(filtered)  # заполняем виджет

    def files_step_image(self, move_forward: bool = True):
        if move_forward:  # движемся вперед...
            index = self.files_list.moveCursor(QtWidgets.QAbstractItemView.MoveDown, QtCore.Qt.NoModifier)
        else:  # ...или назад по списку
            index = self.files_list.moveCursor(QtWidgets.QAbstractItemView.MoveUp, QtCore.Qt.NoModifier)
        if index.isValid():  # проверяем валидность индекса
            self.files_list.setCurrentIndex(index)

    @QtCore.pyqtSlot()
    def file_selection_changed(self):  # метод смены файла
        items = self.files_list.selectedItems()
        if not items:
            return  # снимков не выбрано, выделение сброшено
        item = items[0]  # первый выделенный элемент
        index = self.current_data_list.index(str(item.text()))  # загрузку производим из current_data_list (!)
        file_to_load = self.current_data_list[index]
        self.load_file(file_to_load)

    def setup_toolbar(self):
        # Настройка Toolbar'a
        self.toolbar = QtWidgets.QToolBar("Dataset viewer instruments")  # панель инструментов для просмотра датасетов
        self.toolbar.setIconSize(QtCore.QSize(30, 30))
        self.toolbar.setFloatable(False)
        self.toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        self.toolbar.addWidget(self.tb_info_dataset)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.actions_load)
        self.toolbar.addWidget(self.tb_load_preset)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.actions_show_data)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.actions_adjust)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.actions_labels)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.actions_control_images)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_shuffle_data)

    @QtCore.pyqtSlot()
    def mdi_windows_1x(self):
        if len(self.mdi.subWindowList()) == 1: self.mdi_show_sub_windows()  # открыто одно окно
        if len(self.mdi.subWindowList()) > 0:  # есть открытые
            current_sub = self.mdi.activeSubWindow()  # а есть ли активные?
            if current_sub is None: current_sub = self.mdi.subWindowList(0)  # нет? берем первый попавшийся
            for sub_win in self.mdi.subWindowList():  # закрываем все кроме активного/первого
                if current_sub != sub_win:
                    self.mdi.removeSubWindow(sub_win)  # закрываем все кроме активного
            self.mdi.activateNextSubWindow()  # активируем окно
            self.mdi_show_sub_windows()  # выравниваем
            return
        self.mdi_add_window()  # если открытых нет

    @QtCore.pyqtSlot()
    def mdi_add_window(self):
        if self.current_file is None:
            self.signal_message.emit("Ошибка загрузки файла")
        sub = QtWidgets.QMdiSubWindow()
        sub.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)  # удалять окна при их закрытии
        self.mdi_window_set_image(sub, self.current_file)
        self.mdi.addSubWindow(sub)
        sub.show()
        self.mdi_show_sub_windows()  # выравниваем

    def mdi_window_set_image(self, subwindow, image):  # загрузка снимка для отображения
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            image_viewer = AzImageViewer()  # формируем контейнер
            image_viewer.set_pixmap(QtGui.QPixmap(image))  # помещаем туда изображение
            subwindow.setWidget(image_viewer)  # добавляем контейнер в окно QMdiSubWindow()
            subwindow.setWindowTitle(str(image))  # заголовок окна
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def mdi_windows_4x(self):
        self.mdi_set_windows(4)

    @QtCore.pyqtSlot()
    def mdi_windows_16x(self):
        self.mdi_set_windows(16)

    def mdi_set_windows(self, windows_number: int):
        if len(self.mdi.subWindowList()) > windows_number:  # Вариант 1: у нас много окон
            for sub_win in reversed(self.mdi.subWindowList()):  # будем удалять лишние SubWidows с конца
                if len(self.mdi.subWindowList()) == windows_number:
                    self.mdi_show_sub_windows()  # располагаем как выбрано в инструментах
                    return
                else:
                    self.mdi.removeSubWindow(sub_win)  # удаляем лишние
        elif len(self.mdi.subWindowList()) < windows_number:  # Вариант 2: у нас мало окон?
            while len(self.mdi.subWindowList()) < windows_number:  # будем добавлять
                self.mdi_add_window()
        else:  # Вариант 3: у нас уже 16 окон; однако же они могут быть не выстроены
            self.mdi_show_sub_windows()  # располагаем как выбрано в инструментах

    def mdi_cascade(self):
        self.mdi.cascadeSubWindows()

    def mdi_tiled(self):
        self.mdi.tileSubWindows()

    def mdi_shuffle(self):  # загрузить случайные данные (перемешать)
        if len(self.mdi.subWindowList()) <= 0 or len(self.current_data_list) <= 0:
            return
        list_subs = self.mdi.subWindowList()
        for sub in list_subs:
            random_filename = random.choice(self.current_data_list)
            self.mdi_window_set_image(sub, random_filename)
        active_mdi = self.mdi.activeSubWindow()
        items = self.files_list.findItems(active_mdi.windowTitle(), QtCore.Qt.MatchFlag.MatchExactly)
        if len(items) > 0:
            self.files_list.setCurrentItem(items[0])

    @QtCore.pyqtSlot()
    def mdi_show_sub_windows(self):
        if self.actions_adjust[2].isChecked():  # не следить за расположением
            return
        elif self.actions_adjust[0].isChecked():  # установлен режим Tiled
            self.mdi.tileSubWindows()
        elif self.actions_adjust[1].isChecked():  # установлен режим Cascade
            self.mdi.cascadeSubWindows()

    @QtCore.pyqtSlot()
    def move_image_right(self):
        self.files_step_image(True)

    @QtCore.pyqtSlot()
    def move_image_left(self):
        self.files_step_image(False)

    def setup_actions(self):
        # Actions
        # Действия для загрузки данных
        self.actions_load = (
            new_act(self, "Load last data", "glyph_folder_recent", the_color, self.open_last_data),
            new_act(self, "Load dir", "glyph_folder_clear", the_color, self.open_dir),
            # загрузить каталог
            new_act(self, "Load dataset", "glyph_folder_dataset", the_color, self.open_project))
        self.action_load_presets = new_act(self, "Load preset dataset", "glyph_folder_preset", the_color)
        self.tb_load_preset = QtWidgets.QToolButton()  # кнопка загрузки предустановленных датасетов
        self.tb_load_preset.setText("Load preset dataset")
        self.tb_load_preset.setIcon(coloring_icon('glyph_folder_preset', the_color))
        self.tb_load_preset.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)  # со всплывающим меню

        self.tb_info_dataset = QtWidgets.QToolButton()  # кнопка информации о датасете
        self.tb_info_dataset.setText(" Info")
        self.tb_info_dataset.setIcon(coloring_icon("glyph_info", the_color))
        self.tb_info_dataset.setCheckable(True)

        self.tb_info_dataset.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # self.tb_load_preset.addActions(self.actions_load)

        # Действия для отображения загруженных данных из датасетов (картинок) в окнах QMdiSubWindow()
        self.actions_show_data = (
            new_act(self, "One window", "glyph_image", the_color, self.mdi_windows_1x),
            new_act(self, "Add window", "glyph_add_image", the_color, self.mdi_add_window),
            new_act(self, "4x windows", "glyph_image_4x", the_color, self.mdi_windows_4x),
            new_act(self, "16x windows", "glyph_image_16x", the_color, self.mdi_windows_16x))

        # Действия для расположения окон QMdiSubWindow()
        self.actions_adjust = (
            new_act(self, "Tiled", "glyph_lay_tiled", the_color, self.mdi_show_sub_windows, True, True),
            new_act(self, "Cascade", "glyph_lay_cascade", the_color, self.mdi_show_sub_windows, True),
            new_act(self, "Disable layout", "glyph_lay_off", the_color, self.mdi_show_sub_windows, True))

        action_group_adjust = QtWidgets.QActionGroup(self)  # общая группа: расположение каскадом, мозаикой или выкл.
        for action in self.actions_adjust:
            action_group_adjust.addAction(action)

        # Действия для меток и имён
        self.actions_labels = (new_act(self, "Show labels", "glyph_label", the_color),
                               new_act(self, "Show filenames", "glyph_signature", the_color))
        for action in self.actions_labels:
            action.setCheckable(True)

        self.actions_control_images = (new_act(self, "Preview", "glyph_left_arrow", the_color, self.move_image_left),
                                       new_act(self, "Next", "glyph_right_arrow", the_color, self.move_image_right))

        self.action_shuffle_data = new_act(self, "Shuffle data", "glyph_dice", the_color,
                                           self.mdi_shuffle)  # отображаемые данные


def load_file(self, filename=None):  # загрузить для отображения новый графический файл
    if filename is None:  # файла нет
        return
    self.current_file = filename  # устанавливаем свойство текущего файла

    if len(self.mdi.subWindowList()) <= 0:  # активного окна для загрузки файла нет
        return
    # выбранный в окне файлов объект не загружен в активное окно и открыто хотя бы одно окно
    active_mdi = self.mdi.activeSubWindow()
    if active_mdi.windowTitle() != filename and len(self.mdi.subWindowList()) > 0:
        self.mdi_window_set_image(active_mdi, filename)
    # self.files_list.repaint()
    # return
