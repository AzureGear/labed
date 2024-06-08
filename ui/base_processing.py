from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import AppSettings, convert_to_sama, UI_COLORS, UI_OUTPUT_TYPES, UI_READ_LINES, dn_crop
from ui import new_act, new_button, coloring_icon, az_file_dialog, natural_order, AzButtonLineEdit, AzSpinBox, \
    AzTableModel, AzManualSlice
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
        self.merge_output_dir = ""
        layout = QtWidgets.QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        layout.setContentsMargins(5, 0, 5, 5)  # уменьшаем границу
        self.tab_widget = QtWidgets.QTabWidget()  # виджет со вкладками-страницами обработки
        self.tab_widget.setIconSize(QtCore.QSize(24, 24))
        layout.addWidget(self.tab_widget)  # добавляем виджет со вкладками в расположение

        # Матрешка виджетов
        # ProcessingUI(QWidget) - наш главный родительский контейнер
        #  └- layout - контейнер типа QVBoxLayout в котором хранится...
        #      └- tab_widget - ...виджет со вкладками, пока их 4: Слияние, Нарезка, Атрибуты, Геометрия.
        #          ├- ui_tab_merge - "Слияние", виджет типа QMainWindow()
        #          |   ├- toolbar - панель инструментов
        #          |   └- list... и др. виджеты
        #          ├- ui_tab_slicing - "Нарезка", виджет типа QMainWindow()
        #          |   └- CentralWidget - главный виджет класса QMainWindow()
        #          |       └- QVBoxLayout  - вертикальный контейнер
        #          |           ├- slice_caption_form - область с заголовочным расположением элементов
        #          |           └- split - разделитель QSplitter
        #          |               ├- self.slice_up_group - группа объектов верхнего разделителя (автоматизир. кадрир.)
        #          |               └- self.slice_down_group - группа объектов нижнего разделителя (ручное кадрирование)

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

        # Загрузка последней активной вкладки "Обработки"
        self.tab_widget.setCurrentIndex(self.settings.read_ui_proc_page())

        # Signals
        self.tab_widget.currentChanged.connect(self.change_tab)  # изменение вкладки

    @QtCore.pyqtSlot()
    def change_tab(self):  # сохранение последней активной вкладки "Обработки"
        self.settings.write_ui_proc_page(self.tab_widget.currentIndex())

    def tab_merge_setup(self):  # настройка страницы "Слияние"
        self.ui_tab_merge = self.tab_basic_setup(complex=True)  # создаём "сложный" виджет
        # Действия для страницы
        self.merge_actions = (
            new_act(self, "Add files", "glyph_add", the_color, self.merge_add_files),
            new_act(self, "Remove files", "glyph_delete3", the_color, self.merge_remove_files),
            new_act(self, "Select all", "glyph_check_all", the_color, self.merge_select_all),
            new_act(self, "Clear list", "glyph_delete2", the_color, self.merge_clear),
            new_act(self, "Merge selected files", "glyph_merge", the_color, self.merge_combine),
            new_act(self, "Open output dir", "glyph_folder_clear", the_color, self.merge_open_output))
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
        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)  # создаём разделитель
        split.addWidget(self.merge_files_list)  # куда помещаем перечень файлов...
        split.addWidget(self.merge_preview_data)  # ...и просмоторщик этих файлов
        split.setChildrenCollapsible(False)  # отключаем полное сворачивание виджетов внутри разделителя
        split.setSizes((90, 30))
        self.merge_files_list.itemSelectionChanged.connect(self.merge_selection_files_change)

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
        self.merge_toolbar.addAction(self.merge_actions[5])  # открыть выходной каталог

        # выходной каталог для Слияния
        hlayout = QtWidgets.QHBoxLayout()  # контейнер QHBoxLayout()
        self.merge_output_file_check = QtWidgets.QCheckBox("Set user output file path other than default:")
        self.merge_output_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                       caption="Output file",
                                                       read_only=True, dir_only=True)
        # соединяем, поскольку требуется изменять выходной каталог, в случае деактивации
        self.merge_output_file_check.clicked.connect(self.merge_toggle_output_file)
        # соединяем, чтобы записывать изменения в переменную.
        self.merge_output_file_path.textChanged.connect(self.merge_output_file_path_change)
        self.merge_output_file_path.setEnabled(False)  # Отключаем, т.е. по умолчанию флаг не включен
        self.merge_output_file_path.setText(self.settings.read_default_output_dir())  # устанавливаем выходной каталог
        hlayout.addWidget(self.merge_output_file_check)
        hlayout.addWidget(self.merge_output_file_path)

        # Собираем итоговую компоновку
        vlayout = QtWidgets.QVBoxLayout()  # контейнер QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(split)  # добавляем область с разделением
        wid = QtWidgets.QWidget()  # создаём виджет-контейнер...
        wid.setLayout(vlayout)  # ...куда помещаем vlayout (поскольку Central Widget может быть только QWidget)
        self.ui_tab_merge.addToolBar(self.merge_toolbar)  # добавляем панель меню
        self.ui_tab_merge.setCentralWidget(wid)  # устанавливаем главный виджет страницы "Слияние"
        self.merge_toggle_instruments()  # устанавливаем доступные инструменты

    @QtCore.pyqtSlot()
    def merge_output_file_path_change(self):
        self.merge_output_dir = self.merge_output_file_path.text()

    @QtCore.pyqtSlot()
    def merge_toggle_output_file(self):
        self.merge_output_file_path.setEnabled(self.merge_output_file_check.checkState())
        if not self.merge_output_file_check.isChecked():
            self.merge_output_file_path.setText(self.settings.read_default_output_dir())

    @QtCore.pyqtSlot()
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
        self.json_obj = None
        self.ui_tab_slicing = self.tab_basic_setup(complex=True)
        split = QtWidgets.QSplitter(QtCore.Qt.Vertical)  # вертикальный разделитель
        slice_auto_form = QtWidgets.QFormLayout()  # форма для расположения виджетов "автоматического разрезания"

        # 1 строка в форме Автоматизированного разрезания
        self.slice_input_file_label = QtWidgets.QLabel("Path to file project *.json:")  # метка исходного файла
        self.slice_input_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                      caption="Select project file to auto slicing",
                                                      read_only=True, dir_only=False, filter="Projects files (*.json)",
                                                      on_button_clicked_callback=self.slice_load_projects_data,
                                                      initial_filter="json (*.json)")
        self.slice_input_file_path.setText(self.settings.read_slicing_input())  # строка для исходного файла
        self.slice_input_file_path.textChanged.connect(
            lambda: self.settings.write_slicing_input(self.slice_input_file_path.text()))  # автосохранение

        # 2 строка в форме Автоматизированного разрезания
        self.slice_output_file_check = QtWidgets.QCheckBox("Set user output file path other than default:")
        self.slice_output_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                       caption="Output file",
                                                       read_only=True, dir_only=True)

        # 3 строка в форме Автоматизированного разрезания
        self.slice_scan_size_label = QtWidgets.QLabel("Scan size:")  # метка для сканирующего окна
        self.slice_scan_size = AzSpinBox(min_val=8, min_wide=53)  # размер сканирующего окна;
        self.slice_overlap_window_label = QtWidgets.QLabel("Scanning window overlap percentage:")

        # процент перекрытия окна для смежных кадров скользящего окна:
        self.slice_overlap_window = AzSpinBox(min_val=30, max_val=95, step=1, max_start_val=False,
                                              start_val=self.settings.read_slice_window_overlap())
        self.slice_overlap_window.valueChanged.connect(self.slice_write_overlap_window)
        self.slice_overlap_pols_default_label = QtWidgets.QLabel("Default overlap percentage for classes:")
        self.slice_overlap_pols_default = AzSpinBox(min_val=1, max_val=95, step=1, max_start_val=False,
                                                    start_val=self.settings.read_default_slice_overlap_pols())
        self.slice_overlap_pols_default.valueChanged.connect(self.slice_write_default_overlap_pols)

        # отступ полигонов от края снимка
        self.slice_edge_label = QtWidgets.QLabel("Offset from the edge")
        self.slice_edge = AzSpinBox(0, 1000, 1, False, start_val=0)

        # группа горизонтальных виджетов для параметров авто разрезания
        h_widgets = [self.slice_scan_size_label, self.slice_scan_size, self.slice_overlap_window_label,
                     self.slice_overlap_window, self.slice_overlap_pols_default_label,
                     self.slice_overlap_pols_default, self.slice_edge_label, self.slice_edge]
        hor_sett_layout = QtWidgets.QHBoxLayout()  # расположение для параметров автоматизированной обработки
        fill_layout_by_widgets(h_widgets, hor_sett_layout, group_by=2)

        # 4 строка в форме Автоматизированного разрезания
        self.slice_output_file_path.setEnabled(False)
        self.slice_output_file_check.clicked.connect(self.slice_toggle_output_file)  # соединяем - требуется настройка
        self.slice_output_file_path.setText(self.settings.read_default_output_dir())  # строка для выходного файла
        # кнопка получения результатов - автоматическое кадрирование
        self.slice_exec = new_button(self, "pb", " Automatically crop images", "glyph_cutter", the_color,
                                     self.slice_exec_run)
        # кнопка открыть каталог результатов кадрирования
        self.slice_open_result = new_button(self, "pb", " Open results", "glyph_folder_clear", the_color,
                                            lambda: os.startfile(self.slice_output_file_path.text()))
        # self.slice_overlap_pols = 0  # какой процент площади полигонов надо перекрыть окном

        self.slice_smart_crop = QtWidgets.QCheckBox("Упрощенное кадрирование сеткой (без интеллектуальной группировки)")

        hor_sett_layout2 = QtWidgets.QHBoxLayout()  # расположение smart + кнопки
        hor_sett_layout2.addWidget(self.slice_smart_crop)
        hor_sett_layout2.addStretch(1)
        hor_sett_layout2.addWidget(self.slice_exec)
        hor_sett_layout2.addWidget(self.slice_open_result)

        # Табличный просмотр в форме Автоматизированного разрезания
        self.slice_tab_labels = QtWidgets.QTableView()  # Создаём объект табличного просмотра
        self.slice_tab_labels.setSortingEnabled(False)  # отключаем сортировку, т.к. для Денисова класса важен порядок
        self.slice_tab_labels.setAlternatingRowColors(True)  # устанавливаем чередование цветов строк таблицы

        slice_auto_form.addRow(hor_sett_layout)  # строка "настройки автоматизированной обработки"
        slice_auto_form.addRow(hor_sett_layout2)  # строка Smart + кнопки
        slice_auto_form.addRow(self.slice_tab_labels)

        slice_caption_form = QtWidgets.QFormLayout()  # общее заголовочное расположение
        slice_caption_form.addRow(self.slice_input_file_label, self.slice_input_file_path)  # строка "исходный файл"
        slice_caption_form.addRow(self.slice_output_file_check, self.slice_output_file_path)  # строка "выходной файл"

        # верхний виджет - автоматизированная обработка
        self.slice_up_group = QtWidgets.QGroupBox("Automatic image cropping")
        self.slice_up_group.setLayout(slice_auto_form)

        # элементы для нижнего виджета
        self.manual_wid = AzManualSlice(self)
        slice_manual_lay = QtWidgets.QVBoxLayout()
        slice_manual_lay.addWidget(self.manual_wid)

        # нижний виджет -  ручная обработка
        self.slice_down_group = QtWidgets.QGroupBox("Manual visual image cropping")
        self.slice_down_group.setLayout(slice_manual_lay)

        split.addWidget(self.slice_up_group)  # верхний виджет - авто разрезание - добавляем в разделитель
        split.addWidget(self.slice_down_group)  # нижний виджет - ручная обработка - добавляем в разделитель
        split.setChildrenCollapsible(True)  # включаем полное сворачивание виджетов внутри разделителя
        split.setSizes((10, 120))

        vlayout = QtWidgets.QVBoxLayout()  # контейнер QVBoxLayout()
        vlayout.addLayout(slice_caption_form)  # добавляем область с заголовочным расположением
        vlayout.addWidget(split)  # добавляем область с разделением
        wid = QtWidgets.QWidget()  # создаём виджет-контейнер...
        wid.setLayout(vlayout)  # ...куда помещаем vlayout (поскольку Central Widget может быть только QWidget)
        self.ui_tab_slicing.setCentralWidget(wid)
        # self.ui_tab_slicing.addToolBar(self.slice_toolbar)

        # проверяем есть ли сохранённый ранее файл проекта, и загружаем его автоматически
        if len(self.slice_input_file_path.text()) > 0:
            self.slice_load_projects_data()

    @QtCore.pyqtSlot()
    def slice_exec_run(self):  # процедура разрезания
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)  # ставим курсор ожидание
        try:
            pols_overlap_percent = []
            model = self.slice_tab_labels.model()
            for row in range(model.rowCount(-198)):  # -198 чтобы тебя запутать))
                # процент указан во втором столбце, роль "Редактирования" включает "Отображение"
                pols_overlap_percent.append((model.data(model.index(row, 1), QtCore.Qt.ItemDataRole.DisplayRole)) / 100)
            new_name = os.path.join(self.slice_output_file_path.text(),
                                    "sliced_%s.json" % datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
            # объект класса для автоматического кадрирования
            cut_images = dn_crop.DNImgCut(os.path.dirname(self.slice_input_file_path.text()),
                                          os.path.basename(self.slice_input_file_path.text()))
            # запуск автоматического кадрирования функцией Дениса
            proc_imgs = cut_images.CutAllImgs(self.slice_scan_size.value(), pols_overlap_percent,
                                              self.slice_overlap_window.value() / 100, new_name,
                                              self.slice_edge.value(), not self.slice_smart_crop.isChecked(), False)
            if proc_imgs > 0:
                self.signal_message.emit("Кадрирование завершено. Общее количество изображений %s" % proc_imgs)
            elif proc_imgs == 0:
                self.signal_message.emit("Кадрирование изображений не выполнено - в проекте отсутствуют изображения")
            else:
                self.signal_message.emit("Нарезка изображений не выполнена")
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
            QtWidgets.QApplication.restoreOverrideCursor()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def slice_load_projects_data(self):  # загрузка файла проекта
        if self.json_obj is not None:
            if self.slice_input_file_path.text() == self.json_obj.FullNameJsonFile:
                return  # Файл не трогали, изменений нет
        self.json_obj = dn_crop.DNjson(self.slice_input_file_path.text())  # Файл проекта, реализация Дениса
        if not self.json_obj.good_file:
            self.signal_message.emit("Выбранный файл не является корректным либо не содержит необходимых данных")
            self.slice_tab_labels.hide()
            self.slice_exec.setEnabled(False)  # отключаем возможность Разрезать
            self.manual_wid.update_input_data(None)  # передаём "Отсутствие" данных для настройки панели Ручной резки
            return
        self.slice_exec.setEnabled(True)
        model_data = []  # данные для отображения
        self.slice_tab_labels.show()
        for label in self.json_obj.labels:
            # [наименование метки, процент перекрытия]
            model_data.append([label, int(self.slice_overlap_pols_default.text())])
        self.slice_tab_labels.setModel(
            AzTableModel(model_data, header_data=["Наименование класса (метки)", "Процент перекрытия"], edit_column=1))
        header = self.slice_tab_labels.horizontalHeader()  # настраиваем отображение столбцов
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.manual_wid.update_input_data(self.json_obj)  # Передаём данные, в т.ч. для настройки панели Ручной резки

    @QtCore.pyqtSlot()
    def slice_write_default_overlap_pols(self):
        self.settings.write_default_slice_overlap_pols(self.slice_overlap_pols_default.value())

    @QtCore.pyqtSlot()
    def slice_write_overlap_window(self):
        self.settings.write_slice_window_overlap(self.slice_overlap_window.value())

    @QtCore.pyqtSlot()
    def slice_toggle_output_file(self):
        self.slice_output_file_path.setEnabled(self.slice_output_file_check.checkState())
        if not self.slice_output_file_check.isChecked():
            self.slice_output_file_path.setText(self.settings.read_default_output_dir())

    def tab_attributes_setup(self):  # настройка страницы "Атрибуты"
        self.ui_tab_attributes = self.tab_basic_setup(True)

    def tab_geometry_setup(self):  # настройка страницы "Геометрия"
        self.ui_tab_geometry = self.tab_basic_setup()

    def tab_basic_setup(self, complex=False):  # базовая настройка каждой страницы QTabWidget
        if complex:
            widget = QtWidgets.QMainWindow()
        else:
            widget = QtWidgets.QWidget()
            widget.layout = QtWidgets.QVBoxLayout(widget)  # не забываем указать ссылку на объект
        return widget

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

    def merge_add_files(self):
        sel_files = az_file_dialog(self, "Select project files to add", self.settings.read_last_dir(), False,
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

    def default_output_dir_change(self):
        # изменение в настройках выходного каталога
        if not self.merge_output_file_check.isChecked():
            self.merge_toggle_output_file()
        if not self.slice_output_file_check.isChecked():
            self.slice_toggle_output_file()


# ----------------------------------------------------------------------------------------------------------------------

def fill_layout_by_widgets(widgets: list, layout, group_by=2):  # автоматизированное заполнение layout
    for i, wdt in enumerate(widgets):
        layout.addWidget(wdt)
        if group_by == 2:
            # Выбираем только нечётные, т.е. 0-нет, 1-да и т.д., а также отбрасываем последний
            if i % 2 == 1 and i < len(widgets) - 1:
                layout.addStretch(1)
        else:  # во всех остальных случаях после каждого виджета - добавляем "растяжку"
            if i < len(widgets) - 1:
                layout.addStretch(1)
