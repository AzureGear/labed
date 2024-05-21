from qdarktheme.qtpy import QtCore
from qdarktheme.qtpy import QtWidgets
from qdarktheme.qtpy import QtGui
from utils import AppSettings, convert_to_sama, UI_COLORS, UI_OUTPUT_TYPES, UI_READ_LINES, dn_crop
from ui import coloring_icon, AzFileDialog, natural_order, AzButtonLineEdit, AzSpinBox, _TableModel, AzTableModel
from datetime import datetime
import os

the_color = UI_COLORS.get("processing_color")
the_color_side = UI_COLORS.get("sidepanel_color")
current_folder = os.path.dirname(os.path.abspath(__file__))


class ProcessingUI(QtWidgets.QWidget):
    """
    Класс виджета обработки датасетов
    """
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        layout = QtWidgets.QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу
        self.tab_widget = QtWidgets.QTabWidget()  # виджет со вкладками-страницами обработки
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))
        self.tab_widget.currentChanged.connect(self.change_tab)
        layout.addWidget(self.tab_widget)  # добавляем виджет со вкладками в расположение

        # Создание и настройка перечня виджетов-вкладок
        self.tab_merge_setup()  # "Слияние"
        self.tab_slicing_setup()  # "Нарезка"
        self.tab_attributes_setup()  # "Атрибуты"
        self.tab_geometry_setup()  # "Геометрия"

        ui_summ = [  # перечень: QWidget, "имя вкладки", "имя иконки", "подсказка"
            [self.ui_tab_merge, "Merge", "glyph_merge", "Объединение файлов разметки в формат SAMA"],  # "Слияние"
            [self.ui_tab_slicing, "Slicing", "glyph_cutter", "Нарезка снимков заданного размера"],  # "Нарезка"
            [self.ui_tab_attributes, "Attributes", "glyph_search-file",
             "Поиск и редактирование снимков по атрибутам разметки"],  # "Атрибуты"
            [self.ui_tab_geometry, "Geometry", "glyph_transform", "Изменение геометрии разметки"]]  # "Геометрия"

        for i, elem in enumerate(ui_summ):
            self.tab_widget.addTab(elem[0], coloring_icon(elem[2], the_color_side), elem[1])  # виджет, иконка, название
            # print("added tab: " + self.tab_widget.tabText(i))
            self.tab_widget.setTabToolTip(i, elem[3])

    def change_tab(self):
        pass
        # print(str(self.tab_widget.currentIndex()))

    def tab_merge_setup(self):  # настройка страницы "Слияние"
        self.ui_tab_merge = self.tab_basic_setup(complex=True)  # создаём "сложный" виджет
        # Действия для страницы
        self.merge_actions = (
            QtGui.QAction(coloring_icon("glyph_add", the_color), "Add files", triggered=self.merge_add_files),
            QtGui.QAction(coloring_icon("glyph_delete3", the_color), "Remove files",
                          triggered=self.merge_remove_files),
            QtGui.QAction(coloring_icon("glyph_check_all", the_color), "Select all",
                          triggered=self.merge_select_all),
            QtGui.QAction(coloring_icon("glyph_delete2", the_color), "Clear list", triggered=self.merge_clear),
            QtGui.QAction(coloring_icon("glyph_merge", the_color), "Merge selected files",
                          triggered=self.merge_combine),
            QtGui.QAction(coloring_icon("glyph_folder_clear", the_color), "Open output dir",
                          triggered=self.merge_open_output))
        self.merge_output_label = QtWidgets.QLabel("Output type:")
        self.merge_output_list = QtWidgets.QComboBox()  # список выходных данных
        self.merge_output_list.addItems(UI_OUTPUT_TYPES)  # перечень вариантов для списка
        self.merge_files_list = QtWidgets.QListWidget()  # перечень добавляемых файлов
        self.merge_files_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.merge_preview_data = QtWidgets.QScrollArea()  # контейнер для предпросмоторщика файлов
        self.merge_preview_data.setWidgetResizable(True)
        self.merge_label = QtWidgets.QLabel()  # предпросмоторщик файлов
        self.merge_preview_data.setWidget(self.merge_label)
        # self.merge_preview_data.setWidget(self.merge_label)
        split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)  # создаём разделитель
        split.addWidget(self.merge_files_list)  # куда помещаем перечень файлов...
        split.addWidget(self.merge_preview_data)  # ...и просмоторщик этих файлов
        split.setChildrenCollapsible(False)  # отключаем полное сворачивание виджетов внутри разделителя
        split.setSizes((90, 30))
        self.merge_files_list.itemSelectionChanged.connect(self.merge_selection_files_change)

        self.merge_output_tb = QtWidgets.QToolButton()  # выходной путь; по нажатии меняется на выбранный пользователем
        self.merge_output_tb.setCheckable(True)  # кнопка "нажимательная"
        self.merge_output_tb.setText("Каталог по умолчанию:" + "\n" + self.settings.read_default_output_dir())
        self.merge_output_tb.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)  # только текст от кнопки
        self.merge_output_tb.toggled.connect(self.merge_output_tb_toggled)  # связываем с методом смены каталога
        self.merge_output_dir = self.settings.read_default_output_dir()  # устанавливаем выходной каталог

        # Настройка панели инструментов
        self.merge_toolbar = QtWidgets.QToolBar("Toolbar for merging project files")  # панель инструментов для слияния
        self.merge_toolbar.setIconSize(QtCore.QSize(30, 30))
        self.merge_toolbar.setFloatable(False)
        self.merge_toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        self.merge_toolbar.addAction(self.merge_actions[0])  # добавить
        self.merge_toolbar.addAction(self.merge_actions[1])  # удалить
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addAction(self.merge_actions[2])  # добавить всё
        self.merge_toolbar.addAction(self.merge_actions[3])  # очистить
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addWidget(self.merge_output_label)
        self.merge_toolbar.addWidget(self.merge_output_list)  # выходной тип
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addAction(self.merge_actions[4])  # объединить проекты и конвертировать
        self.merge_toolbar.addSeparator()
        self.merge_toolbar.addWidget(self.merge_output_tb)
        self.merge_toolbar.addAction(self.merge_actions[5])  # открыть выходной каталог

        vlayout = QtWidgets.QVBoxLayout()  # контейнер QVBoxLayout()
        vlayout.addWidget(split)  # добавляем область с разделением
        wid = QtWidgets.QWidget()  # создаём виджет-контейнер...
        wid.setLayout(vlayout)  # ...куда помещаем vlayout (поскольку Central Widget может быть только QWidget)
        self.ui_tab_merge.addToolBar(self.merge_toolbar)  # добавляем панель меню
        self.ui_tab_merge.setCentralWidget(wid)  # устанавливаем главный виджет страницы "Слияние"
        self.merge_toggle_instruments()

    def merge_cust_path_box_toggled(self):
        if not self.merge_cust_path_box.isChecked():
            self.merge_output_line.setText(self.settings.read_default_output_dir())

    def merge_selection_files_change(self):  # загрузка данных *.json в предпросмотр
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)  # ставим курсор ожидание
        try:
            if self.merge_files_list.count() > 0:  # количество объектов больше 0
                if self.merge_files_list.currentItem() is not None:
                    file = self.merge_files_list.currentItem().text()  # считываем текущую строку
                    if os.path.exists(file):
                        with open(file, "r") as f:
                            data = [file + ":\n\n"]  # лист для данных из файла
                            for i in range(0, int(UI_READ_LINES)):  # читаем только первые несколько строк...
                                data.append(f.readline())  # ...поскольку файлы могут быть большими
                            data.append("...")
                            self.merge_label.setText(("".join(data)))  # объединяем лист в строку
                            self.merge_label.setAlignment(
                                QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)  # выравниваем надпись
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.merge_toggle_instruments()

    def tab_slicing_setup(self):  # настройка страницы "Нарезка"
        self.ui_tab_slicing = self.tab_basic_setup(complex=True)
        self.pb2 = QtWidgets.QPushButton("Manual Visual Slice Process")
        split = QtWidgets.QSplitter(QtCore.Qt.Vertical)  # вертикальный разделитель
        slice_auto_form = QtWidgets.QFormLayout()  # форма для расположения виджетов "автоматического разрезания"
        self.slice_input_file_label = QtWidgets.QLabel("Path to file project *.json:")  # метка исходного файла
        self.slice_input_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                      caption="Select project file to auto slicing",
                                                      read_only=True, dir_only=False, filter="Projects files (*.json)",
                                                      on_button_clicked_callback=self.slice_load_projects_data,
                                                      initial_filter="json (*.json)")
        self.slice_input_file_path.setText(self.settings.read_slicing_input())  # строка для исходного файла
        self.slice_input_file_path.textChanged.connect(
            lambda: self.settings.write_slicing_input(self.slice_input_file_path.text()))  # автосохранение
        self.slice_output_file_check = QtWidgets.QCheckBox("Set user output file path other than default:")
        self.slice_output_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                       caption="Output file",
                                                       read_only=True, dir_only=True)
        # regexp = QtCore.QRegExp(r'^[[:ascii:]]+$')  # проверка имени файла на символы
        # validator = QtGui.QRegExpValidator(regexp, self.slice_output_file_path)  # создаём валидатор
        # self.slice_output_file_path.setValidator(validator)  # применяем его к нашей строке
        self.slice_scan_size_label = QtWidgets.QLabel("Scan size:")  # метка для сканирующего окна
        self.slice_scan_size = AzSpinBox(min_val=8, min_wide=70, suffix=" pix")  # размер сканирующего окна;
        self.slice_overlap_window_label = QtWidgets.QLabel("Scanning window overlap percentage:")
        # процент перекрытия окна для смежных кадров:
        self.slice_overlap_window = AzSpinBox(min_val=0, max_val=95, step=1, max_start_val=False, start_val=5)
        self.slice_overlap_pols_default_label = QtWidgets.QLabel("Default overlap percentage for classes:")
        current_overlap_pols_default = self.settings.read_default_slice_overlap_pols()
        self.slice_overlap_pols_default = AzSpinBox(min_val=0, max_val=95, step=1, max_start_val=False,
                                                    start_val=current_overlap_pols_default)
        self.slice_overlap_pols_default.valueChanged.connect(self.slice_write_default_overlap_pols)
        self.slice_output_file_path.setEnabled(False)
        self.slice_output_file_check.clicked.connect(self.slice_toggle_output_file)  # соединяем - требуется настройка
        self.slice_output_file_path.setText(self.settings.read_default_output_dir())  # строка для выходного файла
        self.slice_exec = QtWidgets.QPushButton(" Slice images")
        self.slice_exec.setIcon(coloring_icon("glyph_cutter", the_color))
        self.slice_exec.clicked.connect(self.slice_exec_run)  # соединение с процедурой разрезания
        self.slice_open_result = QtWidgets.QPushButton(" Open results")
        self.slice_open_result.setIcon(coloring_icon("glyph_folder_clear", the_color))
        self.slice_open_result.clicked.connect(lambda: os.startfile(self.slice_output_file_path.text()))
        self.slice_overlap_pols = 0  # какой процент площади полигонов надо перекрыть окном
        h_widgets = [self.slice_scan_size_label, self.slice_scan_size, self.slice_overlap_window_label,
                     self.slice_overlap_window, self.slice_overlap_pols_default_label,
                     self.slice_overlap_pols_default]  # группа вертикальных виджетов для параметров авто разрезания

        hor_sett_layout = QtWidgets.QHBoxLayout()  # расположение для параметров автоматизированной обработки
        for i, wdt in enumerate(h_widgets):
            hor_sett_layout.addWidget(wdt)
            if i % 2 == 1:  # Выбираем только нечётные, т.е. 0-нет, 1-да и т.д.
                hor_sett_layout.addStretch(20)
        self.slice_tab_labels = QtWidgets.QTableView()  # Создаём объект табличного просмотра
        self.slice_tab_labels.setSortingEnabled(False)  # отключаем сортировку, т.к. для Денисова класса важен порядок
        self.slice_tab_labels.setAlternatingRowColors(True)  # устанавливаем чередование цветов строк таблицы

        slice_auto_form.addRow(self.slice_input_file_label, self.slice_input_file_path)  # строка "исходный файл"
        slice_auto_form.addRow(self.slice_output_file_check, self.slice_output_file_path)  # строка "выходной файл"
        slice_auto_form.addRow(hor_sett_layout)  # строка "настройки автоматизированной обработки"
        slice_auto_form.addRow(self.slice_tab_labels)

        slice_auto_form.addRow(self.slice_open_result, self.slice_exec)
        up_widget = QtWidgets.QWidget()  # верхний виджет - автоматизированная обработка
        up_widget.setLayout(slice_auto_form)
        split.addWidget(up_widget)
        split.addWidget(self.pb2)  # нижний виджет - ручная обработка
        split.setChildrenCollapsible(True)  # включаем полное сворачивание виджетов внутри разделителя
        split.setSizes((10, 120))
        vlayout = QtWidgets.QVBoxLayout()  # контейнер QVBoxLayout()
        vlayout.addWidget(split)  # добавляем область с разделением
        wid = QtWidgets.QWidget()  # создаём виджет-контейнер...
        wid.setLayout(vlayout)  # ...куда помещаем vlayout (поскольку Central Widget может быть только QWidget)
        self.ui_tab_slicing.setCentralWidget(wid)

        # проверяем есть ли сохранённый ранее файл проекта, и загружаем его автоматически
        if len(self.slice_input_file_path.text()) > 0:
            self.slice_load_projects_data()

    def slice_exec_run(self):  # процедура разрезания
        pols_overlap_percent = []
        model = self.slice_tab_labels.model()
        for row in range(model.rowCount(-198)):  # -198 чтобы тебя запутать))
            # процент указан во втором столбце, роль "Редактирования" включает "Отображение"
            pols_overlap_percent.append((model.data(model.index(row, 1), QtCore.Qt.ItemDataRole.DisplayRole)) / 100)
        print(pols_overlap_percent)
        cut_settings = []  # выбранные параметры разрезания
        cut_settings.append(self.slice_scan_size.value())  # размер сканирующего окна
        cut_settings.append(pols_overlap_percent)
        cut_settings.append(self.slice_overlap_window.value() / 100)
        new_name = os.path.join(self.slice_output_file_path.text(),
                                "sliced_%s.json" % datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
        cut_settings.append(new_name)
        print(cut_settings)
        # ImgCutObj = dn_crop.DNImgCut(PathData, JsonNameFile)
        # ImgCutObj.CutAllImgs(1280, [0.5, 0.5, 0.5, 0.5, 0.5, 0.5], 0.5, 'res.json')

    def slice_load_projects_data(self):  # загрузка файла проекта
        self.json_obj = dn_crop.DNjson(self.slice_input_file_path.text())  # Файл проекта, реализация Дениса
        if not self.json_obj.good_file:
            self.signal_message.emit("Выбранный файл не является корректным либо не содержит необходимых данных")
            self.slice_exec.setEnabled(False)  # отключаем возможность Разрезать
            return
        self.slice_exec.setEnabled(True)
        model_data = []  # данные для отображения
        for label in self.json_obj.labels:
            # [наменование метки, процент перекрытия]
            model_data.append([label, int(self.slice_overlap_pols_default.text())])
        self.slice_tab_labels.setModel(
            AzTableModel(model_data, header_data=["Наименование класса (метки)", "Процент перекрытия"], edit_column=1))
        header = self.slice_tab_labels.horizontalHeader()  # настраиваем отображение столбцов
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    def slice_write_default_overlap_pols(self):
        self.settings.write_default_slice_overlap_pols(self.slice_overlap_pols_default.value())

    def slice_toggle_output_file(self):
        self.slice_output_file_path.setEnabled(self.slice_output_file_check.checkState())
        if not self.slice_output_file_check.isChecked():
            self.slice_output_file_path.setText(self.settings.read_default_output_dir())

    def tab_attributes_setup(self):  # настройка страницы "Атрибуты"
        self.ui_tab_attributes = self.tab_basic_setup()

    def tab_geometry_setup(self):  # настройка страницы "Геометрия"
        self.ui_tab_geometry = self.tab_basic_setup()

    def merge_toggle_instruments(self):  # включает/отключает инструменты
        # сначала всё отключим по умолчанию
        self.merge_actions[1].setEnabled(False)
        self.merge_actions[2].setEnabled(False)
        self.merge_actions[3].setEnabled(False)
        self.merge_actions[4].setEnabled(False)
        if self.merge_files_list.count() > 0:
            self.merge_actions[2].setEnabled(True)  # включаем кнопку "очистить список"
            self.merge_actions[3].setEnabled(True)  # включаем кнопку "выделить всё"
        if len(self.merge_files_list.selectedItems()) > 0:  # имеются выбранные файлы
            self.merge_actions[1].setEnabled(True)  # включаем кнопку "удалить выбранные"
            if len(self.merge_files_list.selectedItems()) > 1:  # выбрано более 2х файлов
                self.merge_actions[4].setEnabled(True)

    def tab_basic_setup(self, complex=False):  # базовая настройка каждой страницы QTabWidget
        if complex:
            widget = QtWidgets.QMainWindow()
        else:
            widget = QtWidgets.QWidget()
            widget.layout = QtWidgets.QVBoxLayout(widget)  # не забываем указать ссылку на объект
        return widget

    def merge_add_files(self):
        sel_files = AzFileDialog(self, "Select project files to add", self.settings.read_last_dir(), False,
                                 filter="LabelMe projects (*.json)", initial_filter="json (*.json)")
        if sel_files:
            self.merge_fill_files(sel_files)
            self.merge_toggle_instruments()

    def merge_fill_files(self, filenames):
        for filename in filenames:
            item = QtWidgets.QListWidgetItem(filename)
            self.merge_files_list.addItem(item)

    def merge_remove_files(self):
        sel_items = self.merge_files_list.selectedItems()
        if len(sel_items) <= 0:
            return
        for item in sel_items:
            self.merge_files_list.takeItem(self.merge_files_list.row(item))  # удаляем выделенные объекты
        self.merge_toggle_instruments()
        if self.merge_files_list.count() <= 0:
            self.merge_label.setText("")

    def merge_clear(self):
        self.merge_files_list.clear()
        self.merge_toggle_instruments()
        if self.merge_files_list.count() <= 0:
            self.merge_label.setText("")

    def merge_combine(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)  # ставим курсор ожидание
        try:
            sel_items = self.merge_files_list.selectedItems()
            data = []
            for item in sel_items:
                if os.path.exists(item.text()):
                    data.append(item.text())
            unique = list(set(data))
            unique = sorted(unique, key=natural_order)
            if len(unique) <= 1:
                self.signal_message.emit("Выбраны дубликаты")
                return
            new_name = os.path.join(self.merge_output_dir,
                                    "converted_%s.json" % datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))

            if convert_to_sama(unique, new_name):
                self.merge_files_list.clearSelection()
                self.signal_message.emit("Файлы успешно объединены и конвертированы")
            else:
                self.signal_message.emit("Ошибка при конвертации данных. Проверьте исходные файлы.")
            # метод возвращающий True|False в зависимости от успеха
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def merge_select_all(self):
        self.merge_files_list.selectAll()

    def merge_open_output(self):
        os.startfile(self.merge_output_dir)  # открываем каталог средствами системы

    def merge_output_tb_toggled(self):  # настройка выходных данных
        if not self.merge_output_tb.isChecked():  # кнопка не нажата - значит каталог по умолчанию
            self.merge_output_dir = self.settings.read_default_output_dir()
            self.merge_output_tb.setText("Каталог по умолчанию" + "\n" + self.settings.read_default_output_dir())
        else:  # кнопка нажата - пробуем установить каталог пользователя
            last_dir = self.settings.read_default_output_dir()  # последний открытый каталог
            if not os.path.exists(last_dir):
                last_dir = ""
            out_path = AzFileDialog(self, "Select directory for files to be merged", last_dir, True)  # диалог
            if out_path:
                self.merge_output_tb.setText("Каталог пользователя" + "\n" + out_path)
                self.merge_output_dir = out_path
            else:
                self.merge_output_tb.setChecked(False)  # если новый путь не выбран, возвращаем кнопку по умолчанию
