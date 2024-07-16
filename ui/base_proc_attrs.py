import copy

from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper, config, natural_order
from utils.sama_project_handler import DatasetSAMAHandler
from utils.az_dataset_sort_handler import DatasetSortHandler
from ui import new_button, AzButtonLineEdit, coloring_icon, new_text, az_file_dialog, save_via_qtextstream, new_act, \
    AzInputDialog, az_custom_dialog, new_icon, setup_dock_widgets, AzTableModel, set_widgets_and_layouts_margins, \
    set_widgets_visible, new_label_icon
import os
import shutil
from datetime import datetime

ROW_H = 16
the_color = UI_COLORS.get("processing_color")
color_train = UI_COLORS.get("train_color")
color_val = UI_COLORS.get("val_color")
color_test = UI_COLORS.get("test_color")


# TODO: сделать кнопку "Добавлять все объекты из выбранной группы"
# TODO: добавить инструмент назначения Разметчика
# TODO: добавить описание проекта, добавить его в сам проект SAMA_handler
# TODO: Сделать фрейм общей статистики отдельно справа, сделать кнопку сбросить данные.


# ----------------------------------------------------------------------------------------------------------------------

class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с Атрибутивными данными проектов разметки
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabAttributesUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Attributes"
        self.tool_tip_title = "Searching and editing dataset attributes"
        if color_active:
            self.icon_active = coloring_icon("glyph_attributes", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_attributes", color_inactive)

        self.current_file = None  # текущий файл проекта SAMA
        self.sort_file = None  # текущий файл сортировки
        self.sort_mode = False  # режим сортировки

        # Настройка ui
        self.setup_log()
        caption = self.setup_caption_widget()  # возвращает QHBoxLayout, настроенный компоновщик
        container_up = self.setup_up_central_widget()  # настройка ui, общая таблица возвращает виджет
        container_down = self.setup_down_central_widget()  # настройка ui, таблица фильтрата, возвращает виджет

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self)
        splitter.addWidget(container_up)
        splitter.addWidget(container_down)
        central_layout = QtWidgets.QVBoxLayout(self)  # главный Layout, наследуемый класс
        central_layout.addLayout(caption)
        central_layout.addWidget(splitter)
        wid = QtWidgets.QWidget()
        wid.setLayout(central_layout)
        self.setCentralWidget(wid)

        # настраиваем все виджеты
        setup_dock_widgets(self, ["bottom_dock"], config.UI_BASE_ATTRS)
        self.image_table_toggle_sort_mode()  # запускаем, чтобы привести в порядок ui инструментов таблицы сортировки

        # Signals
        self.table_widget.signal_message.connect(self.forward_signal)  # перенаправление сигнала в строку состояния
        self.table_widget.signal_data_changed.connect(self.log_change_data)  # запись информации в лог для пользователя

        # изменение фильтра
        self.ti_cbx_sel_class.currentIndexChanged.connect(self.table_image_filter_changed)
        self.ti_cbx_sel_obj.currentIndexChanged.connect(self.table_image_filter_changed)

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

    def setup_caption_widget(self):
        self.btn_log_and_status = new_button(self, "tb", icon="circle_grey", color=None, icon_size=16,
                                             slot=self.toggle_log, checkable=True, tooltip=self.tr("Toggle log"))
        self.label_project = QtWidgets.QLabel("Path to file project *.json:")
        self.file_json = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Load dataset SAMA project"),
                                          read_only=True, dir_only=False, filter=self.tr("Projects files (*.json)"),
                                          slot=self.attr_load_projects_data,
                                          initial_filter="json (*.json)")
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.btn_log_and_status)
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
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
        self.ti_sel_obj_icon = new_label_icon("glyph_objects", the_color, config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        self.ti_cbx_sel_class = QtWidgets.QComboBox()
        self.ti_cbx_sel_obj = QtWidgets.QComboBox()
        self.ti_cbx_sel_obj.setMaximumWidth(130)
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

        # сортировщик Train/Val/Test
        self.table_train = QtWidgets.QTableView()
        self.table_val = QtWidgets.QTableView()
        tables = [self.table_train, self.table_val]

        for i, table in enumerate(tables):  # настраиваем таблицы для Train/Val
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
            table.setWindowTitle("t" + str(i))
            table.setSortingEnabled(True)

        h_layout_instr = QtWidgets.QHBoxLayout()  # компоновщик инструментов
        self.ti_tb_sort_mode = new_button(self, "tb", self.tr(" Toggle sort\n train/val"), "glyph_categorization",
                                          the_color, self.image_table_toggle_sort_mode, True, False,
                                          config.UI_AZ_PROC_ATTR_IM_ICON_SIZE,
                                          self.tr("Enable sort mode for train/val"))
        # активатор режима сортировки Train/Val/Test
        self.ti_tb_sort_mode.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        h_layout_instr.addWidget(self.ti_tb_sort_mode)

        self.ti_tb_sort_new = new_button(self, "tb", icon="glyph_add", color=the_color, slot=self.new_sort_file,
                                         tooltip=self.tr("New train-val sorting project"))
        self.ti_tb_toggle_tables = new_button(self, "tb", icon="glyph_save", color=the_color, slot=self.toggle_tables,
                                              tooltip=self.tr("Toggle tables"))
        self.ti_tb_sort_save = new_button(self, "tb", icon="glyph_save", color=the_color, slot=self.save_sort_file,
                                          tooltip=self.tr("Save train-val sorting project"))
        self.ti_tb_sort_smart = new_button(self, "tb", icon="glyph_smart_process", color=the_color,
                                           slot=self.smart_sort, tooltip=self.tr("Smart dataset sort"))
        self.ti_tb_sort_cook = new_button(self, "tb", icon="glyph_cook", color=the_color, slot=self.cook_dataset,
                                          tooltip=self.tr("Cook dataset"))
        self.ti_tb_sort_open = AzButtonLineEdit("glyph_folder", the_color, "Open file", True, dir_only=False,
                                                filter="sort (*.sort)", initial_filter="sort (*.sort)",
                                                slot=self.open_sort_file)
        v_line = QtWidgets.QFrame()  # добавляем линию-разделитель
        v_line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        v_line2 = QtWidgets.QFrame()
        v_line2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.ti_instruments = [self.ti_tb_sort_open, self.ti_tb_sort_new, v_line, self.ti_tb_toggle_tables,
                               self.ti_tb_sort_save, v_line2, self.ti_tb_sort_smart, self.ti_tb_sort_cook]

        for tool in self.ti_instruments:
            h_layout_instr.addWidget(tool)
            if isinstance(tool, QtWidgets.QToolButton):
                tool.setIconSize(QtCore.QSize(config.UI_AZ_PROC_ATTR_IM_ICON_SIZE, config.UI_AZ_PROC_ATTR_IM_ICON_SIZE))

        # компоновка таблицы Train
        lay_train = QtWidgets.QVBoxLayout()
        h_lay_train = QtWidgets.QHBoxLayout()
        self.ti_train_label = QtWidgets.QLabel(self.tr("Train table:"))
        self.ti_tb_sort_add_to_train = new_button(self, "tb", "train", "glyph_add2", color=color_train,
                                                  slot=self.add_to_sort_table, tooltip=self.tr("Add to train"),
                                                  icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)
        self.ti_tb_sort_remove_from_train = new_button(self, "tb", "train", "glyph_delete2", color=color_train,
                                                       slot=self.remove_from_sort_table,
                                                       tooltip=self.tr("Remove selected rows from train"),
                                                       icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # горизонтальный спейсер
        h_lay_train.addWidget(self.ti_train_label)
        h_lay_train.addWidget(self.ti_tb_sort_add_to_train)
        h_lay_train.addWidget(spacer)
        h_lay_train.addWidget(self.ti_tb_sort_remove_from_train)
        lay_train.addLayout(h_lay_train)
        lay_train.addWidget(self.table_train)

        # компоновка таблицы Validation
        lay_val = QtWidgets.QVBoxLayout()
        h_lay_val = QtWidgets.QHBoxLayout()
        self.ti_train_val = QtWidgets.QLabel(self.tr("Validation table:"))
        self.ti_tb_sort_add_to_val = new_button(self, "tb", "val", "glyph_add2", color=color_val,
                                                slot=self.add_to_sort_table, tooltip=self.tr("Add to val"),
                                                icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)
        self.ti_tb_sort_remove_from_val = new_button(self, "tb", "val", "glyph_delete2", color=color_val,
                                                     slot=self.remove_from_sort_table,
                                                     tooltip=self.tr("Remove selected rows from val"),
                                                     icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)
        h_lay_val.addWidget(self.ti_train_val)
        h_lay_val.addWidget(self.ti_tb_sort_add_to_val)
        h_lay_val.addWidget(spacer)
        h_lay_val.addWidget(self.ti_tb_sort_remove_from_val)
        lay_val.addLayout(h_lay_val)
        lay_val.addWidget(self.table_val)

        h_layout2 = QtWidgets.QHBoxLayout()  # устанавливаем виджеты-таблицы
        h_layout2.addLayout(lay_train)
        table_line = QtWidgets.QFrame()  # добавляем линию-разделитель
        table_line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        h_layout2.addWidget(table_line)
        h_layout2.addLayout(lay_val)
        self.widget_test = AzSortTable(color_test, "test", self)

        ####
        h_layout2.addWidget(self.widget_test)

        self.table_statistic = QtWidgets.QTableView()
        h_lay_stat = QtWidgets.QHBoxLayout()  # горизонтальный компоновщик с меткой для таблицы результатов разбиения
        self.test_val_stats_label = QtWidgets.QLabel(self.tr("Statistic for train/val data:"))
        h_lay_stat.addWidget(self.test_val_stats_label)
        v_layout_stat = QtWidgets.QVBoxLayout()  # вертикальный компоновщик, который принимает еще таблицу
        v_layout_stat.addLayout(h_lay_stat)
        v_layout_stat.addWidget(self.table_statistic)

        h_layout2.addLayout(v_layout_stat)

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

        set_widgets_and_layouts_margins(splitter, 0, 0, 0, 0)
        splitter.setContentsMargins(5, 5, 5, 5)  # и только главный виджет будет иметь отступы
        return splitter

    def toggle_tables(self):
        """Включение и выключение таблиц"""
        self.widget_test.setHidden(not self.widget_test.isHidden())

    def setup_up_central_widget(self):
        """Настройка интерфейса для таблицы статистики и перечня инструментов (центральный виджет)"""
        self.dataset_info_images_desc = new_text(self, "Count of images: ", alignment="r")
        self.dataset_info_images_val = new_text(self, "-", bald=False)
        self.dataset_info_labels_desc = new_text(self, "Count of labels: ", "indianred", "r")
        self.dataset_info_labels_val = new_text(self, "-", "indianred", bald=False)
        self.dataset_info_lrm_desc = new_text(self, "Average GSD:", alignment="r")
        self.dataset_info_lrm_val = new_text(self, "-", bald=False)
        self.dataset_info_devi_lrm_desc = new_text(self, "Deviation GSD:", "peru", "r")
        self.dataset_info_devi_lrm_val = new_text(self, "-", "peru", bald=False)
        self.labels_dataset_info = [self.dataset_info_images_desc, self.dataset_info_labels_desc,
                                    self.dataset_info_lrm_desc, self.dataset_info_devi_lrm_desc]
        self.labels_dataset_val = [self.dataset_info_images_val, self.dataset_info_labels_val,
                                   self.dataset_info_lrm_val, self.dataset_info_devi_lrm_val]

        hlay2 = QtWidgets.QHBoxLayout()
        hlay2.setSpacing(0)

        # информация о датасете: количество снимков в датасете, количество меток, среднее ЛРМ, девиация ЛРМ
        for i in range(4):
            hlay2.addWidget(self.labels_dataset_info[i])
            hlay2.addWidget(self.labels_dataset_val[i])

        #  Перечень действий с файлом проекта: копия+; экспорт+; сохранить палитру+; применить палитру+;
        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addLayout(hlay2)
        self.btn_copy = new_button(self, "tb", icon="glyph_duplicate", slot=self.attrs_copy_project, color=the_color,
                                   icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                   tooltip=self.tr("Make copy of current project"))
        self.btn_export = new_button(self, "tb", icon="glyph_check_all", slot=self.attrs_export, color=the_color,
                                     icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                     tooltip=self.tr("Export current project info"))
        self.btn_save_palette = new_button(self, "tb", icon="glyph_palette", slot=self.attrs_save_palette,
                                           color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                           tooltip=self.tr("Save original project palette"))
        self.btn_apply_palette = new_button(self, "tb", icon="glyph_paint_brush", slot=self.attrs_apply_palette,
                                            color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                            tooltip=self.tr("Apply palette for current project and reload it"))
        self.btn_apply_lrm = new_button(self, "tb", icon="glyph_sat_image", slot=self.attrs_apply_lrm_from_folder,
                                        color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE,
                                        tooltip="Set GSD data from map files in folder to current project")
        self.btn_save = new_button(self, "tb", icon="glyph_save2", tooltip=self.tr("Save changes to the project"),
                                   slot=self.save, color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)
        self.common_buttons = [self.btn_copy, self.btn_save_palette, self.btn_apply_palette, self.btn_export,
                               self.btn_apply_lrm, self.btn_save]
        hlay3 = QtWidgets.QHBoxLayout()
        hlay3.addSpacing(50)
        for button in self.common_buttons:
            hlay3.addWidget(button)
        hlay_finish = QtWidgets.QHBoxLayout()
        hlay_finish.addLayout(vlay2)
        hlay_finish.addLayout(hlay3)

        # заголовок для таблицы
        self.headers = [
            self.tr("Label name"), self.tr("Number of labels"), self.tr("Frequency per 100 images"),
            self.tr("% total labels"), self.tr("Average area, pixels"), self.tr('SD of area, pixels'),
            self.tr("Balance"), self.tr("Color"), self.tr("Action")]

        # данные из проекта SAMA будут загружаться в DatasetSAMAHandler
        self.sama_data = DatasetSAMAHandler()  # делаем изначально пустым

        # данные из DatasetSAMAHandler будут отображаться в таблице
        self.table_widget = AzTableAttributes(headers=self.headers, special_cols={7: "color", 8: "action"},
                                              data=None, parent=self)  # и таблица тоже пустая

        header = self.table_widget.horizontalHeader()  # настраиваем отображение столбцов именно таблицы SAMA
        for column in range(self.table_widget.columnCount()):
            if column == 6:
                self.table_widget.setColumnWidth(column, 55)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            elif column == 7:
                self.table_widget.setColumnWidth(column, 45)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            elif column == 8:
                self.table_widget.setColumnWidth(column, 45)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            # else:
            #     header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)  # ResizeToContents
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

        # итоговая настройка ui центрального виджета
        layout_up = QtWidgets.QVBoxLayout()  # главный Layout, наследуемый класс
        layout_up.addLayout(hlay_finish)  # добавляем ему расположение с кнопками и QLabel
        layout_up.addWidget(self.table_widget)
        container_up = QtWidgets.QWidget()
        container_up.setLayout(layout_up)
        return container_up

    @QtCore.pyqtSlot(str)
    def forward_signal(self, message):  # перенаправление сигналов
        self.signal_message.emit(message)

    @QtCore.pyqtSlot(str)
    def default_dir_changed(self, path):
        # заглушка на смену каталога для выходных данных по умолчанию
        pass

    def save(self):
        self.save_and_reload(self.current_file, self.tr(f"Project was saved and reload: {self.current_file}"))

    def save_and_reload(self, file, message):
        self.sama_data.save(file)  # сохранение данных и перезагрузка данных
        self.load_project(file, message)

    def setup_log(self):
        """ Настройка интерфейса для лога """
        self.log = QtWidgets.QTextEdit(self)  # лог, для вывода сообщений.
        self.log.setReadOnly(True)
        self.bottom_dock = QtWidgets.QDockWidget("")  # контейнер для информации о логе
        self.bottom_dock.setWidget(self.log)  # устанавливаем в контейнер QLabel
        self.bottom_dock.setWindowTitle("Log")
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)

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

    def update_sort_data_tables(self):
        """Заполнение таблиц сортировки данными сортировщика DatasetSortHandler"""
        self.set_sort_data_with_model(self.table_val, self.sort_data.get_images_names("val"))
        self.set_sort_data_with_model(self.table_train, self.sort_data.get_images_names("train"))
        # такое же будет и для таблицы Test
        self.set_sort_data_statistic()

    def set_sort_data_with_model(self, table_view, data):
        """Создание модели для таблиц сортировки и установка в table_view, выравнивание строк"""
        # обязательно конвертируем просто список в список списков
        data = [[item] for item in data]
        if len(data) < 1:
            model = AzTableModel()
        else:
            model = AzTableModel(data, ["images"])  # заголовок всего один "images"

        proxyModel = QtCore.QSortFilterProxyModel()  # используем для включения сортировки
        proxyModel.setSourceModel(model)
        table_view.setSortingEnabled(True)

        table_view.setModel(proxyModel)
        if table_view.model().columnCount() > 0:
            table_view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        if table_view.model().rowCount() > 0:
            for row in range(model.rowCount()):  # выравниваем высоту
                table_view.setRowHeight(row, ROW_H)

    def add_to_sort_table(self):
        """Добавление в сортировочные таблицы строк из table_image"""
        sender = self.sender().text()  # определяем от кого пришёл сигнал
        if sender:
            self.move_to_sort_data(sender)

    def remove_from_sort_table(self):
        """Удаление строк из сортировочной таблицы и возвращение их в table_image"""
        sender = self.sender().text()  # определяем от кого пришёл сигнал
        if sender:
            self.remove_from_sort_data(sender)

    def move_to_sort_data(self, table_sender):
        """Перемещение записей в классе DatasetSortHandler. table - таблица, в которую следует переместить"""
        if not self.image_table.selectionModel().hasSelection():  # ничего не выбрано
            return
        if not self.sort_file:  # данных для сортировки не загружено
            return
        sel_rows = self.get_selected_rows(self.image_table, 1)  # нас интересуют выделенные строки 2 столбца
        if sel_rows:
            self.sort_data.move_rows_by_images_names("unsort", table_sender, sel_rows)  # добавляем объекты в таблицу
            self.update_sort_data_tables()  # обновляем таблицы сортировки train/val
            self.table_image_filter_changed()  # обновляем таблицу фильтрата

    def remove_from_sort_data(self, table_sender):
        """Удаление в классе DatasetSortHandler"""
        table = self.get_table(table_sender)
        if table is None or not table.selectionModel().hasSelection():
            return  # нет выделенных элементов либо мистика
        sel_rows = self.get_selected_rows(table, 0)  # для удаления - 1 столбец
        if sel_rows:
            self.sort_data.move_rows_by_images_names(table_sender, "unsort", sel_rows)
            self.update_sort_data_tables()  # обновляем таблицы сортировки train/val
            self.table_image_filter_changed()  # обновляем таблицу фильтрата

    @staticmethod
    def get_selected_rows(table, column):
        """Получение выделенных строк таблицы"""
        indexes = table.selectionModel().selectedIndexes()
        sel_rows = set()
        for index in indexes:
            if index.column() == column:
                sel_rows.add(index.data(QtCore.Qt.ItemDataRole.DisplayRole))  # получаем набор уникальных значений
        return sel_rows

    def get_table(self, name):  # определить таблицу #
        if name == "train":
            return self.table_train
        elif name == "val":
            return self.table_val
        elif name == "test":
            return self.table_test

    def alla(self):
        pass

    def new_sort_file(self):
        if not self.sama_data.is_correct_file:
            return
        file = az_file_dialog(self, self.tr("Create new sorting train/validation project *.sort file"),
                              self.settings.read_last_dir(),
                              dir_only=False, file_to_save=True, filter="Sort (*.sort)",
                              initial_filter="sort (*.sort)")
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
            return
        helper.save(self.sort_file, self.sort_data.data)
        self.signal_message.emit(self.tr(f"Train-val sorting project saved: &{self.sort_file}"))

    def load_sort_project(self, path):
        """Загрузка проекта сортировки датасета"""
        # TODO: проверку файла, сообщения для пользователя
        sort_data = DatasetSortHandler()  # создаем объект сортировщика
        sort_data.load_from_file(path)  # заполняем его данными

        if sort_data.is_correct_file:  # если всё хорошо, то загружаем
            self.sort_file = path
            self.sort_data = sort_data
            self.settings.write_sort_file_input(path)  # записываем удачный файл для последующего автооткрытия
            self.ti_tb_sort_open.setText(path)
            self.update_sort_data_tables()  # заполняем таблицы
            self.signal_message.emit(self.tr(f"Train-val sorting project load: {path}"))
        else:
            self.ti_tb_sort_open.clear()  # Очищаем поле с файлом, что выбрал пользователь, т.к. файл не корректен

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
        self.ti_tb_sort_open.setEnabled(self.sort_mode)
        self.ti_tb_sort_save.setEnabled(self.sort_mode)
        self.ti_tb_sort_new.setEnabled(self.sort_mode)
        self.ti_tb_sort_add_to_train.setEnabled(self.sort_mode)
        self.ti_tb_sort_add_to_val.setEnabled(self.sort_mode)
        self.ti_tb_sort_remove_from_train.setEnabled(self.sort_mode)
        self.ti_tb_sort_remove_from_val.setEnabled(self.sort_mode)
        self.ti_tb_sort_cook.setEnabled(self.sort_mode)
        self.ti_tb_sort_smart.setEnabled(self.sort_mode)
        if self.sort_mode:
            if not silent:
                self.signal_message.emit(self.tr("Toggle train/val sort mode on"))
        else:
            if not silent:
                self.signal_message.emit(self.tr("Toggle train/val sort mode off"))
        self.table_image_filter_changed()  # отфильтровать вывод в таблице фильтрата

    def toggle_log(self):
        if self.btn_log_and_status.isChecked():
            self.bottom_dock.setHidden(False)
        else:
            self.bottom_dock.setHidden(True)

    def log_clear(self):
        self.log.clear()

    def log_change_data(self, message):
        self.change_log_icon("red")
        current_time = datetime.now().time().strftime("%H:%M:%S")
        message = current_time + ": " + message
        self.log.setPlainText(self.log.toPlainText() + message + "\n")

    def change_log_icon(self, color):
        if color == "red":
            icon = "circle_red"
        elif color == "green":
            icon = "circle_green"
        else:
            icon = "circle_grey"
        self.btn_log_and_status.setIcon(new_icon(icon))

    def attr_actions_disable(self, message):  # сброс всех форм при загрузке, а также отключение инструментов
        self.current_file = None
        self.toggle_tool_buttons(False)
        self.clear_dataset_info()
        self.table_widget.clear_table()
        self.signal_message.emit(message)

    def clear_dataset_info(self):
        for label in self.labels_dataset_val:
            label.setText("-")

    def toggle_tool_buttons(self, b):  # отключаем инструменты для датасета
        for button in self.common_buttons:
            button.setEnabled(b)

    def attr_load_projects_data(self):
        if len(self.file_json.text()) < 5:  # недостойно внимания
            return
        self.load_project(self.file_json.text(), self.tr(f"Loaded project file: {self.file_json.text()}"))

    def load_project(self, filename, message):  # загрузка проекта
        self.sama_data = None  # очищаем
        self.sama_data = DatasetSAMAHandler()
        self.unload_sort_file()  # выгружаем файлы сортировки, если они были загружены
        self.sama_data.load(filename)
        self.log_clear()
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
        self.load_dataset_info()  # загружаем общее инфо о датасете
        self.table_widget.load_table_data(self.sama_data)  # обновляем данные для таблицы
        self.original_image_data = None  # очищаем данные с исходными значениями
        self.load_image_data_model()  # загружаем таблицу изображений данные для таблицы
        self.log_change_data(message)
        self.change_log_icon("green")
        self.signal_message.emit(message)
        QtWidgets.QApplication.restoreOverrideCursor()

    def load_dataset_info(self):  # общая информация о датасете
        self.dataset_info_images_val.setText(str(self.sama_data.get_images_num()))
        self.dataset_info_labels_val.setText(str(self.sama_data.get_labels_count()))

        # рассчитаем ЛРМ
        min_lrm = float('inf')
        max_lrm = float('-inf')
        no_lrm = 0
        all_count = 0
        summ = 0
        count = 0

        for image in self.sama_data.data["images"]:
            res = self.sama_data.get_image_lrm(image)
            if res is not None:
                min_lrm = min(min_lrm, res)
                max_lrm = max(max_lrm, res)
                summ += res
                count += 1
            else:
                no_lrm += 1  # изображений без ЛРМ
            all_count += 1

        if all_count != no_lrm:
            # округляем всё с точностью до 2 знаков после запятой
            self.dataset_info_devi_lrm_val.setText(f"{round(min_lrm, 2):.2f}-{round(max_lrm, 2):.2f}")
            self.dataset_info_lrm_val.setText(f"{round(summ / count, 2):.2f}")

    def attrs_copy_project(self):  # копирование проекта
        file = az_file_dialog(self, self.tr("Make copy project file and load it"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="json (*.json)",
                              initial_filter="json (*.json)")
        if file is None:
            return
        if len(file) < 1:  # если всё в порядке...
            return
        # ...копируем и загружаем
        import shutil
        shutil.copyfile(self.current_file, file)
        self.load_project(file, self.tr(f"Project was copied and loaded to: {file}"))

    def attrs_save_palette(self):  # сохранение палитры
        """Извлечь и сохранить палитру из проекта SAMA"""
        data = dict()
        colors = self.sama_data.data["labels_color"]
        data["labels_color"] = colors
        file = az_file_dialog(self, self.tr("Save project SAMA *.json palette"), self.settings.read_last_dir(),
                              dir_only=False, file_to_save=True, filter="Palette (*.palette)",
                              initial_filter="palette (*.palette)")
        if file is None:
            return
        if len(file) > 0:
            helper.save(file, data, 'w+')  # сохраняем файл как палитру
        self.signal_message.emit(self.tr(f"Palette saved to: &{file}"))

    def attrs_apply_palette(self):  # применение палитры
        """Применить палитру к файлу проекта SAMA"""
        # загружаем файл с палитрой
        sel_file = az_file_dialog(self, self.tr("Apply palette file to current project"), self.settings.read_last_dir(),
                                  dir_only=False, filter="Palette (*.palette)", initial_filter="palette (*.palette)")
        if not helper.check_files(sel_file):
            return
        palette = helper.load(sel_file[0])
        colors = palette["labels_color"]  # выгружаем цвета палитры
        input_colors = self.sama_data.data["labels_color"]

        # обходим ключи
        for color in input_colors:  # палитра текущего проекта SAMA
            if color in colors:  # цвет для метки в текущем проекте есть в загруженной палитре
                input_colors[color] = colors[color]
        # применяем и перезагружаем файл, чтобы поменялась палитра
        self.save_and_reload(self.current_file, self.tr(f"Palette was apply, project was reload: {self.current_file}"))

    def attrs_apply_lrm_from_folder(self):
        """Поиск в выбранном каталоге файлов *.map с записанными значениями ЛРМ и установка соответствующим данным
        изображений в проекте ЛРМ"""
        sel_dir = az_file_dialog(self, self.tr("Directory with map files containing GSD data about "),
                                 self.settings.read_last_dir(), dir_only=True)
        if not helper.check_file(sel_dir):
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        lrms = {}  # словарь ("имя изображения": ЛРМ(float))

        files = [f for f in os.listdir(sel_dir) if f.endswith("map")]  # собираем имена файлов
        for file in files:
            res = helper.get_file_line(os.path.join(sel_dir, file), 54)  # в файлах MAP за ЛРМ отвечает 54 строка
            if res is not None:
                lrm = float(res.split(',')[1])
                image_name = os.path.join(os.path.splitext(file)[0]) + ".jpg"
                lrms[image_name] = lrm

        good_files, bad_files = self.sama_data.set_lrm_for_all_images(lrms, no_image_then_continue=True)
        # print(f"good: {good_files}")
        # print(f"badb: {bad_files}")
        QtWidgets.QApplication.restoreOverrideCursor()
        self.log_change_data(self.tr(f"Set GSD for {len(good_files)} images"))
        self.signal_message.emit(self.tr(f"Set GSD for {len(good_files)} images"))

    def attrs_export(self):
        """ Экспорт табличных данных проекта SAMA в текстовый файл """
        file = az_file_dialog(self, self.tr("Export table data to text file"), self.settings.read_last_dir(),
                              dir_only=False, remember_dir=False, file_to_save=True, filter="txt (*.txt)",
                              initial_filter="txt (*.txt)")
        if not helper.check_file(file):
            return
        if len(file) > 0:  # сохраняем в файл, при этом пропускаем определенные столбцы
            # TODO: сделать экспорт данных об разрешении
            if save_via_qtextstream(self.table_widget, file, [7, 8]):
                self.signal_message.emit(self.tr(f"Table data export to: {file}"))

    def sef_image_data_model(self, data):
        """Создание и установка модели в таблице фильтрата, по исходным данным, настройка ui таблицы"""
        # TODO: сортировку TableView

        if len(data) < 1:
            self.image_table.setModel(AzTableModel())
        else:
            model_sorting = AzTableModel(data, self.image_headers)  # модель для данных фильтрата
            self.image_table.setModel(model_sorting)

        # настраиваем отображение
        if self.image_table.model().columnCount() > 0:  # для столбцов
            header = self.image_table.horizontalHeader()
            for col in range(model_sorting.columnCount()):
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        if self.image_table.model().rowCount() > 0:  # для строк
            for row in range(self.image_table.model().rowCount()):  # выравниваем высоту
                self.image_table.setRowHeight(row, ROW_H)

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
        self.sef_image_data_model(data)  # загружаем и устанавливаем модель

    def load_image_data_model(self):
        """Первичное заполнение таблицы фильтрата данными"""
        # Данные - массив [["object1", "image_name1", "label1, "item1"][...]]
        if self.original_image_data is None:
            data = self.sama_data.get_model_data()
            self.original_image_data = data
        self.fill_image_data_filters()  # заполняем параметрами для сортировки (фильтрами)
        self.sef_image_data_model(data)  # загружаем и устанавливаем модель

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

    def get_filtered_model_data(self, object_name=None, label_name=None, pattern=r"^([^_]+)_([^_]+)"):
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

    def unload_sort_file(self):
        """Выгрузка данных режима сортировщика"""
        if self.sort_file:  # имеется файл сортировки
            if self.sort_mode:
                self.ti_tb_sort_mode.setChecked(False)  # отключаем инструмент
                self.image_table_toggle_sort_mode(silent=True)  # выключаем режим сортировки в тихом режиме
            self.sort_file = None  # убираем данные
            self.ti_tb_sort_open.clear()
            self.sort = None
            self.table_statistic.setModel(None)
            self.table_train.setModel(None)
            self.table_val.setModel(None)
            # self.table_statistic.setModel(None) # Table Test

    def smart_sort(self):
        """Интеллектуальная автоматизированная сортировка"""
        pass

    def cook_dataset(self):
        """Сортировка датасета в соответствии с выбранными параметрами"""
        # входной каталог:
        input_dir = "d:\\data_sets\\oil_refinery\\yolo_seg\\alfa\\"

        # выходной каталог:
        output_dir = "d:\\data_sets\\oil_refinery\\yolo_seg\\"
        os.makedirs(output_dir, exist_ok=True)

        # сначала базовые каталоги "images" и "labels"
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        labels_dir = os.path.join(output_dir, 'labels')
        os.makedirs(labels_dir, exist_ok=True)

        # создаем каталоги "test", "train" и "val"
        for subdir in ['test', 'train', 'val']:
            images_subdir = os.path.join(images_dir, subdir)
            os.makedirs(images_subdir, exist_ok=True)
            labels_subdir = os.path.join(labels_dir, subdir)
            os.makedirs(labels_subdir, exist_ok=True)

        train = self.move_sorting_files(input_dir, output_dir, "train", self.sort_data.get_images_names("train"))
        val = self.move_sorting_files(input_dir, output_dir, "val", self.sort_data.get_images_names("val"))
        self.signal_message.emit(self.tr(f"Moving complete. Success moved {train[0] + val[0]} files. "
                                         f"Errors for {train[1] + val[1]} files"))

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

            try:
                shutil.move(src_txt, dst_txt)
                shutil.move(src_jpg, dst_jpg)
                good_counts += 1
            except FileNotFoundError:
                bad_counts += 1
        return [good_counts, bad_counts]

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabAttributesUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes
        self.table_widget.translate_ui()
        self.label_project.setText(self.tr("Path to file project *.json:"))
        self.dataset_info_images_desc.setText(self.tr("Numbers of images: "))
        self.dataset_info_labels_desc.setText(self.tr("Numbers of labels: "))
        self.dataset_info_lrm_desc.setText(self.tr("Average GSD:"))
        self.dataset_info_devi_lrm_desc.setText(self.tr("Deviation GSD:"))
        self.btn_copy.setToolTip(self.tr("Make copy of current project"))
        self.btn_export.setToolTip(self.tr("Export current project info"))
        self.btn_save_palette.setToolTip(self.tr("Save palette from current project"))
        self.btn_apply_palette.setToolTip(self.tr("Apply palette for current project"))


# ----------------------------------------------------------------------------------------------------------------------


class AzSortTable(QtWidgets.QWidget):
    """Testestet"""
    def __init__(self, color, sort_type="train",  parent=None):
        super().__init__(parent)

        # создаем таблицу QTableView
        self.table_view = QtWidgets.QTableView()

        h_lay_train = QtWidgets.QHBoxLayout()
        self.ti_train_label = QtWidgets.QLabel(self.tr("Train table:"))
        self.ti_tb_sort_add_to_train = new_button(self, "tb", "train", "glyph_add2", color=color,
                                                  slot=self.add_to_sort_table, tooltip=self.tr("Add to train"),
                                                  icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)
        self.ti_tb_sort_remove_from_train = new_button(self, "tb", "train", "glyph_delete2", color=color,
                                                       slot=self.remove_from_sort_table,
                                                       tooltip=self.tr("Remove selected rows from train"),
                                                       icon_size=config.UI_AZ_PROC_ATTR_IM_ICON_SIZE)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)  # горизонтальный спейсер
        h_lay_train.addWidget(self.ti_train_label)
        h_lay_train.addWidget(self.ti_tb_sort_add_to_train)
        h_lay_train.addWidget(spacer)
        h_lay_train.addWidget(self.ti_tb_sort_remove_from_train)

        # итоговая настройка компоновки
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(h_lay_train)
        layout.addWidget(self.table_view, 1)  # делаем доминантным

        # Создаем модель данных
        self.model = MyTableModel()

        # Устанавливаем модель данных для QTableView
        self.table_view.setModel(self.model)

        # Разрешаем выделение строк
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QTableView.SelectionMode.MultiSelection)

    def add_to_sort_table(self):
        print("add_to_sort_table")
        pass

    def remove_from_sort_table(self):
        print("remove_from_sort_table")
        pass


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data=[], headers=[]):
        super().__init__()
        self._data = data
        self._headers = headers

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()
            value = self._data[row][column]
            return value

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        if self._data:
            return len(self._data[0])
        else:
            return 0

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self._headers[section]

