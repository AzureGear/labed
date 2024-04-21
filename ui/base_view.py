from qdarktheme.qtpy.QtCore import Qt, QSize, pyqtSignal, Slot, QFile
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication, QMessageBox, QToolBar, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QGraphicsSimpleTextItem, QAction, QListWidget, QMdiArea, QMdiSubWindow, QActionGroup, QFileDialog, QListWidgetItem
from qdarktheme.qtpy.QtGui import QPixmap, QImageReader
from utils import AppSettings, UI_COLORS, UI_BASE_VIEW
from ui import AzButtonLineEdit, AzImageViewer, AzAction, coloring_icon, AzFileDialog
import os
import re
#import natsort

the_color = UI_COLORS.get("datasets_color")
the_color2 = UI_COLORS.get("datasets_change_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class ViewDatasetUI(QWidget):
    """
    Класс виджета просмотра датасетов
    """

    def __init__(self, parent):
        super().__init__()
        self.count = 0
        self.settings = AppSettings()  # настройки программы
        self.setup_actions()  # настраиваем QActions
        self.setup_toolbar()  # настраиваем Toolbar
        self.setup_files_and_labels()  # Настраиваем левую область: файлы, метки

        main_win = QMainWindow()  # главное окно виджетов

        self.image_viewer = AzImageViewer()  # класс QGraphicView, который предназначен для отрисовки графической сцены
        self.top_dock = QDockWidget("")  # контейнер для информации о датасете
        self.top_dock.setWidget(self.label_info)  # устанавливаем в контейнер QLabel
        self.tb_info_dataset.clicked.connect(self.show_info)

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

        main_win.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.top_dock)
        main_win.addToolBar(self.toolbar)
        main_win.addDockWidget(Qt.RightDockWidgetArea, self.files_dock)

        self.mdi = QMdiArea()
        self.mdi.tileSubWindows()
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
        print("triggered")
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

    def open_dir(self, _value=False, dirpath=None):  # загрузить каталог изображений
        last_dir = self.settings.read_last_dir()  # вспоминаем прошлый открытый каталог
        using_folder = current_folder
        if last_dir and os.path.exists(last_dir):
            using_folder = last_dir
        sel_dir = AzFileDialog(self, "Select directory to load images", last_dir, True)
        if sel_dir:
            self.settings.write_last_dir(sel_dir)
            self.importDirImages(sel_dir)

    def importDirImages(self, dirpath, pattern=None, load=True):
        # self.actions.openNextImg.setEnabled(True)
        # self.actions.openPrevImg.setEnabled(True)

        # if not self.mayContinue() or not dirpath:
        #     return
        # self.lastOpenDir = dirpath
        self.filename = None
        self.files_list.clear()  # очищаем перечень файлов

        filenames = self.scanAllImages(dirpath)
        if pattern:
            try:
                filenames = [f for f in filenames if re.search(pattern, f)]
            except re.error:
                pass
        for filename in filenames:
            #label_file = os.path.splitext(filename)[0] + ".json"
            #if self.output_dir:
            #    label_file_without_path = os.path.basename(label_file)
            #    label_file = os.path.join(self.output_dir, label_file_without_path)
            item = QListWidgetItem(filename)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            # if QFile.exists(label_file) and LabelFile.is_label_file(label_file):
            #     item.setCheckState(Qt.Checked)
            # else:
            item.setCheckState(Qt.Unchecked)
            self.files_list.addItem(item)
        #self.openNextImg(load=load)

    def scanAllImages(self, folderPath):
        extensions = [
            ".%s" % fmt.data().decode().lower()
            for fmt in QImageReader.supportedImageFormats()
        ]

        images = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.normpath(os.path.join(root, file))
                    images.append(relativePath)
        #images = natsort.os_sorted(images)
        return images


    def file_selection_changed(self):  # метод смены файла
        items = self.files_list.selectedItems()
        if not items:
            return
        item = items[0]

        if not self.mayContinue():
            return

        currIndex = self.imageList.index(str(item.text()))
        if currIndex < len(self.imageList):
            filename = self.imageList[currIndex]
            if filename:
                self.loadFile(filename)

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
        self.toolbar.addAction(self.action_shuffle_data)

        self.label_info = QLabel("Dataset information:")  # за отображение информации будет отвечать QLable
        self.label_info.setWordWrap(True)  # устанавливаем перенос по словам

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
        print(len(self.mdi.subWindowList()))
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

    def setup_actions(self):
        # Actions
        self.act_info = AzAction("Dataset information", "glyph_info", the_color2, the_color)  # информация о датасете

        # Действия для загрузки данных
        self.actions_load = (QAction(coloring_icon("glyph_folder_recent", the_color), "Load last data"),
                             QAction(coloring_icon("glyph_folder_clear", the_color), "Load dir",
                                     triggered=self.open_dir),  # загрузить каталог
                             QAction(coloring_icon("glyph_folder_dataset", the_color), "Load dataset"))
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

        self.action_shuffle_data = QAction(coloring_icon("glyph_dice", the_color), "Shuffle data",
                                           triggered=self.mdi_shuffle)  # отображаемые данные


#######################################################################

"""Module setting up ui of mdi window."""
# def _make_mdi_area_test_widget(self, enable_tab_mode=False):
#     # Widgets
#     container = QWidget()
#     mdi_area = QMdiArea()
#     label_test_name = QLabel()
#     cascade_button = QPushButton("Cascade")
#     new_button = QPushButton("Add new")
#     tiled_button = QPushButton("Tiled")
#
#     # Setup widgets
#     if enable_tab_mode:
#         mdi_area.setViewMode(QMdiArea.ViewMode.TabbedView)
#         label_test_name.setText("QMdiArea(QMdiArea.viewMode = TabbedView)")
#     else:
#         label_test_name.setText("QMdiArea(QMdiArea.viewMode = SubWindowView)")
#
#     def add_new_sub_window():
#         sub_win = QMdiSubWindow(container)
#         sub_win_main_widget = QWidget(sub_win)
#         v_layout = QVBoxLayout(sub_win_main_widget)
#         v_layout.addWidget(QTextEdit("Sub window"))
#
#         sub_win.setWidget(sub_win_main_widget)
#         mdi_area.addSubWindow(sub_win)
#         sub_win.show()
#
#     add_new_sub_window()
#     new_button.pressed.connect(add_new_sub_window)
#     cascade_button.pressed.connect(mdi_area.cascadeSubWindows)
#     tiled_button.pressed.connect(mdi_area.tileSubWindows)
#     new_button.setDefault(True)
#
#     # Layout
#     h_layout = QHBoxLayout()
#     h_layout.addWidget(new_button)
#     h_layout.addWidget(cascade_button)
#     h_layout.addWidget(tiled_button)
#
#     v_main_layout = QVBoxLayout(container)
#     v_main_layout.addWidget(label_test_name)
#     v_main_layout.addLayout(h_layout)
#     v_main_layout.addWidget(mdi_area)
#     return container
#
# def setup_ui(self, win: QWidget) -> None:
#     """Set up ui."""
#     # Widgets
#     splitter = QSplitter()
#
#     # Setup widgets
#     mdi_area = self._make_mdi_area_test_widget()
#     mdi_area_with_tab = self._make_mdi_area_test_widget(enable_tab_mode=True)
#
#     # Layout
#     splitter.addWidget(mdi_area)
#     splitter.addWidget(mdi_area_with_tab)
#
#     main_layout = QVBoxLayout(win)
#     main_layout.addWidget(splitter)


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
