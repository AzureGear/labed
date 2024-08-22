from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper, config, natural_order
from utils.sama_project_handler import DatasetSAMAHandler
from utils.az_dataset_sort_handler import DatasetSortHandler
from ui import new_act, new_button, new_icon, coloring_icon, new_text, new_label_icon, AzButtonLineEdit, \
    az_file_dialog, AzInputDialog
from ui import save_via_qtextstream, setup_dock_widgets
from ui import AzSortTable, AzTableModel, AzTableAttributes, AzSortingDatasetDialog
import os
import shutil
from datetime import datetime

ROW_H = 16
the_color = UI_COLORS.get("processing_color")
color_train = UI_COLORS.get("train_color")
color_val = UI_COLORS.get("val_color")
color_test = UI_COLORS.get("test_color")


# TODO: случайное выделение указанных% от группы
# TODO: инструмент добавить объекты уже имеющихся групп
# TODO: переключить вид на просмотр групп
# TODO: добавить инструмент назначения Разметчика
# TODO: рассчитать баланс датасета

# ----------------------------------------------------------------------------------------------------------------------

class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с Атрибутивными данными проектов разметки
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabAttributesUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = self.tr("Attributes")

        if color_active:
            self.icon_active = coloring_icon("glyph_attributes", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_attributes", color_inactive)

        self.current_file = None  # текущий файл проекта SAMA
        self.sort_file = None  # текущий файл сортировки
        self.sort_mode = False  # режим сортировки
        self.sort_dialog = None # диалог сортировки

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
        # self.setStyleSheet("QWidget { border: 1px solid yellow; }")  # проверка отображения виджетов

        # указываем инструменты, которые должны выключаться
        self.special_tools = [self.ti_cbx_sel_obj, self.ti_cbx_sel_class, self.ti_tb_sort_mode,
                              self.tb_edit_project_descr, self.ti_pb_sel_clear_selection, self.ti_pb_sel_clear_filters]
        # настраиваем все виджеты
        setup_dock_widgets(self, ["bottom_dock"], config.UI_BASE_ATTRS)
        self.image_table_toggle_sort_mode()  # запускаем, чтобы привести в порядок ui инструментов таблицы сортировки

        # Signals
        self.table_widget.signal_message.connect(self.forward_signal)  # перенаправление сигнала в строку состояния
        self.table_widget.signal_data_changed.connect(self.log_change_data)  # запись информации в лог для пользователя

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

    def setup_caption_widget(self):
        self.btn_log_and_status = new_button(self, "tb", icon="circle_grey", color=None, icon_size=16,
                                             slot=self.toggle_log, checkable=True, tooltip=self.tr("Toggle log"))
        self.label_project = QtWidgets.QLabel("Path to file project (*.json:)")
        self.file_json = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Load dataset SAMA project"),
                                          read_only=True, dir_only=False, filter=self.tr("Projects files (*.json)"),
                                          slot=self.attr_load_projects_data,
                                          initial_filter="json (*.json)")
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.btn_log_and_status)
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
        hlay.addWidget(spacer)
        return hlay

    def setup_up_central_widget(self):
        """Настройка интерфейса для таблицы статистики и перечня инструментов (центральный виджет)"""
        self.common_headers = [self.tr("Count of\nimages: "), self.tr("Count of\nlabels: "),
                               self.tr("Average\nGSD: "), self.tr("Deviation\nGSD: ")]
        self.common_table = QtWidgets.QTableView()
        self.common_table.setFixedHeight(70)
        # информация о датасете: количество снимков в датасете, количество меток, среднее ЛРМ, девиация ЛРМ
        self.common_data = [["-", "-", "-", "-"]]
        self.project_label = new_text(self.tr("Project description:"))  # кнопка редактирования описания проекта
        self.tb_edit_project_descr = new_button(self, "tb", None, "glyph_signature", the_color, self.toggle_edit_descr,
                                                True, tooltip=self.tr("Toggle edit project description"))
        self.project_description = QtWidgets.QTextEdit()
        self.project_description.setReadOnly(True)
        hlay_descr = QtWidgets.QHBoxLayout()
        hlay_descr.addWidget(self.project_label, 1)
        hlay_descr.addWidget(self.tb_edit_project_descr)
        vlay_table_descr = QtWidgets.QVBoxLayout()
        vlay_table_descr.addWidget(self.common_table)
        vlay_table_descr.addLayout(hlay_descr)
        vlay_table_descr.addWidget(self.project_description)

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
                                        tooltip=self.tr("Set GSD data from map files in folder to current project"))
        self.btn_save = new_button(self, "tb", icon="glyph_save2", tooltip=self.tr("Save changes to the project"),
                                   slot=self.save, color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)
        self.btn_remove_empty = new_button(self, "tb", icon="glyph_clear", slot=self.remove_empty, color=the_color,
                                           tooltip=self.tr("Remove image entries with missing markup"),
                                           icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)
        self.btn_remove_imgs_records = new_button(self, "tb", icon="glyph_delete", slot=self.remove_imgs_records,
                                                  color=the_color, tooltip=self.tr("Remove image with pattern"),
                                                  icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)

        self.common_buttons = [self.btn_save, self.btn_save_palette, self.btn_apply_palette, self.btn_export,
                               self.btn_apply_lrm, self.btn_copy, self.btn_remove_empty, self.btn_remove_imgs_records]

        v_lay_buttons = QtWidgets.QVBoxLayout()
        for button in self.common_buttons:
            v_lay_buttons.addWidget(button)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        v_lay_buttons.addWidget(spacer)

        # заголовок для таблицы
        self.headers = [
            self.tr("Label name"), self.tr("Labels count"), self.tr("Frequency per 100 images"),
            self.tr("% total labels"), self.tr("Average area, pixels"), self.tr('SD of area, pixels'),
            self.tr("Balance"), self.tr("Color"), self.tr("Action")]

        # данные из проекта SAMA будут загружаться в DatasetSAMAHandler
        self.sama_data = DatasetSAMAHandler()  # делаем изначально пустым

        # данные из DatasetSAMAHandler будут отображаться в таблице
        self.table_widget = AzTableAttributes(headers=self.headers, special_cols={7: "color", 8: "action"},
                                              data=None, parent=self, color=the_color, row_h=ROW_H)  # таблица пустая

        header = self.table_widget.horizontalHeader()  # настраиваем отображение столбцов именно таблицы SAMA
        for column in range(self.table_widget.columnCount()):
            if column == 6:
                self.table_widget.setColumnWidth(column, 55)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            elif column == 7:
                self.table_widget.setColumnWidth(column, 45)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            elif column == 8:
                self.table_widget.setColumnWidth(column, 60)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            # else:
            #     header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)  # ResizeToContents
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

        # итоговая настройка ui центрального виджета
        layout_up = QtWidgets.QHBoxLayout()  # главный Layout, наследуемый класс
        layout_up.addWidget(self.table_widget, 5)  # делаем доминантным
        layout_up.addLayout(v_lay_buttons)  # добавляем ему расположение с кнопками и QLabel
        layout_up.addLayout(vlay_table_descr, 2)  # добавляем ему расположение с кнопками и QLabel
        container_up = QtWidgets.QWidget()
        container_up.setLayout(layout_up)
        return container_up

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
        self.ti_instruments = [self.sort_project_name, self.ti_tb_sort_open, self.ti_tb_sort_new, v_line,
                               self.ti_tb_toggle_tables, self.ti_tb_sort_save, v_line2, self.ti_tb_sort_smart,
                               self.ti_tb_sort_cook]

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

    def setup_log(self):
        """ Настройка интерфейса для лога """
        self.log = QtWidgets.QTextEdit(self)  # лог, для вывода сообщений.
        self.log.setReadOnly(True)
        self.bottom_dock = QtWidgets.QDockWidget()  # контейнер для информации о логе
        self.bottom_dock.setWidget(self.log)  # устанавливаем в контейнер QLabel
        self.bottom_dock.setWindowTitle("Log")
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)

    @QtCore.pyqtSlot(str)
    def forward_signal(self, message):  # перенаправление сигналов
        self.signal_message.emit(message)

    @QtCore.pyqtSlot(str)
    def default_dir_changed(self, path):
        # заглушка на смену каталога для выходных данных по умолчанию
        pass

    def toggle_edit_descr(self):
        """Переключение (с сохранением в SamaDataHandler) редактора описания проекта"""
        self.project_description.setReadOnly(not self.tb_edit_project_descr.isChecked())
        if self.project_description.isReadOnly():
            self.project_description.setStyleSheet("")
            if self.sama_data.is_correct_file:  # добавляем то, что было описано
                self.sama_data.set_project_description(self.project_description.toPlainText())
        else:
            if self.settings.read_ui_theme() == "light":
                self.project_description.setStyleSheet("background-color: lavenderblush;")
            else:
                self.project_description.setStyleSheet("background-color: indigo;")

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

    def save(self):
        self.save_and_reload(self.current_file, self.tr(f"Project was saved and reload: {self.current_file}"))

    def save_and_reload(self, file, message):
        self.sama_data.save(file)  # сохранение данных и перезагрузка данных
        self.load_project(file, message)

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

        for wid in self.sort_tables:  # устанавливаем флаг для виджетов таблиц сортировки
            wid.setEnabled(self.sort_mode)

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

    def clear_dataset_info(self):
        self.common_data = [["-", "-", "-", "-"]]
        self.common_model = AzTableModel(self.common_data, self.common_headers, no_rows_captions=True)
        self.common_table.setModel(self.common_model)
        for i in range(self.common_model.columnCount()):
            self.common_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def toggle_tool_buttons(self, flag):
        """Переключаем базовые и особые инструменты"""
        for button in self.common_buttons:
            button.setEnabled(flag)
        for item in self.special_tools:
            item.setEnabled(flag)

    def attr_actions_disable(self, message):  # сброс всех форм при загрузке, а также отключение инструментов
        self.current_file = None
        self.toggle_tool_buttons(False)
        self.clear_dataset_info()
        self.table_widget.clear_table()
        self.image_table.setModel(None)
        self.ti_cbx_sel_class.clear()
        self.ti_cbx_sel_obj.clear()
        self.signal_message.emit(message)

    def attr_load_projects_data(self):
        if len(self.file_json.text()) < 5:  # недостойно внимания
            return
        self.load_project(self.file_json.text(), self.tr(f"Loaded project file: {self.file_json.text()}"))

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
        self.signal_message.emit(self.tr(f"Palette saved to: {file}"))

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

    def load_dataset_info(self):  # общая информация о датасете
        self.common_data.clear()

        # Определяем общую информацию по датасету. Сначала рассчитаем ЛРМ
        min_lrm = float('inf')
        max_lrm = float('-inf')
        no_lrm, all_count, summ, count = 0, 0, 0, 0

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

        images_count = self.sama_data.get_images_num()  # количество снимков в датасете
        labels_count = self.sama_data.get_labels_count()  # количество меток
        # округляем всё с точностью до 2 знаков после запятой
        lrm = f"{round(summ / count, 2):.2f}"  # среднее ЛРМ
        min_max_lrm = f"{round(min_lrm, 2):.2f}-{round(max_lrm, 2):.2f}"  # девиация ЛРМ
        if all_count != no_lrm:  # данные в наличии
            self.common_data = [[images_count, labels_count, lrm, min_max_lrm]]
        else:  # данных нет, ставим прочерк
            self.common_data = [[images_count, labels_count, "-", "-"]]

        self.common_model = AzTableModel(self.common_data, self.common_headers, no_rows_captions=True)
        self.common_table.setModel(self.common_model)
        for i in range(self.common_table.model().columnCount()):
            self.common_table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def load_project(self, filename, message):  # загрузка проекта
        self.sama_data = DatasetSAMAHandler()
        self.unload_sort_file()  # выгружаем файлы сортировки, если они были загружены
        self.sama_data.load(filename)
        self.log_clear()
        self.toggle_descr()  # настраиваем ui описания проекта
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
        if self.sama_data.get_project_description() is not None:  # загрузка описания проекта
            self.project_description.setText(self.sama_data.get_project_description())
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

    def toggle_descr(self):
        self.project_description.clear()  # очищаем текст
        if self.tb_edit_project_descr.isChecked():  # остался включённым режим редактирования
            self.tb_edit_project_descr.animateClick(0)

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
            sel_rows = self.get_selected_rows(self.image_table, 1)  # нас интересуют выделенные строки 2 столбца
            return sender, sel_rows

        if check_out:
            wid = self.get_table(sender)  # определение виджета и таблицы
            # проверка наличие выделенных строк
            if wid.table_view is None or not wid.table_view.selectionModel().hasSelection():
                return None, None  # нет выделенных элементов либо мистика
            sel_rows = self.get_selected_rows(wid.table_view, 0)  # для удаления - 1 столбец
            return sender, sel_rows

    def get_rows_by_group(self, data, source):
        import re
        # сначала определяем таблицу
        source_table = None
        if source == "unsort":
            source_table = self.image_table
            target_column = 1  # значащий столбец таблицы
        else:
            for wid in self.sort_tables:
                if source == wid.sort_type:
                    source_table = wid.table_view
                    target_column = 0  # значащий столбец таблицы

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
            data = self.get_rows_by_group(data, source)
        self.sort_data.move_rows_by_images_names(source, target, data, use_group)  # переносим объекты
        self.update_sort_data_tables()  # обновляем таблицы сортировки train/val
        self.table_image_filter_changed()  # обновляем таблицу фильтрата

    def add_to_sort_table(self):
        """
        Добавление в сортировочные таблицы строк из table_image. Производится перемещение записей в классе
        DatasetSortHandler из "unsort" в выбранную таблицу Train, Sort или Val.
        """
        sender, sel_rows = self.identify_sender_get_rows(check_in=True)
        if sel_rows:
            self.transfer_data("unsort", sender, sel_rows)

    def add_group_to_sort_table(self):
        """
        Групповое добавление в сортировочные таблицы строк из table_image: перемещение записей в классе
        DatasetSortHandler из "unsort" в выбранную таблицу Train, Sort или Val всех изображений, относящихся 
        к выбранной группе.
        """
        sender, sel_rows = self.identify_sender_get_rows(check_in=True)
        if sel_rows:
            self.transfer_data("unsort", sender, sel_rows, use_group=True)

    def remove_from_sort_table(self):
        """
        Удаление строк из сортировочной таблицы и в классе DatasetSortHandler. Перемещение удаленных строк в table_image
        """
        sender, sel_rows = self.identify_sender_get_rows(check_out=True)  # получаем отправителя и строки
        if sel_rows:
            self.transfer_data(sender, "unsort", sel_rows)

    def remove_group_from_sort_table(self):
        """
        Групповое удаление из сортировочной таблицы и в классе DatasetSortHandler. Перемещение удаленных строк
        в table_image.
        """
        sender, sel_rows = self.identify_sender_get_rows(check_out=True)  # получаем отправителя и строки
        if sel_rows:
            self.transfer_data(sender, "unsort", sel_rows, use_group=True)

    def update_sort_data_tables(self):
        """Заполнение таблиц сортировки данными сортировщика DatasetSortHandler"""
        for wid in self.sort_tables:  # устанавливаем последовательно для каждой таблицы
            # нам нужны данные [[data1], [data2], ...], а не [data1, data2, ...]
            wid.core_model.setData([[item] for item in self.sort_data.get_images_names(wid.sort_type)])
            wid.table_view.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)  # сортируем по возрастанию

            wid.align_rows_and_cols()  # выровняем строки и столбцы
        self.set_sort_data_statistic()

    def get_table(self, name):
        """Определение таблицы сортировки по значению сигнала кнопки"""
        for wid in self.sort_tables:
            if wid.sort_type == name:
                return wid

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

    def smart_sort(self):
        """Автоматизированная сортировка"""
        if not self.sort_data:
            return

        result = None
        if self.sort_data.is_correct_file and len(self.sort_data.data["full"]) > 2:
            # sort_dialog = AzSortingDatasetDialog(self, window_title=self.tr("Smart dataset sorting"))
            self.sort_dialog = AzSortingDatasetDialog(self.sort_data.data["full"], parent=self,
                                                 window_title=self.tr("Smart dataset sorting"))
            if self.sort_dialog.exec_() == QtWidgets.QDialog.Accepted:
                print("Dialog accepted")

        else:
            self.signal_message.emit(self.tr("The current data is not correct for smart sorting."))
            return

        # file = az_file_dialog(self, self.tr("save_stats"), self.settings.read_last_dir(),
        #                       dir_only=False, remember_dir=False, file_to_save=True, filter="json (*.json)",
        #                       initial_filter="json (*.json)")
        # if file is None:
        #     return
        # if len(file) < 1:  # если всё в порядке...
        #     return
        # data = self.sort_data.data["full"]
        # helper.save(file, data, 'w+')  # сохраняем файл как палитру
        # # print(self.sort_data.statistic["train"])
        # # print(self.sort_data.statistic["val"])
        # # print(self.sort_data.statistic["test"])
        # print(self.sort_data.data["full"])

    def cook_dataset(self):
        """Сортировка датасета в соответствии с выбранными параметрами"""
        # входной каталог:
        input_dir = "d:\\data_sets\\oil_refinery\\tank_exp\\full"

        # выходной каталог:
        output_dir = "d:\\data_sets\\oil_refinery\\yolo_seg\\tanks_1280"
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

    def remove_empty(self):
        """Удаление записей изображений с отсутствующей разметкой (очистка датасета)"""
        if not self.sama_data:
            return
        deleted = self.sama_data.clear_records_without_labeling_info()
        if deleted:
            message = self.tr(f"Removed: {len(deleted)} empty entries")
            self.log_change_data(message)
            self.signal_message.emit(message)
        else:
            self.signal_message.emit(self.tr("There are no images without markup to clear"))

    def remove_imgs_records(self):
        """Удаление записей изображений по шаблону, например: '125s_FRA, 147s_DEU', возвращает количество
        удалённых записей"""
        dialog = AzInputDialog(self, 1, [self.tr("Enter pattern ('125s_FRA, 147s_DEU', for example)")],
                               input_type=[0],
                               window_title=self.tr("Delete records images with pattern"),
                               cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные
        print(result)
        pattern_list = [item.strip() for item in result[0].split(',')]  # разделяем по запятым, удаляем пробелы
        deleted = self.sama_data.remove_records_with_pattern(pattern_list)  # удаляем записи из проекта
        if deleted:
            message = self.tr(f"Removed: {len(deleted)} images records")
            self.log_change_data(message)
            self.signal_message.emit(message)
        else:
            self.signal_message.emit(self.tr("There are no images with pattern to delete"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabAttributesUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes
        self.table_widget.translate_ui()
        self.table_widget.setHorizontalHeaderLabels(
            [self.tr("Label name"), self.tr("Labels count"), self.tr("Frequency per 100 images"),
             self.tr("% total labels"), self.tr("Average area, pixels"), self.tr('SD of area, pixels'),
             self.tr("Balance"), self.tr("Color"), self.tr("Action")])
        self.common_model.setHorizontalHeaderLabels([self.tr("Count of\nimages: "), self.tr("Count of\nlabels: "),
                                                     self.tr("Average\nGSD: "), self.tr("Deviation\nGSD: ")])
        self.model_image.setHorizontalHeaderLabels([self.tr("Group"), self.tr("Images"), self.tr("Label"),
                                                    self.tr("Number")])
        self.sort_widget_train.translate_ui()
        self.sort_widget_val.translate_ui()
        self.sort_widget_test.translate_ui()
        if self.sort_dialog:
            self.sort_dialog.translate_ui()
        self.label_project.setText(self.tr("Path to file project (*.json):"))
        self.btn_copy.setToolTip(self.tr("Make copy of current project"))
        self.btn_export.setToolTip(self.tr("Export current project info"))
        self.btn_save_palette.setToolTip(self.tr("Save palette from current project"))
        self.btn_apply_palette.setToolTip(self.tr("Apply palette for current project"))
        self.btn_save.setToolTip(self.tr("Save changes to the project"))
        self.btn_apply_lrm.setToolTip(self.tr("Set GSD data from map files in folder to current project"))
        self.btn_remove_empty.setToolTip(self.tr("Remove image entries with missing markup"))
        self.btn_remove_imgs_records.setToolTip(self.tr("Remove image with pattern"))

        self.tb_edit_project_descr.setToolTip(self.tr("Toggle edit project description"))
        self.project_label.setText(self.tr("Project description:"))

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

    # todo: перенести в другое место
    def find_by_label(self):
        val = "04-cat_crack"
        mylist = self.sama_data.get_images_by_label(val)
        print("list: ", mylist)


# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TabAttributesUI()
    window.show()
    sys.exit(app.exec_())
