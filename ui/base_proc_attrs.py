import copy

from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper, config
from utils.sama_project_handler import DatasetSAMAHandler
from ui import new_button, AzButtonLineEdit, coloring_icon, new_text, az_file_dialog, save_via_qtextstream, new_act, \
    AzInputDialog, az_custom_dialog, new_icon, setup_dock_widgets
import os

the_color = UI_COLORS.get("processing_color")


# ----------------------------------------------------------------------------------------------------------------------

class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
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

        self.current_file = None  # текущий файл

        # Настройка ui
        wid = QtWidgets.QWidget()
        self.setCentralWidget(wid)

        # Лог
        self.log = QtWidgets.QTextEdit(self)  # лог, для вывода сообщений.
        self.log.setReadOnly(True)
        self.top_dock = QtWidgets.QDockWidget("")  # контейнер для информации о логе
        self.top_dock.setWidget(self.log)  # устанавливаем в контейнер QLabel
        self.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.top_dock)
        setup_dock_widgets(self, ["top_dock"], config.UI_BASE_ATTRS)
        self.top_dock.setWindowTitle("Log")

        self.btn_log_and_status = new_button(self, "tb", icon="glyph_circle_grey", color=None, icon_size=16,
                                             slot=self.toggle_log, checkable=True, tooltip=self.tr("Toggle log"))
        self.label_project = QtWidgets.QLabel("Path to file project *.json:")
        self.file_json = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Load dataset SAMA project"),
                                          read_only=True, dir_only=False, filter=self.tr("Projects files (*.json)"),
                                          on_button_clicked_callback=self.attr_load_projects_data,
                                          initial_filter="json (*.json)")

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

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.btn_log_and_status)
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json)  # текущий проект
        hlay2 = QtWidgets.QHBoxLayout()
        hlay2.setSpacing(0)

        # информация о датасете: количество снимков в датасете, количество меток, среднее ЛРМ, девиация ЛРМ
        for i in range(4):
            hlay2.addWidget(self.labels_dataset_info[i])
            hlay2.addWidget(self.labels_dataset_val[i])

        #  Перечень действий с файлом проекта: копия+; экспорт+; сохранить палитру+; применить палитру+;
        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addLayout(hlay)
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
            self.tr("Label name"), self.tr("Number of labels"), self.tr("Frequency of appearance on the image"),
            self.tr("Percentage of total labels"), self.tr("Average area, pixels"), self.tr('SD of area, pixels'),
            self.tr("Balance"), self.tr("Color"), self.tr("Action")]

        # данные из проекта SAMA будут загружаться в DatasetSAMAHandler
        self.sama_data = DatasetSAMAHandler()  # делаем изначально пустым

        # данные из DatasetSAMAHandler будут отображаться в таблице
        self.table_widget = AzTableAttributes(headers=self.headers, special_cols={7: "color", 8: "action"},
                                              data=None, parent=self)  # и таблица тоже пустая

        header = self.table_widget.horizontalHeader()  # настраиваем отображение столбцов именно таблицы SAMA
        for column in range(self.table_widget.columnCount()):
            if column == 0:
                pass
                # header.setSectionResizeMode(column, QtWidgets.QHeaderView.Interactive)
            elif column == 6:
                self.table_widget.setColumnWidth(column, 55)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            elif column == 7:
                self.table_widget.setColumnWidth(column, 45)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            elif column == 8:
                self.table_widget.setColumnWidth(column, 45)
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
            else:
                header.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)  # ResizeToContents
        # header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # первый столбец доминантный

        # смотрим, есть ли в реестре файл, который запускали прошлый раз?
        if os.path.exists(self.settings.read_attributes_input()):
            self.load_project(self.settings.read_attributes_input(),
                              self.tr(f"Loaded las used project file: {self.file_json.text()}"))  # пробуем загрузить
        else:  # файла нет, тогда ограничиваем функционал
            self.toggle_tool_buttons(False)



        # итоговая настройка ui
        vlayout = QtWidgets.QVBoxLayout(self)  # главный Layout, наследуемый класс
        vlayout.addLayout(hlay_finish)  # добавляем ему расположение с кнопками и QLabel
        vlayout.addWidget(self.table_widget)
        wid.setLayout(vlayout)

        # Signals
        self.table_widget.signal_message.connect(self.forward_signal)
        self.table_widget.signal_data_changed.connect(self.log_change_data)
        # print("init, cur_file:", self.current_file)
        # print("init, sama_labels:", self.sama_data.get_labels())

    def forward_signal(self, message):  # перенаправление сигналов
        self.signal_message.emit(message)

    def save(self):
        self.save_and_reload(self.current_file, self.tr(f"Project was saved and reload: {self.current_file}"))

    def save_and_reload(self, file, message):
        self.log_clear()
        self.sama_data.save(file)  # сохранение данных и перезагрузка данных
        self.load_project(file, message)
        self.change_log_icon("green")

    def toggle_log(self):
        if self.btn_log_and_status.isChecked():
            self.top_dock.setHidden(False)
        else:
            self.top_dock.setHidden(True)

    def log_clear(self):
        self.log.clear()

    def change_log_icon(self, color):
        if color == "red":
            icon = "glyph_circle_red"
        elif color == "green":
            icon = "glyph_circle_green"
        else:
            icon = "glyph_circle_grey"
        self.btn_log_and_status.setIcon(new_icon(icon))

    def log_change_data(self, message):
        self.change_log_icon("red")
        self.log.setPlainText(self.log.toPlainText() + "\n" + message)

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
        self.load_dataset_info()  # загружаем общее инфо о датасете
        self.table_widget.load_table_data(self.sama_data)  # обновляем данные для таблицы
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

class AzTableAttributes(QtWidgets.QTableWidget):
    """
    Таблица для взаимодействия с QTabWidget для работы с MNIST:
    headers - перечень заголовков (может быть переводимым, если translate_headers = True).
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
            self.horizontalHeader().setFixedHeight(56)  # для SAMA высота 56
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
        color = QtWidgets.QColorDialog.getColor(button.palette().color(button.backgroundRole()), self,
                                                self.tr("Select label color"))  # стандартный диалог цвета
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
