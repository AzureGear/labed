from qdarktheme.qtpy.QtCore import Qt, QSize, pyqtSignal, Slot, QFile
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication, QMessageBox, QToolBar, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QGraphicsSimpleTextItem, QAction, QListWidget, QMdiArea, QMdiSubWindow, QActionGroup, QListWidgetItem, \
    QSizePolicy, QFileDialog
from qdarktheme.qtpy.QtGui import QPixmap, QImageReader
from utils import AppSettings, UI_COLORS, UI_BASE_VIEW
from ui import AzImageViewer, AzAction, coloring_icon, AzFileDialog
import os
import re

# import natsort

the_color = UI_COLORS.get("datasets_color")
the_color2 = UI_COLORS.get("datasets_change_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class ViewDatasetUI(QWidget):
    """
    Класс виджета просмотра датасетов
    """
    signal_message = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_and_labels()  # Настраиваем левую область: файлы, метки
        self.count = 0
        self.current_data = ""

        main_win = QMainWindow()  # главное окно виджетов
        self.image_viewer = AzImageViewer()  # класс QGraphicView, который предназначен для отрисовки графической сцены
        self.label_info = QLabel("Информация о датасете:")  # за отображение информации будет отвечать QLabel
        self.label_info.setMaximumHeight(28)
        self.label_info.setWordWrap(True)  # устанавливаем перенос по словам

        self.top_dock = QDockWidget("")  # контейнер для информации о датасете
        self.top_dock.setWidget(self.label_info)  # устанавливаем в контейнер QLabel
        self.tb_info_dataset.clicked.connect(self.show_info)  # соединяем с выводом инфо о датасете

        self.toggle_instruments()
        button = QPushButton("Сделай хорошо")

        # Настроим все QDockWidgets для нашего main_win
        features = QDockWidget.DockWidgetFeatures()  # features для док-виджетов
        for dock in ["top_dock", "files_dock"]:
            dock_settings = UI_BASE_VIEW.get(dock)  # храним их описание в config.py
            if not dock_settings[0]:  # 0 - show
                getattr(self, dock).setVisible(False)  # устанавливаем атрибуты напрямую
            if dock_settings[1]:  # 1 - closable
                features = features | QDockWidget.DockWidgetClosable
            if dock_settings[2]:  # 2 - movable
                features = features | QDockWidget.DockWidgetMovable
            if dock_settings[3]:  # 3 - floatable
                features = features | QDockWidget.DockWidgetFloatable
            if dock_settings[4]:  # 4 - no_caption
                getattr(self, dock).setTitleBarWidget(QWidget())
            if dock_settings[5]:  # 5 - no_actions - "close"
                getattr(self, dock).toggleViewAction().setVisible(False)
            getattr(self, dock).setFeatures(features)  # применяем настроенные атрибуты [1-3]

        self.top_dock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.top_dock.setMaximumHeight(28)
        self.top_dock.setMinimumHeight(28)
        main_win.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.top_dock)
        main_win.addToolBar(self.toolbar)
        main_win.addDockWidget(Qt.RightDockWidgetArea, self.files_dock)

        # self.top_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        # self.label_info.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # main_win.resizeDocks(self.top_dock, [150], Qt.Orientation.Vertical)  # THIS!

        self.mdi = QMdiArea()  # класс для данных (изображения, подписи, графики и т.п.)
        # self.mdi.tileSubWindows()   # по умолчанию ставим tileSubWi
        main_win.setCentralWidget(self.mdi)

        # main_win.setCentralWidget(self.image_viewer)
        layout = QVBoxLayout(self)  # главный QLayout на виджете
        layout.setContentsMargins(4, 4, 4, 4)  # визуально граница на 1 пиксель меньше для состыковки с другими
        layout.addWidget(main_win)  # добавляем наш QMainWindow
        layout.addWidget(button)  # test button

        test_img = os.path.join(current_folder, "..", "test.jpg")
        self.image_viewer.set_pixmap(QPixmap(test_img))  # создаём QPixmap и устанавливаем в QGraphicView

        layout.addWidget(button)

    @Slot()
    def show_info(self):
        if self.tb_info_dataset.isChecked():
            self.top_dock.setHidden(False)
        else:
            self.top_dock.setHidden(True)

    def open_image(self, image_name):  # загрузить изображение
        self.image_viewer.set_pixmap(QPixmap(image_name))
        self.image_viewer.fitInView(self.image_viewer.pixmap_item, Qt.KeepAspectRatio)

    def setup_files_and_labels(self):
        # Настройка правого (по умолчанию) виджета для отображения перечня файлов датасета
        self.files_list = QListWidget()
        self.files_search = QLineEdit()  # строка поиска файлов
        self.files_search.setPlaceholderText("Search files")
        # self.fileSearch.textChanged.connect(self.fileSearchChanged)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        # right_layout.addWidget(QLabel("Dataset/dir files:"))
        right_layout.addWidget(self.files_search)
        right_layout.addWidget(self.files_list)
        file_list_widget = QWidget()
        file_list_widget.setLayout(right_layout)
        self.files_dock = QDockWidget("Files List")  # Контейнер для виджета QListWidget
        self.files_dock.setWidget(file_list_widget)  # устанавливаем виджет перечня файлов

        self.files_list.itemSelectionChanged.connect(self.file_selection_changed)  # выбора файла в QWidgetList
        # fileListLayout = QtWidgets.QVBoxLayout()

    def toggle_instruments(self):  # включить/выключить инструменты при загрузке данных
        if self.current_data and self.files_list.count() > 0:
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
        if isinstance(item, QAction) or isinstance(item, QToolButton):
            item.setEnabled(b)
        elif isinstance(item, tuple):  # если набор, то вызываем себя рекурсивно
            for obj in item:
                self.set_instrument(obj, b)

    def open_project(self):
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

    def open_last_data(self):  # загрузка последних использованных данных
        last_data = self.settings.read_last_load_data()
        if self.current_data == last_data:
            self.signal_message.emit("Текущие данные являются последними использованными")
            return
        if last_data and os.path.exists(last_data):
            self.open_dir(dir_path=last_data, no_dialog=True)  # загружаем данные без диалогов
            self.toggle_instruments()  # включаем/выключаем доступ к инструментам
        else:
            self.signal_message.emit("Использованные ранее данные отсутствуют")

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
            self.settings.write_last_dir(sel_dir)  # сохраняем последний добавленный каталог
            self.settings.write_last_load_data(sel_dir)  # сохраняем последние добавленные данные
            self.import_dir_images(sel_dir)  # импортируем изображения
            self.current_data = sel_dir
            self.set_dataset_info(sel_dir)  # обновляем информацию о датасете
            self.toggle_instruments()  # включаем/выключаем доступ к инструментам

    def set_dataset_info(self, path):
        # str = "%s - %s" % (index, name)
        str_info = "Каталог датасета: {}\nКоличество объектов: {}".format(path, str(self.files_list.count()))
        # print('Sum of {} and 2 is {}'.format(i, add_partials[i - 1](2)))
        self.label_info.setText(str_info)

    def import_dir_images(self, path, pattern=None, load=True):
        # self.actions.openNextImg.setEnabled(True)
        # self.actions.openPrevImg.setEnabled(True)
        # if not self.mayContinue() or not path:
        #     return
        # self.lastOpenDir = path
        # self.filename = None
        self.files_list.clear()  # очищаем перечень файлов
        filenames = self.search_for_images(path)
        for filename in filenames:
            item = QListWidgetItem(filename)
            self.files_list.addItem(item)
        # if pattern:
        #     try:
        #         filenames = [f for f in filenames if re.search(pattern, f)]
        #     except re.error:
        #         pass
        # for filename in filenames:
        #     # label_file = os.path.splitext(filename)[0] + ".json"
        #     # if self.output_dir:
        #     #    label_file_without_path = os.path.basename(label_file)
        #     #    label_file = os.path.join(self.output_dir, label_file_without_path)
        #     item = QListWidgetItem(filename)
        #     item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        #     # if QFile.exists(label_file) and LabelFile.is_label_file(label_file):
        #     #     item.setCheckState(Qt.Checked)
        #     # else:
        #     item.setCheckState(Qt.Unchecked)
        #     self.files_list.addItem(item)
        # self.openNextImg(load=load)

    def search_for_images(self, path):  # формирование перечня загружаемых изображений
        deep = self.settings.read_load_sub_dir()
        # используем только поддерживаемые QImageReader расширения
        types = [".%s" % fmt.data().decode().lower() for fmt in QImageReader.supportedImageFormats()]
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

    def file_selection_changed(self):  # метод смены файла
        items = self.files_list.selectedItems()
        if not items:
            return
        item = items[0]

        # if not self.mayContinue():
        #     return

        # currIndex = self.imageList.index(str(item.text()))
        # if currIndex < len(self.imageList):
        #     filename = self.imageList[currIndex]
        #     if filename:
        #         self.loadFile(filename)

    @property
    def image_list(self):  # перечень объектов в file_list (делаем методы класса доступными как атрибуты: @property)
        lst = []
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            lst.append(item.text())
        return lst

    def setup_toolbar(self):
        # Настройка Toolbar'a
        self.toolbar = QToolBar("Dataset viewer instruments")  # панель инструментов для просмотра датасетов
        self.toolbar.setIconSize(QSize(30, 30))
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

    def mdi_add_window(self):
        self.count = self.count + 1
        sub = QMdiSubWindow()
        sub.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # удалять окна при их закрытии
        sub.setWidget(QTextEdit())
        sub.setWindowTitle("subwindow" + str(self.count))
        self.mdi.addSubWindow(sub)
        sub.show()
        self.mdi_show_sub_windows()

    def mdi_windows_4x(self):
        self.mdi_set_windows(4)

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

    def mdi_shuffle(self):
        pass

    def mdi_show_sub_windows(self):
        if self.actions_adjust[2].isChecked():  # не следить за расположением
            return
        elif self.actions_adjust[0].isChecked():  # установлен режим Tiled
            self.mdi.tileSubWindows()
        elif self.actions_adjust[1].isChecked():  # установлен режим Cascade
            self.mdi.cascadeSubWindows()

    def move_image(self, to_right: bool = True):
        if self.files_list.count() <= 1:
            return
        index = self.files_list.index(self.files_list)
        if not to_right:
            if index - 1 >= 0:
                filename = self.files_list[index - 1]
        else:
            if index + 1 < len(self.files_list):
                filename = self.files_list[index + 1]
        print("load!")
        self.loadFile(filename)

    def move_image_right(self):
        self.move_image(True)

    def move_image_left(self):
        self.move_image(False)

    def setup_actions(self):
        # Actions
        self.act_info = AzAction("Dataset information", "glyph_info", the_color2, the_color)  # информация о датасете

        # Действия для загрузки данных
        self.actions_load = (
            QAction(coloring_icon("glyph_folder_recent", the_color), "Load last data", triggered=self.open_last_data),
            QAction(coloring_icon("glyph_folder_clear", the_color), "Load dir", triggered=self.open_dir),
            # загрузить каталог
            QAction(coloring_icon("glyph_folder_dataset", the_color), "Load dataset", triggered=self.open_project))
        self.action_load_presets = QAction(coloring_icon("glyph_folder_preset", the_color), "Load preset dataset")
        self.tb_load_preset = QToolButton()  # кнопка загрузки предустановленных датасетов
        self.tb_load_preset.setText("Load preset dataset")
        self.tb_load_preset.setIcon(coloring_icon('glyph_folder_preset', the_color))
        self.tb_load_preset.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)  # со всплывающим меню

        self.tb_info_dataset = QToolButton()  # кнопка информации о датасете
        self.tb_info_dataset.setText(" Info")
        self.tb_info_dataset.setIcon(coloring_icon("glyph_info", the_color))
        self.tb_info_dataset.setCheckable(True)

        self.tb_info_dataset.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # self.tb_load_preset.addActions(self.actions_load)

        # Действия для отображения загруженных данных из датасетов (картинок)
        self.actions_show_data = (
            QAction(coloring_icon("glyph_image", the_color), "One window", triggered=self.mdi_windows_1x),
            QAction(coloring_icon("glyph_add_image", the_color), "Add window", triggered=self.mdi_add_window),
            QAction(coloring_icon("glyph_image_4x", the_color), "4x windows", triggered=self.mdi_windows_4x),
            QAction(coloring_icon("glyph_image_16x", the_color), "16x windows", triggered=self.mdi_windows_16x))

        # Действия для расположения окон QMdiSubWindow()
        self.actions_adjust = (
            QAction(coloring_icon("glyph_lay_tiled", the_color), "Tiled", triggered=self.mdi_show_sub_windows),
            QAction(coloring_icon("glyph_lay_cascade", the_color), "Cascade", triggered=self.mdi_show_sub_windows),
            QAction(coloring_icon("glyph_lay_off", the_color), "Disable layout", triggered=self.mdi_show_sub_windows))

        action_group_adjust = QActionGroup(self)  # объединяем в группу для расположения каскадом, мозаикой или выкл.
        for action in self.actions_adjust:
            action.setCheckable(True)
            action_group_adjust.addAction(action)  # соединяем действия боковой панели в группу
        self.actions_adjust[0].setChecked(True)  # включаем по умолчанию каскадом

        # Действия для меток и имён
        self.actions_labels = (
            QAction(coloring_icon("glyph_label", the_color), "Show labels"),
            QAction(coloring_icon("glyph_signature", the_color), "Show filenames"))
        for action in self.actions_labels:
            action.setCheckable(True)

        self.actions_control_images = (
            QAction(coloring_icon("glyph_left_arrow", the_color), "Preview", triggered=self.move_image_left),
            QAction(coloring_icon("glyph_right_arrow", the_color), "Next", triggered=self.move_image_right))

        self.action_shuffle_data = QAction(coloring_icon("glyph_dice", the_color), "Shuffle data",
                                           triggered=self.mdi_shuffle)  # отображаемые данные

# Отображение картинок, текста и проч. - было добавлено в init
# test_img = os.path.join(current_folder, "..", "test.jpg")
# scene = QGraphicsScene()  # Создание графической сцены
# graphicView = QGraphicsView(scene)  # Создание инструмента для отрисовки графической сцены
# graphicView.setGeometry(200, 220, 400, 400)  # Задание местоположения и размера графической сцены
# picture = QPixmap(test_img)  # Создание объекта QPixmap
# image_container = QGraphicsPixmapItem()  # Создание "пустого" объекта QGraphicsPixmapItem
# image_container.setPixmap(picture)  # Задание изображения в объект QGraphicsPixmapItem
# image_container.setOffset(0, 0)  # Позиция объекта QGraphicsPixmapItem
# # Добавление объекта QGraphicsPixmapItem на сцену
# scene.addItem(image_container)
#
# # Создание объекта QGraphicsSimpleTextItem
# text = QGraphicsSimpleTextItem('Пример текста')
# # text.setX(0) # Задание позиции текста
# # text.setY(200)
# scene.addItem(text)  # Добавление текста на сцену
# layout.addWidget(graphicView)