# ----------------------------------------------------------------------------------------------------------------------

class AzTableAttributes(QtWidgets.QTableWidget):
    """
    Таблица для взаимодействия с общей статистикой данных проекта SAMA *.json:
    headers - перечень заголовков (может быть переводимым, если translate_headers = True*), *пока не реализовано
    special_cols - словарь особых столбцов: ключ - номер столбца, значение - acton или color; может быть None, следует
        помнить, что нумерация идет с 0.
    data - данные для таблицы, если тип данных DatasetSAMAHandler, то записываются в self.my_data.
    Пример: tb = AzTableAttributes(headers=self.headers, special_cols={5: "color", 6: "action"},data=None, parent=self)
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    signal_data_changed = QtCore.pyqtSignal(str)  # сигнал об изменении в данных

    def __init__(self, headers=None, special_cols=None, data=None, parent=None,
                 translate_headers=False, current_file=None):
        # создать заголовки, построить ячейки, заполнить данными, заполнить особыми столбцами
        super(AzTableAttributes, self).__init__(parent)
        self.col_color = None  # столбец цвета
        self.current_file = current_file
        self.special_cols = special_cols
        self.translate_headers = translate_headers  # надобность перевода
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)  # заголовки
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # выделение построчно
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # отключаем редактирование
        self.setSortingEnabled(True)  # включаем сортировку
        self.setAlternatingRowColors(True)  # включаем чередование цветов
        self.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.Alignment(QtCore.Qt.TextFlag.TextWordWrap))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setColumnWidth(0, int(self.width() * 0.23))  # устанавливаем у первого столбца ширину в 23% от общей ширины

    def clear_table(self):  # простая очистка таблицы
        self.setRowCount(0)

    def set_special_cols(self):  # установка особых типов столбцов: action - меню; color - цвет;
        for column, item_type in self.special_cols.items():
            if item_type == "color":
                for row in range(self.rowCount()):
                    self.setCellWidget(row, column, self.add_color_button())
            elif item_type == "action":
                for row in range(self.rowCount()):
                    self.setCellWidget(row, column, self.add_action_button())

    def add_action_button(self):  # добавление кнопки меню
        act_button = new_button(self, "tb", icon="glyph_menu", color=the_color, tooltip=self.tr("Select action"),
                                icon_size=14)
        act_button.clicked.connect(self.show_context_menu)
        # act_button.clicked.connect(lambda ch, row=row: self.show_context_menu(row))
        return act_button

    def add_color_button(self):  # добавление цветной кнопки выбора цвета
        color_button = new_button(self, "tb", tooltip=self.tr("Select color"))
        color_button.setStyleSheet("QToolButton { background-color: rgb(0, 0, 0); }")  # по умолчанию черного цвета
        color_button.clicked.connect(self.change_color)
        # color_button.clicked.connect(lambda ch, btn=color_button, row=row: self.change_color(btn, row))
        return color_button

    def show_context_menu(self):
        """Дополнительное меню действий с именами меток/классами"""
        button = self.sender()  # определяем от кого пришёл сигнал
        index = self.indexAt(button.pos())  # вот и индекс (проклятье, часа четыре потратил на эти 3 строчки!)
        row = index.row()

        menu = QtWidgets.QMenu()
        rename_act = new_act(self, self.tr(f"Rename"), "glyph_signature", the_color,
                             tip=self.tr("Rename current label"))
        rename_act.triggered.connect(lambda ch, the_row=row: self.label_rename(row))

        delete_act = new_act(self, self.tr("Delete"), "glyph_delete2", the_color, tip=self.tr("Delete current label"))
        delete_act.triggered.connect(lambda ch, the_row=row: self.label_delete(row))

        merge_act = new_act(self, self.tr("Merge"), "glyph_merge", the_color,
                            tip=self.tr("Merge current label to other label"))
        merge_act.triggered.connect(lambda ch, the_row=row: self.label_merge(row))

        acts = [rename_act, merge_act, delete_act]  # перечень наших действий
        menu.addActions(acts)

        pos = QtGui.QCursor.pos()
        menu.exec_(pos)

    def load_table_data(self, data):
        self.clear_table()
        if isinstance(data, DatasetSAMAHandler):  # установка данных SAMA, если они переданы
            self.my_data = data
            self.horizontalHeader().setFixedHeight(36)  # для SAMA
            self.load_sama_data()
        else:
            # заглушка на другие типы данных
            pass

    def load_sama_data(self):
        labels = self.my_data.get_labels()
        self.setRowCount(len(labels))  # число строк
        self.col_color = None  # по умолчанию "цветного" столбца нет

        # устанавливаем особые столбцы
        if self.special_cols is not None and self.my_data is not None:  # в конец, т.к. изначально установим цвет
            self.set_special_cols()
            self.col_color = next((k for k, v in self.special_cols.items() if v == "color"), None)  # номер столбца

        stat = self.my_data.calc_stat()  # рассчитываем статистику
        self.setSortingEnabled(False)  # обязательно отключить сортировку, иначе случится дичь
        for row, name in enumerate(labels):
            if self.col_color:  # заполнение кнопки цветом
                color_tuple = self.my_data.get_label_color(name)
                color = QtGui.QColor(*color_tuple)
                button = self.cellWidget(row, self.col_color)
                button.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
            # имя класса/метки
            self.add_item_text(row, 0, name, QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
            self.add_item_number(row, 1, stat[name]['count'])  # количество объектов/меток
            self.add_item_number(row, 2, stat[name]['frequency'], 1)  # частота встречаемости на изображении
            self.add_item_number(row, 3, stat[name]['percent'], 2)  # проценты от общего
            self.add_item_number(row, 4, stat[name]['size']['mean'], 1)  # средний размер
            self.add_item_number(row, 5, stat[name]['size']['std'], 1)  # СКО размера
        self.setSortingEnabled(True)
        for row in range(self.rowCount()):  # выравниваем высоту
            self.setRowHeight(row, ROW_H)

    def add_item_text(self, row, col, text,
                      align=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter):
        """ Установка текстовых значений.
        row - строка, col - столбце,  text - текстовое значение, align - расположение значения по
        горизонтали | вертикали типа "Qt.AlignmentFlag"
        """
        item = QtWidgets.QTableWidgetItem(text)
        item.setTextAlignment(align)
        self.setItem(row, col, item)

    def add_item_number(self, row, col, number, acc=0,
                        align=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter):
        """ Установка числовых значений.
        row - строка, col - столбце, number - отображаемое число, acc - знаки с точностью после запятой
        align - расположение значения по горизонтали | вертикали типа "Qt.AlignmentFlag"
        """
        item = QtWidgets.QTableWidgetItem()
        item.setData(QtCore.Qt.ItemDataRole.EditRole, round(float(number), acc))
        item.setTextAlignment(align)
        self.setItem(row, col, item)

    def fill_column(self, col, text_data):  # заполнение столбца данными
        for row, text in enumerate(text_data):
            new_item = QtWidgets.QTableWidgetItem(text)
            self.setItem(row, col, new_item)

    def change_color(self):  # изменение цвета
        button = self.sender()  # определяем от кого пришёл сигнал
        index = self.indexAt(button.pos())
        row = index.row()
        name = self.item(row, 0).text()

        if self.col_color is None:
            return
        button = self.cellWidget(row, self.col_color)  # узнаем по какой кнопке щелкнули
        if button is None:
            self.signal_message.emit(self.tr("Something goes wrong. Can't assign a button"))
            return
        color_dialog = QtWidgets.QColorDialog(self)  # создаём и настраиваем диалог цвета
        color_dialog.setWindowTitle(self.tr("Select label color"))
        color_dialog.setCurrentColor(button.palette().color(button.backgroundRole()))  # начальный цвет
        result = color_dialog.exec_()  # запускаем
        if result != QtWidgets.QDialog.Accepted:
            return
        color = color_dialog.selectedColor()
        if color.isValid():
            button.setStyleSheet(
                f"QToolButton {{ background-color: rgb({color.red()}, {color.green()}, {color.blue()}); }}")
        self.my_data.set_label_color(name, [color.red(), color.green(), color.blue()])  # устанавливаем цвет и в данных
        self.signal_message.emit(
            self.tr(f"Label '{name}' color was changed to 'rgb({color.red()}, {color.green()}, {color.blue()})'"))
        self.signal_data_changed.emit(self.tr(f"Label color was changed to 'rgb({color.red()}, {color.green()}, "
                                              f"{color.blue()})'"))

    def label_rename(self, row):
        """ Перечень действий: переименовать класс"""
        names = self.my_data.get_labels()  # набор исходных имён
        current_name = self.item(row, 0).text()
        if current_name not in names:
            self.signal_message.emit(self.tr("Something goes wrong. Check input data."))
        dialog = AzInputDialog(self, 1, [self.tr("Enter new label name:")], input_type=[0],
                               window_title=f"Rename label '{self.item(row, 0).text()}'",
                               cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные

        # проверки
        if result is None:
            return
        if len(result) < 1:
            return
        if result[0] in names:
            self.signal_message.emit(
                self.tr(f"The specified name '{result[0]}' is present in the dataset, rename was canceled."))
            return
        self.my_data.change_name(current_name, result[0])
        self.item(row, 0).setText(result[0])
        self.signal_message.emit(self.tr(f"Objects with label '{current_name}' was renamed to '{result[0]}'"))
        self.signal_data_changed.emit(self.tr(f"Objects with label '{current_name}' was renamed to '{result[0]}'"))

    def label_delete(self, row):
        """ Перечень действий: удалить метку"""
        name = self.item(row, 0).text()
        dialog = az_custom_dialog(self.tr("Label deleting"),
                                  self.tr(f"Are you sure you want to delete all objects related to label '{name}'?"),
                                  parent=self)
        if dialog != 1:  # если не "утверждение", то выходим
            return

        if not self.my_data.filename:  # ошибка, дальше даже не стоит продолжать
            self.signal_message.emit(self.tr("Something goes wrong."))
            return
        self.my_data.delete_data_by_class_name(name)  # удаляем данные
        self.removeRow(row)
        self.signal_message.emit(self.tr(f"Objects with label '{name}' was deleted"))
        self.signal_data_changed.emit(self.tr(f"Objects with label '{name}' was deleted"))

    def label_merge(self, row):
        """Перечень действий: слить с другой меткой"""
        if self.my_data is None:
            return
        name = self.item(row, 0).text()  # имя текущей метки
        names = copy.copy(self.my_data.get_labels())  # имена всех меток
        if len(names) < 2:
            self.signal_message.emit(self.tr("There are not enough labels for merging."))
            return
        names.remove(name)  # сделать копию! ибо будет удаление

        dialog = AzInputDialog(self, 1, [self.tr(f"Select the label {name} to merge with:")],
                               self.tr("Merge labels"), input_type=[1],
                               combo_inputs=[names], cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные
        if result is None:
            return
        if len(result) < 1:
            return
        self.my_data.change_data_class_from_to(name, result[0])
        self.removeRow(row)
        self.signal_message.emit(self.tr(f"Merged object with labels '{name}' to '{result[0]}'"))
        self.signal_data_changed.emit(self.tr(f"Merged object with labels '{name}' to '{result[0]}'"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzTableAttributes", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes - AzTableAttributes
        self.setToolTip(self.tr("Data by classes (labels) of the dataset"))
        # Заголовки таблицы
        if self.translate_headers:
            pass
        # TODO: headers


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TabAttributesUI()
    window.show()
    sys.exit(app.exec_())
