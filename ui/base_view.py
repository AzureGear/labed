from qdarktheme.qtpy.QtCore import Qt, QSize, pyqtSignal, Slot, QFile
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication, QMessageBox, QToolBar, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, \
    QGraphicsSimpleTextItem, QAction, QListWidget, QMdiArea, QMdiSubWindow, QActionGroup, QListWidgetItem, \
    QSizePolicy, QFileDialog, QAbstractItemView
from qdarktheme.qtpy.QtGui import QPixmap, QImageReader, QImage
from utils import AppSettings, UI_COLORS, UI_BASE_VIEW
from ui import AzImageViewer, AzAction, coloring_icon, AzFileDialog
import os
import re
import random


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
        self.current_data_list = []
        self.current_data_dir = ""
        self.current_file = None

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
        self.files_search.textChanged.connect(self.file_search_changed)
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
        if isinstance(item, QAction) or isinstance(item, QToolButton):
            item.setEnabled(b)
        elif isinstance(item, tuple):  # если набор, то вызываем себя рекурсивно
            for obj in item:
                self.set_instrument(obj, b)

    def open_project(self):  # загрузить датасет
        # classic
        students = ["Abid", "Natasha", "Nick", "Matthew", "Greetings", "Kramola", "Poeben"]
        pattern = "i."  # "N.*"
        filtered_students = [x for x in students if re.findall(pattern, x, re.IGNORECASE)]
        print(filtered_students)
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
        if self.current_data_dir == last_data:
            self.signal_message.emit("Текущие данные являются последними использованными")
            return
        if last_data and os.path.exists(last_data):
            self.open_dir(dir_path=last_data, no_dialog=True)  # загружаем данные без диалогов
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
            self.prepear_for_load()  # подготавливаем: закрываем SubWindows, очищаем все
            self.import_dir_images(sel_dir)  # импортируем изображения
            self.current_data_dir = sel_dir  # устанавливаем текущие данные
            self.set_dataset_info(sel_dir)  # обновляем информацию о датасете
            self.files_list.setCurrentRow(0)  # если первый раз открыли датасет - загружаем первое изображение
            self.mdi_add_window()  # добавляем окно
            self.toggle_instruments()  # включаем/выключаем доступ к инструментам
            # self.show_image()

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
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
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
            item = QListWidgetItem(filename)
            self.files_list.addItem(item)

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
            index = self.files_list.moveCursor(QAbstractItemView.MoveDown, Qt.NoModifier)
        else:  # ...или назад по списку
            index = self.files_list.moveCursor(QAbstractItemView.MoveUp, Qt.NoModifier)
        if index.isValid():  # проверяем валидность индекса
            self.files_list.setCurrentIndex(index)

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
        if self.current_file is None:
            self.signal_message.emit("Ошибка загрузки файла")
        sub = QMdiSubWindow()
        sub.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # удалять окна при их закрытии
        self.mdi_window_set_image(sub, self.current_file)
        self.mdi.addSubWindow(sub)
        sub.show()
        self.mdi_show_sub_windows()  # выравниваем

    def mdi_window_set_image(self, subwindow, image):  # загрузка снимка для отображения
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            image_viewer = AzImageViewer()  # формируем контейнер
            image_viewer.set_pixmap(QPixmap(image))  # помещаем туда изображение
            subwindow.setWidget(image_viewer)  # добавляем контейнер в окно QMdiSubWindow()
            subwindow.setWindowTitle(str(image))  # заголовок окна
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()

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

    def mdi_shuffle(self):  # загрузить случайные данные (перемешать)
        if len(self.mdi.subWindowList()) <= 0 or len(self.current_data_list) <= 0:
            return
        list_subs = self.mdi.subWindowList()
        for sub in list_subs:
            random_filename = random.choice(self.current_data_list)
            self.mdi_window_set_image(sub, random_filename)
        active_mdi = self.mdi.activeSubWindow()
        items = self.files_list.findItems(active_mdi.windowTitle(), Qt.MatchFlag.MatchExactly)
        if len(items) > 0:
            self.files_list.setCurrentItem(items[0])



    def mdi_show_sub_windows(self):
        if self.actions_adjust[2].isChecked():  # не следить за расположением
            return
        elif self.actions_adjust[0].isChecked():  # установлен режим Tiled
            self.mdi.tileSubWindows()
        elif self.actions_adjust[1].isChecked():  # установлен режим Cascade
            self.mdi.cascadeSubWindows()

        # return
        # index = None
        # if len(self.image_list) <= 0:  # если в списке оригинальных изображений 0 шт.
        #     return
        # if self.current_file is None:  # ни разу после загрузки датасета не выбирался файл
        #     # filename = self.image_list[0]  # значит ставим первый
        #     index = 0
        # else:
        #     if self.files_list.count() < 1:
        #         return  # в перечне файлов (с учётом фильтра) отсутствуют данные
        #     items = self.files_list.selectedItems()  # выбранные в перечне files_list объекты
        #     if not items:  # если не выбрано (с учётом фильтра), то выбираем первый отфильтрованный
        #         index = 0
        #     else:  # иначе пытаемся отобразить следующий/предыдущий
        #         if move_forward:  # движемся вперед...
        #             s_index = self.files_list.moveCursor(QAbstractItemView.MoveDown, Qt.NoModifier)
        #         else:  # ...или назад по списку
        #             s_index = self.files_list.moveCursor(QAbstractItemView.MoveUp, Qt.NoModifier)
        #         if s_index.isValid():  # проверяем валидность индекса
        #             self.files_list.setCurrentIndex(s_index)
        #             return
        # self.files_list.setCurrentRow(index)

    def move_image_right(self):
        self.files_step_image(True)

    def move_image_left(self):
        self.files_step_image(False)

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

        # Действия для отображения загруженных данных из датасетов (картинок) в окнах QMdiSubWindow()
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
            action_group_adjust.addAction(action)
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

    def load_file(self, filename=None):  # загрузить для отображения новый графический файл
        """Load the specified file, or the last opened file if None."""
        # changing fileListWidget loads file
        if filename is None:
            return
        self.current_file = filename
        active_mdi = self.mdi.activeSubWindow()
        curr_filename = self.files_list.item(self.files_list.currentRow()).text()  # выбранный в окне файлов объект
        # if curr_filename != self.current_file:  # переданный для загрузки файл имеет такое же имя
        #     # как и текущий файл в листе
        #     return

        # выбранный в окне файлов объект не загружен в активное окно и открыто хотя бы одно окно
        if active_mdi.windowTitle() != filename and len(self.mdi.subWindowList()) > 0:
            self.mdi_window_set_image(active_mdi, filename)
        # self.files_list.repaint()
        # return

    # print(filename)
    # return
    # self.resetState()
    # self.canvas.setEnabled(False)
    # if filename is None:
    #     filename = self.settings.value("filename", "")
    # filename = str(filename)
    # if not QFile.exists(filename):
    #     self.errorMessage(
    #         self.tr("Error opening file"),
    #         self.tr("No such file: <b>%s</b>") % filename,
    #     )
    #     return False
    # # assumes same name, but json extension
    # self.status(str(self.tr("Loading %s...")) % os.path.basename(str(filename)))
    # label_file = os.path.splitext(filename)[0] + ".json"
    # if self.output_dir:
    #     label_file_without_path = os.path.basename(label_file)
    #     label_file = os.path.join(self.output_dir, label_file_without_path)
    # if QFile.exists(label_file) and LabelFile.is_label_file(label_file):
    #     try:
    #         self.labelFile = LabelFile(label_file)
    #     except LabelFileError as e:
    #         self.errorMessage(
    #             self.tr("Error opening file"),
    #             self.tr(
    #                 "<p><b>%s</b></p>"
    #                 "<p>Make sure <i>%s</i> is a valid label file."
    #             )
    #             % (e, label_file),
    #         )
    #         self.status(self.tr("Error reading %s") % label_file)
    #         return False
    #     self.imageData = self.labelFile.imageData
    #     self.imagePath = os.path.join(
    #         os.path.dirname(label_file),
    #         self.labelFile.imagePath,
    #     )
    #     self.otherData = self.labelFile.otherData
    # else:
    #     self.imageData = LabelFile.load_image_file(filename)
    #     if self.imageData:
    #         self.imagePath = filename
    #     self.labelFile = None
    # image = QImage.fromData(self.imageData)
    #
    # if image.isNull():
    #     formats = [
    #         "*.{}".format(fmt.data().decode())
    #         for fmt in QtGui.QImageReader.supportedImageFormats()
    #     ]
    #     self.errorMessage(
    #         self.tr("Error opening file"),
    #         self.tr(
    #             "<p>Make sure <i>{0}</i> is a valid image file.<br/>"
    #             "Supported image formats: {1}</p>"
    #         ).format(filename, ",".join(formats)),
    #     )
    #     self.status(self.tr("Error reading %s") % filename)
    #     return False
    # self.image = image
    # self.filename = filename
    # if self._config["keep_prev"]:
    #     prev_shapes = self.canvas.shapes
    # self.canvas.loadPixmap(QPixmap.fromImage(image))
    # flags = {k: False for k in self._config["flags"] or []}
    # if self.labelFile:
    #     self.loadLabels(self.labelFile.shapes)
    #     if self.labelFile.flags is not None:
    #         flags.update(self.labelFile.flags)
    # self.loadFlags(flags)
    # if self._config["keep_prev"] and self.noShapes():
    #     self.loadShapes(prev_shapes, replace=False)
    #     self.setDirty()
    # else:
    #     self.setClean()
    # self.canvas.setEnabled(True)
    # # set zoom values
    # is_initial_load = not self.zoom_values
    # if self.filename in self.zoom_values:
    #     self.zoomMode = self.zoom_values[self.filename][0]
    #     self.setZoom(self.zoom_values[self.filename][1])
    # elif is_initial_load or not self._config["keep_prev_scale"]:
    #     self.adjustScale(initial=True)
    # # set scroll values
    # for orientation in self.scroll_values:
    #     if self.filename in self.scroll_values[orientation]:
    #         self.setScroll(
    #             orientation, self.scroll_values[orientation][self.filename]
    #         )
    # # set brightness contrast values
    # dialog = BrightnessContrastDialog(
    #     utils.img_data_to_pil(self.imageData),
    #     self.onNewBrightnessContrast,
    #     parent=self,
    # )
    # brightness, contrast = self.brightnessContrast_values.get(
    #     self.filename, (None, None)
    # )
    # if self._config["keep_prev_brightness"] and self.recentFiles:
    #     brightness, _ = self.brightnessContrast_values.get(
    #         self.recentFiles[0], (None, None)
    #     )
    # if self._config["keep_prev_contrast"] and self.recentFiles:
    #     _, contrast = self.brightnessContrast_values.get(
    #         self.recentFiles[0], (None, None)
    #     )
    # if brightness is not None:
    #     dialog.slider_brightness.setValue(brightness)
    # if contrast is not None:
    #     dialog.slider_contrast.setValue(contrast)
    # self.brightnessContrast_values[self.filename] = (brightness, contrast)
    # if brightness is not None or contrast is not None:
    #     dialog.onNewValue(None)
    # self.paintCanvas()
    # self.addRecentFile(self.filename)
    # self.toggleActions(True)
    # self.canvas.setFocus()
    # self.status(str(self.tr("Loaded %s")) % os.path.basename(str(filename)))
    # return True
