from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper, config, natural_order
from utils.sama_project_handler import DatasetSAMAHandler
from utils.az_dataset_sort_handler import DatasetSortHandler
from ui import new_act, new_button, new_icon, coloring_icon, new_text, new_label_icon, AzButtonLineEdit, \
    az_file_dialog, AzInputDialog, setup_dock_widgets
from ui import AzSortTable, AzTableModel, AzTableAttributes, AzSortingDatasetDialog, AzExportDialog
from collections import defaultdict
import os
import shutil
from datetime import datetime

ROW_H = 16
the_color = UI_COLORS.get("processing_color")
color_train = UI_COLORS.get("train_color")
color_val = UI_COLORS.get("val_color")
color_test = UI_COLORS.get("test_color")


class TabSortUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Страница QTabWidget раздела Сортировка датасета
    color_active, icon_inactive цвета иконок активные и неактивные соответственно
    Example: tab_page = TabSortUI(QtCore.Qt.GlobalColor.red, QtCore.Qt.GlobalColor.white, self)
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabSortUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Sorting"

        if color_active:
            self.icon_active = coloring_icon("glyph_objects", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_objects", color_inactive)

        self.current_file = None  # текущий файл проекта SAMA
        self.sort_file = None  # текущий файл сортировки
        self.sort_mode = False  # режим сортировки
        self.group_mode = False  # режим
        self.sort_dialog = None  # диалог сортировки
        self.export_dialog = None  # диалог экспорта данных
        self.model_image = None  # модель для данных фильтрата
        self.sama_data = DatasetSAMAHandler()  # данные из проекта SAMA инициализируем пустым

        caption = self.setup_caption_widget()  # возвращает QHBoxLayout, настроенный компоновщик
        container_down = self.setup_down_central_widget()  # настройка ui, таблица фильтрата, возвращает виджет

        central_layout = QtWidgets.QVBoxLayout()  # главный Layout, наследуемый класс
        central_layout.addLayout(caption)
        central_layout.addWidget(container_down, 1)
        wid = QtWidgets.QWidget()
        wid.setLayout(central_layout)
        self.setCentralWidget(wid)
        # self.setStyleSheet("QWidget { border: 1px solid yellow; }")  # проверка отображения виджетов

        # указываем инструменты, которые должны выключаться
        self.special_tools = [self.ti_cbx_sel_obj, self.ti_cbx_sel_class, self.ti_tb_sort_mode,
                              self.ti_pb_sel_clear_selection, self.ti_pb_sel_clear_filters]
        # настраиваем все виджеты
        self.image_table_toggle_sort_mode()  # запускаем, чтобы привести в порядок ui инструментов таблицы сортировки

        # Signals: изменение фильтра
        self.ti_cbx_sel_class.currentIndexChanged.connect(self.table_image_filter_changed)
        self.ti_cbx_sel_obj.currentIndexChanged.connect(self.table_image_filter_changed)

        # Signals: взаимодействие с таблицами сортировки
        for wid in self.sort_tables:
            wid.ti_tb_sort_add_to.clicked.connect(self.add_to_sort_table)  # добавление
            wid.ti_tb_sort_remove_from.clicked.connect(self.remove_from_sort_table)  # удаление
            wid.ti_tb_sort_add_group_to.clicked.connect(self.add_group_to_sort_table)  # добавление группы
            wid.ti_tb_sort_remove_group_from.clicked.connect(self.remove_group_from_sort_table)  # добавление группы

        # смотрим, есть ли в реестре файл проекта, который запускали прошлый раз?
        if os.path.exists(self.settings.read_attributes_input()):
            # пробуем загрузить
            self.load_project(self.settings.read_attributes_input(),
                              self.tr(f"Loaded last used project file: {self.settings.read_attributes_input()}"))
        else:  # файла нет, тогда ограничиваем функционал
            self.toggle_tool_buttons(False)

        if self.sama_data.is_correct_file:  # успешна ли автозагрузка данных из реестра?
            if os.path.exists(self.settings.read_sort_file_input()):
                self.load_sort_project(self.settings.read_sort_file_input())  # загружаем проект сортировки

    @QtCore.pyqtSlot(str)
    def default_dir_changed(self, path):
        # заглушка на смену каталога для выходных данных по умолчанию
        pass

    @QtCore.pyqtSlot(str)
    def forward_signal(self, message):  # перенаправление сигналов
        self.signal_message.emit(message)

    def show_status(self):
        pass  # заглушка на кнопку статуса

    def setup_caption_widget(self):
        self.btn_status = new_button(self, "tb", icon="circle_grey", color=None, icon_size=16,
                                     slot=self.show_status, checkable=True, tooltip=self.tr("Toggle log"))
        self.label_project = QtWidgets.QLabel("Path to file project (*.json:)")
        self.file_json = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Load dataset SAMA project"),
                                          read_only=True, dir_only=False, filter="Projects files (*.json)",
                                          slot=self.try_to_load_project,
                                          initial_filter="Projects files (*.json)")
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.btn_status)
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
        hlay.addWidget(spacer)
        return hlay

    def setup_down_central_widget(self):
        """
        Настройка интерфейса для таблицы просмотра изображений/объектов/меток, далее по тексту таблица фильтрата,
        для инструментов сортировки данных на train/val
        """
        self.image_headers = [self.tr("Group"), self.tr("Images"), self.tr("Label"), self.tr("Number")]
        self.image_table = QtWidgets.QTableView()  # используется таблица QTableView, поскольку значений >1000
        self.image_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.image_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.image_table.resizeColumnsToContents()

        h_layout = QtWidgets.QHBoxLayout()
        # для настройки метки (класса)
        self.ti_sel_class_text = QtWidgets.QLabel(self.tr("Selected\nlabel:"))
        self.ti_sel_class_icon = new_label_icon("glyph_filter_labels", the_color, config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        # для настройки группы
        self.ti_sel_obj_text = QtWidgets.QLabel(self.tr("Selected\ngroup:"))
        self.ti_sel_obj_icon = new_label_icon("glyph_filter", the_color, config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        self.ti_cbx_sel_class = QtWidgets.QComboBox()
        self.ti_cbx_sel_obj = QtWidgets.QComboBox()
        self.ti_cbx_sel_obj.setMaximumWidth(130)
        self.ti_cbx_sel_class.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.ti_pb_sel_clear_selection = new_button(self, "tb", self.tr("Reset selection"), "glyph_clear_selection",
                                                    the_color, self.image_table_clear_selection,
                                                    tooltip=self.tr("Reset selection"))
        self.ti_pb_sel_clear_filters = new_button(self, "tb", self.tr("Clear filters"), "glyph_clear_filter",
                                                  the_color, self.image_table_clear_filters,
                                                  tooltip=self.tr("Clear filters"))
        h_widgets = [self.ti_sel_class_icon, self.ti_sel_class_text, self.ti_cbx_sel_class, self.ti_sel_obj_icon,
                     self.ti_sel_obj_text, self.ti_cbx_sel_obj, self.ti_pb_sel_clear_selection,
                     self.ti_pb_sel_clear_filters]

        for widget in h_widgets:  # добавляем виджеты и меняем размер иконки
            if isinstance(widget, QtWidgets.QPushButton) or isinstance(widget, QtWidgets.QToolButton):
                widget.setIconSize(
                    QtCore.QSize(config.UI_AZ_PROC_ATTR_IM_ICON_SIZE, config.UI_AZ_PROC_ATTR_IM_ICON_SIZE))
            h_layout.addWidget(widget)

        v_layout = QtWidgets.QVBoxLayout()  # компоновщик фильтра и таблицы фильтрата
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.image_table)

        h_layout_instr = QtWidgets.QHBoxLayout()  # компоновщик инструментов
        self.ti_tb_sort_mode = new_button(self, "tb", self.tr(" Toggle sort\n train/val"), "glyph_categorization",
                                          the_color, self.image_table_toggle_sort_mode, True, False,
                                          config.UI_AZ_PROC_ATTR_IM_ICON_SIZE,
                                          self.tr("Enable sort mode for train/val"))
        # активатор режима сортировки Train/Val/Test
        self.ti_tb_sort_mode.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # добавляем инструмент "переключения режима сортировки" отдельно, чтобы к нему не применялись общие свойства
        h_layout_instr.addWidget(self.ti_tb_sort_mode)

        self.ti_tb_toggle_groups = new_button(self, "tb", icon="glyph_layers", color=the_color, slot=self.toggle_groups,
                                              tooltip=self.tr("Toggle groups"), checkable=True)
        self.ti_tb_sort_new = new_button(self, "tb", icon="glyph_add", color=the_color, slot=self.new_sort_file,
                                         tooltip=self.tr("New train-val sorting project"))
        self.ti_tb_toggle_tables = new_button(self, "tb", icon="glyph_toggle_cols", color=the_color,
                                              tooltip=self.tr("Toggle tables"))
        self.ti_tb_sort_save = new_button(self, "tb", icon="glyph_save", color=the_color, slot=self.save_sort_file,
                                          tooltip=self.tr("Save train-val sorting project"))
        self.ti_tb_sort_smart = new_button(self, "tb", icon="glyph_smart_process", color=the_color,
                                           slot=self.smart_sort, tooltip=self.tr("Smart dataset sort"))
        self.ti_tb_sort_cook = new_button(self, "tb", icon="glyph_cook", color=the_color, slot=self.cook_dataset,
                                          tooltip=self.tr("Cook dataset"))
        self.sort_project_name = new_text(self, self.tr("Path to sorting project (*.sort):"))
        self.ti_tb_sort_open = AzButtonLineEdit("glyph_folder", the_color, self.tr("Open file"), True, dir_only=False,
                                                filter="sort (*.sort)", initial_filter="sort (*.sort)",
                                                slot=self.open_sort_file)

        v_line = QtWidgets.QFrame()  # добавляем линию-разделитель
        v_line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        v_line2 = QtWidgets.QFrame()
        v_line2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.ti_instruments = [self.ti_tb_toggle_groups, self.sort_project_name,
                               self.ti_tb_sort_open, self.ti_tb_sort_new, v_line, self.ti_tb_toggle_tables,
                               self.ti_tb_sort_save, v_line2, self.ti_tb_sort_smart, self.ti_tb_sort_cook]

        for tool in self.ti_instruments:
            h_layout_instr.addWidget(tool)
            if isinstance(tool, QtWidgets.QToolButton):
                tool.setIconSize(QtCore.QSize(config.UI_AZ_PROC_ATTR_IM_ICON_SIZE, config.UI_AZ_PROC_ATTR_IM_ICON_SIZE))

        # создание виджетов таблиц Train, Val, Sort
        self.sort_widget_train = AzSortTable(color_train, "train", self, ROW_H)
        self.sort_widget_val = AzSortTable(color_val, "val", self, ROW_H)
        self.sort_widget_test = AzSortTable(color_test, "test", self, ROW_H)
        self.sort_tables = [self.sort_widget_train, self.sort_widget_val, self.sort_widget_test]

        h_layout2 = QtWidgets.QHBoxLayout()  # компоновщик таблиц сортировки и таблицы статистики
        h_layout2.addWidget(self.sort_widget_train)
        h_layout2.addWidget(self.sort_widget_val)
        h_layout2.addWidget(self.sort_widget_test)

        self.table_statistic = QtWidgets.QTableView()
        h_lay_stat = QtWidgets.QHBoxLayout()  # горизонтальный компоновщик с меткой для таблицы результатов разбиения
        self.test_val_stats_label = QtWidgets.QLabel(self.tr("Statistic for train/val data:"))
        h_lay_stat.addWidget(self.test_val_stats_label)
        v_layout_stat = QtWidgets.QVBoxLayout()  # вертикальный компоновщик, который принимает еще таблицу
        v_layout_stat.addLayout(h_lay_stat)
        v_layout_stat.addWidget(self.table_statistic)

        h_layout2.addLayout(v_layout_stat)  # добавляем компоновщик статистики

        # Добавляем меню показа/скрытия таблиц сортировки
        self.toggle_train = new_act(self, self.tr(f"Toggle train"), None, the_color, None, True, True,
                                    tip=self.tr("Show or hide table train"))
        self.toggle_train.triggered.connect(
            lambda: self.sort_widget_train.setHidden(not self.sort_widget_train.isHidden()))
        self.toggle_val = new_act(self, self.tr(f"Toggle val"), None, the_color, None, True, True,
                                  tip=self.tr("Show or hide table val"))
        self.toggle_val.triggered.connect(lambda: self.sort_widget_val.setHidden(not self.sort_widget_val.isHidden()))
        self.toggle_test = new_act(self, self.tr(f"Toggle test"), None, the_color, None, True, True,
                                   tip=self.tr("Show or hide table test"))
        self.toggle_test.triggered.connect(
            lambda: self.sort_widget_test.setHidden(not self.sort_widget_test.isHidden()))

        acts = [self.toggle_train, self.toggle_val, self.toggle_test]  # перечень действий меню
        menu = QtWidgets.QMenu(self)
        menu.addActions(acts)
        self.ti_tb_toggle_tables.setMenu(menu)  # устанавливаем меню
        self.ti_tb_toggle_tables.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)

        v_layout2 = QtWidgets.QVBoxLayout()
        v_layout2.addLayout(h_layout_instr)
        line = QtWidgets.QFrame()  # добавляем линию-разделитель
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        v_layout2.addWidget(line)
        v_layout2.addLayout(h_layout2, 1)  # компоновщик для таблиц Train/Val/Stats, делаем доминантным

        # v_layout2.addLayout(v_layout_stat)  # компоновщик для статистики

        container_left = QtWidgets.QWidget()  # контейнер инструментов фильтра и таблицы фильтрата
        container_left.setLayout(v_layout)
        container_right = QtWidgets.QWidget()  # контейнер таблиц Train/Val/Stats и их инструментов
        container_right.setLayout(v_layout2)

        # добавляем контейнеры в разделитель
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(container_left)
        splitter.addWidget(container_right)
        return splitter

    def toggle_tool_buttons(self, flag):
        """Переключаем инструменты"""
        for item in self.special_tools:
            item.setEnabled(flag)

    @QtCore.pyqtSlot(int)
    def table_image_filter_changed(self):
        """Загрузка данных в таблицу фильтрата при изменении фильтров. Если включен режим сортировки, то также
         проверяется наличие объектов в таблицах Train/Val через класс DatasetSortHandler"""
        if not self.current_file:  # если нет исходных данных покидаем
            return
        # выбираем новые результаты в соответствии с доступными фильтрами
        data = self.get_filtered_model_data(self.ti_cbx_sel_obj.currentText(), self.ti_cbx_sel_class.currentText())

        if self.ti_tb_sort_mode.isChecked() and self.sort_file:
            # Если сортировщик включён, то:
            # данные = data[all] - train[data] - val[data] - test[data] = unsort[data] in data[all]
            exclusions = list(self.sort_data.get_images_names_train_val_test())  # недопустимые для вывода данные
            # фильтруем данные с учетом недопустимых элементов
            data = [item for item in data if item[1] not in exclusions]

            if self.group_mode:  # режим "только группы"
                cnt_dict = defaultdict(lambda: [set(), set(), 0])  # используем библиотеку коллекций

                # Структура count_dict: set, set и счетчик для 2, 3 и 4 столбцов соответственно
                for row in data:  # считаем количество
                    key = row[0]
                    cnt_dict[key][0].add(row[1])
                    cnt_dict[key][1].add(row[2])
                    cnt_dict[key][2] += 1

                # Приводим словарь-счетчик к списку и определяем длину по разделам
                data = [[key, len(cnt_dict[key][0]), len(cnt_dict[key][1]), cnt_dict[key][2]] for key in cnt_dict]

                # print(result)

        self.set_image_data_model(data)  # загружаем и устанавливаем модель

    def fill_image_data_filters(self):
        self.ti_cbx_sel_obj.blockSignals(True)  # Отключаем вызов сигналов, т.к. добавляем фильтры
        self.ti_cbx_sel_class.blockSignals(True)

        self.ti_cbx_sel_class.clear()  # сначала ...
        self.ti_cbx_sel_obj.clear()  # ...чистим

        # заполняем отсортированными параметрами
        items = sorted(self.sama_data.get_labels(), key=natural_order)
        self.ti_cbx_sel_class.addItem("< all labels >")
        if helper.check_list(items):
            self.ti_cbx_sel_class.addItems(items)

        items = sorted(self.sama_data.get_group_objects(), key=natural_order)
        self.ti_cbx_sel_obj.addItem("< all >")
        if helper.check_list(items):
            self.ti_cbx_sel_obj.addItems(items)

        self.ti_cbx_sel_obj.blockSignals(False)  # возвращаем функционал обратно
        self.ti_cbx_sel_class.blockSignals(False)

    def get_filtered_model_data(self, object_name=None, label_name=None):
        """Фильтр строк исходных данных (self.original_image_data) таблицы фильтрата"""
        if self.original_image_data is None:
            return
        if object_name == "< all >":
            object_name = None  # устанавливаем пустыми, будем собирать все объекты
        if label_name == "< all labels >":
            label_name = None  # устанавливаем пустыми, будем собирать все метки

        # фильтруем объекты по столбцам 0 и 2
        filtered = [row for row in self.original_image_data if (object_name is None or row[0] == object_name) and
                    (label_name is None or row[2] == label_name)]
        return filtered

    def image_table_clear_selection(self):
        # сброс выделения с таблицы фильтрата image_table
        self.image_table.clearSelection()

    def image_table_clear_filters(self):
        # сброс фильтров
        if self.ti_cbx_sel_obj.count() > 0:
            self.ti_cbx_sel_obj.setCurrentIndex(0)
        if self.ti_cbx_sel_class.count() > 0:
            self.ti_cbx_sel_class.setCurrentIndex(0)

    def image_table_toggle_sort_mode(self, silent=False):
        """Включение и выключение режима сортировщика"""
        self.sort_mode = self.ti_tb_sort_mode.isChecked()  # устанавливаем текущий режим
        for ti_instr in self.ti_instruments:
            ti_instr.setEnabled(self.sort_mode)

        if self.sort_file:
            flag_wid = self.sort_mode
        else:
            flag_wid = False

        for wid in self.sort_tables:  # устанавливаем флаг для виджетов таблиц сортировки
            wid.setEnabled(flag_wid)

        if not silent:
            if self.sort_mode:
                self.signal_message.emit(self.tr("Toggle train/val sort mode on"))
            else:
                self.signal_message.emit(self.tr("Toggle train/val sort mode off"))
        self.table_image_filter_changed()  # отфильтровать вывод в таблице фильтрата

    def set_image_data_model(self, data):
        """Создание и установка модели в таблице фильтрата, по исходным данным, настройка ui таблицы"""
        if len(data) < 1:
            self.image_table.setModel(AzTableModel())

        else:
            self.model_image = AzTableModel(data, self.image_headers)  # модель для данных фильтрата
            proxyModel = QtCore.QSortFilterProxyModel()  # используем для включения сортировки
            proxyModel.setSourceModel(self.model_image)
            self.image_table.setModel(proxyModel)
            self.image_table.setSortingEnabled(True)
            self.image_table.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)

        # настраиваем отображение
        if self.image_table.model().columnCount() > 0:  # для столбцов
            header = self.image_table.horizontalHeader()
            for col in range(self.image_table.model().columnCount()):
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        if self.image_table.model().rowCount() > 0:  # для строк
            for row in range(self.image_table.model().rowCount()):  # выравниваем высоту
                self.image_table.setRowHeight(row, ROW_H)

    def load_image_data_model(self):
        """Первичное заполнение таблицы фильтрата данными"""
        # Данные - массив [["object1", "image_name1", "label1, "item1"][...]]

        if self.original_image_data is None:
            data = self.sama_data.get_model_data()
            self.original_image_data = data

        self.fill_image_data_filters()  # заполняем параметрами для сортировки (фильтрами)
        self.set_image_data_model(data)  # загружаем и устанавливаем модель

    def toggle_groups(self):
        """Включение и выключение режима сортировщика"""
        if not self.sort_mode:
            for wid in self.sort_tables:
                wid.ti_tb_sort_add_to.setEnabled(False)
                wid.ti_tb_sort_remove_from.setEnabled(False)
            return

        flag = not self.ti_tb_toggle_groups.isChecked()
        self.group_mode = not flag
        for wid in self.sort_tables:
            wid.ti_tb_sort_add_to.setEnabled(flag)
            wid.ti_tb_sort_remove_from.setEnabled(flag)
        if flag:
            self.signal_message.emit(self.tr("Toggle group mode off"))
        else:
            self.signal_message.emit(self.tr("Toggle group mode on"))

        self.update_sort_data_tables()  # обновляем таблицы сортировки и...
        self.table_image_filter_changed()  # ...таблицу фильтрата

    def try_to_load_project(self):
        if len(self.file_json.text()) < 5:  # недостойно внимания
            return
        self.load_project(self.file_json.text(), self.tr(f"Loaded project file: {self.file_json.text()}"))

    def load_project(self, filename, message):  # загрузка проекта
        self.sama_data = DatasetSAMAHandler()
        self.unload_sort_file()  # выгружаем файлы сортировки, если они были загружены
        self.sama_data.load(filename)
        if not self.sama_data.is_correct_file:
            self.attr_actions_disable(
                self.tr("Selected file isn't correct, or haven't data"))
            # Выбранный файл не является корректным либо не содержит необходимых данных
            self.file_json.clear()
            self.change_log_icon("grey")
            return

        # Все загружено и всё корректно, поэтому записываем его в реестр и начинаем процедуру загрузки
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        self.file_json.setText(filename)
        self.current_file = filename
        self.settings.write_attributes_input(filename)
        self.toggle_tool_buttons(True)
        self.original_image_data = None  # очищаем данные с исходными значениями
        self.load_image_data_model()  # загружаем таблицу изображений данные для таблицы
        self.change_log_icon("green")
        self.signal_message.emit(message)
        QtWidgets.QApplication.restoreOverrideCursor()

    def change_log_icon(self, color):
        if color == "red":
            icon = "circle_red"
        elif color == "green":
            icon = "circle_green"
        else:
            icon = "circle_grey"
        self.btn_status.setIcon(new_icon(icon))

    def new_sort_file(self):
        if not self.sama_data.is_correct_file:
            return
        file = az_file_dialog(self, self.tr("Create new sorting train/validation project *.sort file"),
                              self.settings.read_last_dir(),
                              dir_only=False, file_to_save=True, filter="Sort (*.sort)",
                              initial_filter="Sort (*.sort)")
        if helper.check_list(file):
            new_sort_file = DatasetSortHandler()  # создаём пустой объект
            data = new_sort_file.create_new_sort_file(self.sama_data)  # создаем данные по текущим SAMA
            helper.save(file, data)  # сохраняем объект
            self.load_sort_project(file)  # загружаем проект, он сам всё настроит
            self.signal_message.emit(self.tr(f"New sorting project file was created: {file}"))

    def open_sort_file(self):
        """Открытие файла сортировка и попытка его загрузки"""
        if len(self.ti_tb_sort_open.text()) < 5:
            return
        self.load_sort_project(self.ti_tb_sort_open.text())

    def save_sort_file(self):
        """Сохранение файла проекта сортировщика"""
        if not helper.check_file(self.sort_file):
            self.signal_message.emit(self.tr("Before saving you must to create or to open a sorting project"))
            return
        helper.save(self.sort_file, self.sort_data.data)
        self.signal_message.emit(self.tr(f"Train-val sorting project saved to: '{self.sort_file}'"))

    def check_sort_project(self, sort_data) -> bool:
        """Проверка соответствия проекта сортировки *.sort текущему проекту разметки *.sama"""
        if not self.sama_data:
            return False
        project_labels = self.sama_data.get_labels()
        for label in sort_data.get_rows_labels_headers():
            if label not in project_labels:
                return False
        return True

    def load_sort_project(self, path):
        """Загрузка проекта сортировки датасета"""
        sort_data = DatasetSortHandler()  # создаем объект сортировщика
        sort_data.load_from_file(path)  # заполняем его данными
        if not self.check_sort_project(sort_data):
            self.signal_message.emit(
                self.tr(f"The selected sorting project is not associated with the current labeling project: '{path}.'"))
            return

        if sort_data.is_correct_file:  # если всё хорошо, то...
            self.unload_sort_file(True)  # ...сначала выгружаем (если был загружен) старый проект
            self.sort_file = path
            self.sort_data = sort_data
            self.settings.write_sort_file_input(path)  # записываем удачный файл для последующего автооткрытия
            self.ti_tb_sort_open.setText(path)  # ставит текст в ui
            for wid in self.sort_tables:  # инициализируем модели при первой загрузке
                wid.init_sort_models()
            self.update_sort_data_tables()  # заполняем таблицы
            self.image_table_toggle_sort_mode()
            self.signal_message.emit(self.tr(f"Train-val sorting project load: {path}"))
        else:
            self.ti_tb_sort_open.clear()  # Очищаем поле с файлом, что выбрал пользователь, т.к. файл не корректен

    def unload_sort_file(self, soft=False):
        """Выгрузка данных режима сортировщика. Флаг soft - использование мягкого режима, без отключения панели."""
        if self.sort_file:  # имеется файл сортировки
            if self.sort_mode:
                if not soft:
                    self.ti_tb_sort_mode.setChecked(False)  # отключаем инструмент
                self.image_table_toggle_sort_mode(silent=True)  # выключаем режим сортировки в тихом режиме
            self.sort_file = None  # убираем данные
            self.sort = None
            self.ti_tb_sort_open.clear()
            # выгружаем все таблицы
            for wid in self.sort_tables:
                wid.table_view.setModel(None)
            self.table_statistic.setModel(None)

    def set_sort_data_statistic(self):
        """Заполнение таблицы статистики для по результатам сортировки"""
        if not self.sort_file:
            return
        header = ["Train", "Val", "Test", "Total"]
        row_headers = self.sort_data.get_rows_labels_headers()  # базовый список меток
        row_headers.insert(0, self.tr("Total images, %"))  # добавляем в начало строки: всего изображений...
        row_headers.insert(0, self.tr("Total labels, %"))  # ...и всего меток
        model = AzTableModel(self.sort_data.export_data, header,
                             vertical_data=row_headers)  # заголовок всего один "images"
        self.table_statistic.setModel(model)
        if self.table_statistic.model().rowCount() > 0:  # для строк
            for row in range(self.table_statistic.model().rowCount()):  # выравниваем высоту
                self.table_statistic.setRowHeight(row, ROW_H)
        if self.table_statistic.model().columnCount() > 0:
            header = self.table_statistic.horizontalHeader()
            for col in range(self.table_statistic.model().columnCount()):
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def identify_sender_get_rows(self, check_in=False, check_out=False):
        """
        Определяем отправителя, проверяем условия, таблицы, возвращаем выделенные строки искомой таблицы. Следует
        обязательно указать флаг: check_in - проверка выделения таблицы self.image_table; check_out - проверка
        выделения таблиц сортировки
        """
        sender = self.sender()
        if not sender:
            return None, None
        sender = self.sender().text()  # определяем от кого пришёл сигнал
        if not sender:
            return None, None
        if check_in:
            if not self.image_table.selectionModel().hasSelection():  # выбранных строк нет
                return None, None
            if not self.sort_file:  # данных для сортировки не загружено
                return None, None
            if self.group_mode:  # при режиме группировки - строки 0 столбца
                sel_rows = self.get_selected_rows(self.image_table, 0)
            else:  # иначе нас интересуют выделенные строки 1 столбца
                sel_rows = self.get_selected_rows(self.image_table, 1)
            return sender, sel_rows

        if check_out:
            wid = self.get_table(sender)  # определение виджета и таблицы
            # проверка наличие выделенных строк
            if wid.table_view is None or not wid.table_view.selectionModel().hasSelection():
                return None, None  # нет выделенных элементов либо мистика
            sel_rows = self.get_selected_rows(wid.table_view, 0)  # для удаления - 1 столбец
            return sender, sel_rows

    def get_rows_in_group_mode(self, data, source):
        source_table = None
        if source == "unsort":
            source_table = "unsort"  # источник - несортированные данные
        else:
            for wid in self.sort_tables:
                if source == wid.sort_type:
                    source_table = wid.sort_type  # источник - данные таблицы выборки

        filtered_rows = self.sort_data.get_images_by_group(source_table, list(data))
        return filtered_rows

    def get_rows_by_group(self, data, source):
        import re
        # сначала определяем таблицу
        source_table = None
        if source == "unsort":
            source_table = self.image_table
            target_column = 1

        else:
            for wid in self.sort_tables:
                if source == wid.sort_type:
                    source_table = wid.table_view
                    target_column = 0  # значащий столбец таблицы

        print("data:", data, "\nsource:", source)
        pattern = helper.PATTERNS.get("double_underscore")
        unique_groups = set()  # набор групп

        for image in data:
            match = re.search(pattern, image)  # ищем имя объекта
            if match:
                unique_groups.add(match.group(0))

        filtered_rows = set()  # новый список изображений выбранных по значению групп
        for group in unique_groups:
            proxy_model = QtCore.QSortFilterProxyModel()  # используем фильтрующую модель
            proxy_model.setSourceModel(source_table.model())  # self.image_table.model()
            proxy_model.setFilterKeyColumn(0)  # фильтруем по первому столбцу
            proxy_model.setFilterFixedString(group)  # фильтруем строки со значением группы (usa_66, ...)
            # добавляем все найденные строки в set()
            for row in range(proxy_model.rowCount()):
                index = proxy_model.index(row, target_column)  # получаем индекс в зависимости от таблицы
                filtered_rows.add(index.data(QtCore.Qt.ItemDataRole.DisplayRole))

        return filtered_rows

    def transfer_data(self, source, target, data, use_group=False):
        """Перенос данных и обновление виджетов; source, target = 'unsort', 'train', 'val' или 'test' """

        if use_group:  # необходимо переместить всю группу объектов
            if self.group_mode:  # включен режим группового перемещения
                data = self.get_rows_in_group_mode(data, source)
            else:
                data = self.get_rows_by_group(data, source)  # {'129c_FRA_0.jpg',  '129c_FRA_1.jpg'}
        self.sort_data.move_rows_by_images_names(source, target, data, use_group)  # переносим объекты
        self.update_sort_data_tables()  # обновляем таблицы сортировки train/val
        self.table_image_filter_changed()  # обновляем таблицу фильтрата

    def add_to_sort_table(self):
        """
        Добавление в сортировочные таблицы строк из table_image. Производится перемещение записей в классе
        DatasetSortHandler из "unsort" в выбранную таблицу Train, Sort или Val.
        """
        sender, sel_rows = self.identify_sender_get_rows(check_in=True)
        if sel_rows and self.sort_data:
            self.transfer_data("unsort", sender, sel_rows)

    def add_group_to_sort_table(self):
        """
        Групповое добавление в сортировочные таблицы строк из table_image: перемещение записей в классе
        DatasetSortHandler из "unsort" в выбранную таблицу Train, Sort или Val всех изображений, относящихся
        к выбранной группе.
        """
        sender, sel_rows = self.identify_sender_get_rows(check_in=True)
        if sel_rows and self.sort_data:
            self.transfer_data("unsort", sender, sel_rows, use_group=True)

    def remove_from_sort_table(self):
        """
        Удаление строк из сортировочной таблицы и в классе DatasetSortHandler. Перемещение удаленных строк в table_image
        """
        sender, sel_rows = self.identify_sender_get_rows(check_out=True)  # получаем отправителя и строки
        if sel_rows and self.sort_data:
            self.transfer_data(sender, "unsort", sel_rows)

    def remove_group_from_sort_table(self):
        """
        Групповое удаление из сортировочной таблицы и в классе DatasetSortHandler. Перемещение удаленных строк
        в table_image.
        """
        sender, sel_rows = self.identify_sender_get_rows(check_out=True)  # получаем отправителя и строки
        if sel_rows and self.sort_data:
            self.transfer_data(sender, "unsort", sel_rows, use_group=True)

    def update_sort_data_tables(self):
        """Заполнение таблиц сортировки данными сортировщика DatasetSortHandler"""
        for wid in self.sort_tables:  # устанавливаем последовательно для каждой таблицы
            # нам нужны данные [[data1], [data2], ...], а не [data1, data2, ...]
            if self.group_mode:
                wid.core_model.setData([[item] for item in self.sort_data.get_group_names(wid.sort_type)])
            else:
                wid.core_model.setData([[item] for item in self.sort_data.get_images_names(wid.sort_type)])
            wid.table_view.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)  # сортируем по возрастанию

            wid.align_rows_and_cols()  # выровняем строки и столбцы
        self.set_sort_data_statistic()

    def get_table(self, name):
        """Определение таблицы сортировки по значению сигнала кнопки"""
        for wid in self.sort_tables:
            if wid.sort_type == name:
                return wid

    @staticmethod
    def get_selected_rows(table, column):
        """Получение выделенных строк таблицы"""
        indexes = table.selectionModel().selectedIndexes()
        sel_rows = set()
        for index in indexes:
            if index.column() == column:
                sel_rows.add(index.data(QtCore.Qt.ItemDataRole.DisplayRole))  # получаем набор уникальных значений
        return sel_rows

    @staticmethod
    def move_sorting_files(input_dir, output_dir, train_val_test, data):
        """
        input_dir - исходный каталог, где размещены файлы изображений и файлы txt
        output_dir - выходной каталог экспорта
        train_val_test - конкретизируйте тип данных: "train", "val", "test"
        data - перечень файлов изображений, которые будут перемещаться
        """
        output_txt_dir = os.path.join(output_dir, "labels", train_val_test)
        output_jpg_dir = os.path.join(output_dir, "images", train_val_test)

        good_counts = 0
        bad_counts = 0

        for filename in data:
            txt_name = os.path.splitext(os.path.basename(filename))[0] + ".txt"
            src_txt = os.path.join(input_dir, txt_name)
            dst_txt = os.path.join(output_txt_dir, txt_name)

            src_jpg = os.path.join(input_dir, filename)
            dst_jpg = os.path.join(output_jpg_dir, filename)

            try:  # перемещение
                shutil.move(src_txt, dst_txt)
                shutil.move(src_jpg, dst_jpg)
                good_counts += 1
            except FileNotFoundError:  # счетчик не перемещенных файлов
                bad_counts += 1
        return [good_counts, bad_counts]

    def smart_sort(self):
        """Автоматизированная сортировка"""
        if not self.sort_file:
            self.signal_message.emit(self.tr(f"First open or create sort file."))
            return
        full_data = self.sort_data.get_data("full")
        if self.sort_data.is_correct_file and len(full_data) > 2:  # исходные данные корректны
            self.sort_dialog = AzSortingDatasetDialog(full_data, parent=self,
                                                      window_title=self.tr("Smart dataset sorting"))
            if self.sort_dialog.exec_() == QtWidgets.QDialog.Accepted:  # сортировка успешна
                self.sort_data.clear_train_val_test_unsort()  # сбросим все установленные выборки

                for name, res_dict in self.sort_dialog.result.items():  # проходим по результатам сортировки...
                    # ...и формируем словари выборок train, val, test
                    self.sort_data.set_data(name, {key: value for key, value in zip(res_dict["img"], res_dict["data"])})
                    # print("data_" + name + ":", self.sort_data.data[name])

                # определяем данные unsort
                train_val_test = self.sort_data.get_images_names_train_val_test()
                unsort_data = {key: val for key, val in full_data.items() if key not in train_val_test}
                self.sort_data.set_data("unsort", unsort_data)
                self.sort_data.update_stats()  # обновляем статистику
                self.update_sort_data_tables()  # обновляем таблицы сортировки train/val
                self.table_image_filter_changed()  # обновляем таблицу фильтрата

        else:  # запуск сортировки неудачен
            self.signal_message.emit(self.tr("The current data is not correct for smart sorting."))
            return

    def cook_dataset(self):
        """Вызов диалога экспорта данных"""
        if not self.sort_file:
            self.signal_message.emit(self.tr(f"First open or create sort file."))
            return

        split_data = {item: list(self.sort_data.get_images_names(item)) for item in ["train", "val", "test"]}
        self.export_dialog = AzExportDialog(self.sama_data.data, split_data, parent=self)
        if self.export_dialog.exec_() == QtWidgets.QDialog.Accepted:
            message = self.tr(f"Dataset export complete to '{self.export_dialog.export_worker.export_dir}'")
            self.signal_message.emit(message)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabSortUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Dataset Sorting

        if self.model_image:
            self.model_image.setHorizontalHeaderLabels([self.tr("Group"), self.tr("Images"), self.tr("Label"),
                                                        self.tr("Number")])
        self.sort_widget_train.translate_ui()
        self.sort_widget_val.translate_ui()
        self.sort_widget_test.translate_ui()
        if self.sort_dialog:
            self.sort_dialog.translate_ui()

        self.label_project.setText(self.tr("Path to file project (*.json):"))

        self.ti_sel_class_text.setText(self.tr("Selected\nlabel:"))
        self.ti_sel_obj_text.setText(self.tr("Selected\ngroup:"))
        self.ti_pb_sel_clear_selection.setToolTip(self.tr("Reset selection"))
        self.ti_pb_sel_clear_filters.setToolTip(self.tr("Clear filters"))

        self.ti_tb_sort_mode.setText(self.tr(" Toggle sort\n train/val"))
        self.ti_tb_sort_mode.setToolTip(self.tr("Enable sort mode for train/val"))
        self.ti_tb_sort_new.setToolTip(self.tr("New train-val sorting project"))
        self.ti_tb_toggle_tables.setToolTip(self.tr("Toggle tables"))
        self.ti_tb_sort_save.setToolTip(self.tr("Save train-val sorting project"))
        self.ti_tb_sort_smart.setToolTip(self.tr("Smart dataset sort"))
        self.ti_tb_sort_cook.setToolTip(self.tr("Cook dataset"))
        self.sort_project_name.setText(self.tr("Path to sorting project (*.sort):"))
        self.ti_tb_sort_open.button.setToolTip(self.tr("Open file"))

        self.test_val_stats_label.setText(self.tr("Statistic for train/val data:"))
        self.toggle_train.setText(self.tr(f"Toggle train"))
        self.toggle_train.setToolTip(self.tr("Show or hide table train"))
        self.toggle_val.setText(self.tr(f"Toggle val"))
        self.toggle_val.setToolTip(self.tr("Show or hide table val"))
        self.toggle_test.setText(self.tr(f"Toggle test"))
        self.toggle_test.setToolTip(self.tr("Show or hide table test"))

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = TabSortUI()
    w.show()
    app.exec()
