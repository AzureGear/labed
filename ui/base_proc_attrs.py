from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, helper, config
from utils.sama_project_handler import DatasetSAMAHandler
from ui import new_act, new_button, new_icon, coloring_icon, new_text, AzButtonLineEdit, \
    az_file_dialog, AzInputDialog, AzCalcStdMean, setup_dock_widgets
from ui import AzTableModel, AzTableAttributes
import os
from datetime import datetime

ROW_H = 16
the_color = UI_COLORS.get("processing_color")
color_train = UI_COLORS.get("train_color")
color_val = UI_COLORS.get("val_color")
color_test = UI_COLORS.get("test_color")


# TODO: add calc mean, sd, for channels
# TODO: функцию переименования изображения - для изменения группировки и т.п., т.е. копирование и удаление старой разметки

# ----------------------------------------------------------------------------------------------------------------------
class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с Атрибутивными данными проектов разметки
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabAttributesUI, self).__init__(parent)
        # self.setStyleSheet("QWidget { border: 1px solid red; }")  # проверка отображения виджетов
        self.settings = AppSettings()  # настройки программы
        self.name = self.tr("Attributes")

        if color_active:
            self.icon_active = coloring_icon("glyph_attributes", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_attributes", color_inactive)

        self.current_file = None  # текущий файл проекта SAMA
        self.sort_file = None  # текущий файл сортировки
        self.sort_mode = False  # режим сортировки
        self.group_mode = False  # режим
        self.sort_dialog = None  # диалог сортировки
        self.export_dialog = None  # диалог экспорта данных
        self.common_model = None  # модель таблицы для отображения общих данных

        # Настройка ui
        self.setup_log()
        caption = self.setup_caption_widget()  # возвращает QHBoxLayout, настроенный компоновщик
        container_up = self.setup_up_central_widget()  # настройка ui, общая таблица возвращает виджет

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self)
        splitter.addWidget(container_up)
        splitter.addWidget(QtWidgets.QPushButton("Temp"))
        central_layout = QtWidgets.QVBoxLayout(self)  # главный Layout, наследуемый класс
        central_layout.addLayout(caption)
        central_layout.addWidget(splitter, 1)
        wid = QtWidgets.QWidget()
        wid.setLayout(central_layout)
        self.setCentralWidget(wid)
        # self.setStyleSheet("QWidget { border: 1px solid yellow; }")  # проверка отображения виджетов

        # настраиваем все виджеты
        setup_dock_widgets(self, ["bottom_dock"], config.UI_BASE_ATTRS)

        # Signals
        self.table_widget.signal_message.connect(self.forward_signal)  # перенаправление сигнала в строку состояния
        self.table_widget.signal_data_changed.connect(self.log_change_data)  # запись информации в лог для пользователя

        # смотрим, есть ли в реестре файл проекта, который запускали прошлый раз?
        if os.path.exists(self.settings.read_attributes_input()):
            # пробуем загрузить
            self.load_project(self.settings.read_attributes_input(),
                              self.tr(f"Loaded last used project file: {self.settings.read_attributes_input()}"))
        else:  # файла нет, тогда ограничиваем функционал
            self.toggle_tool_buttons(False)

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

        self.btn_save = new_button(self, "tb", icon="glyph_save2", tooltip=self.tr("Save changes to the project"),
                                   slot=self.save, color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)
        self.btn_project_tools = new_button(self, "tb", icon="glyph_file-cabinet", color=the_color,
                                            tooltip=self.tr("Project tools"),
                                            icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)

        self.btn_copy = new_act(self, self.tr("Make copy of current project"), "glyph_duplicate", the_color,
                                self.attrs_copy_project, tip=self.tr("Make copy of current project"))
        self.btn_export = new_act(self, self.tr("Export current project info"), "glyph_check_all", the_color,
                                  self.attrs_export, tip=self.tr("Export current project info"))
        self.btn_save_palette = new_act(self, self.tr("Save original project palette"), "glyph_palette", the_color,
                                        self.attrs_save_palette, tip=self.tr("Save original project palette"))

        self.btn_apply_palette = new_act(self, self.tr("Apply palette for current project"), color=the_color,
                                         icon="glyph_paint_brush", slot=self.attrs_apply_palette,
                                         tip=self.tr("Apply palette for current project and reload it"))
        self.btn_apply_lrm = new_act(self, self.tr("Set GSD data via folder"), icon="glyph_sat_image", color=the_color,
                                     slot=self.attrs_apply_lrm_from_folder,
                                     tip=self.tr("Set GSD data from map files in folder to current project"))
        self.btn_remove_empty = new_act(self, self.tr("Remove image entries with missing markup"), icon="glyph_clear",
                                        color=the_color, slot=self.remove_empty,
                                        tip=self.tr("Remove image entries with missing markup"))
        self.btn_remove_imgs_records = new_act(self, self.tr("Remove image with pattern"), icon="glyph_delete",
                                               color=the_color, slot=self.remove_imgs_records,
                                               tip=self.tr("Remove image with pattern"))
        self.btn_assign_user = new_act(self, self.tr("Assign user for data"), icon="glyph_user_check",
                                       color=the_color, slot=self.assign_user,
                                       tip=self.tr("Assign user for data"))
        self.btn_calc_std_mean = new_act(self, self.tr("Calculate mean and std for dataset"), icon="glyph_donut-chart",
                                         color=the_color, slot=self.calc_std_mean,
                                         tip=self.tr("Calculate mean and std for dataset"))

        # перечень инструментов проекта
        self.tools_for_project = [self.btn_copy, self.btn_remove_empty, self.btn_remove_imgs_records,
                                  self.btn_assign_user, self.btn_apply_lrm, self.btn_save_palette,
                                  self.btn_apply_palette, self.btn_calc_std_mean, self.btn_export]
        menu_project = QtWidgets.QMenu(self)
        menu_project.addActions(self.tools_for_project)
        self.btn_project_tools.setMenu(menu_project)  # устанавливаем меню
        self.btn_project_tools.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)

        self.btn_change_balance_calc = new_button(self, "tb", icon="glyph_data_graph", slot=self.change_balance_calc,
                                                  tooltip=self.tr("Select dataset balance method"),
                                                  color=the_color, icon_size=config.UI_AZ_PROC_ATTR_ICON_SIZE)

        self.common_buttons = [self.btn_save, self.btn_project_tools, self.btn_change_balance_calc]

        hlay_buttons = QtWidgets.QHBoxLayout()
        for button in self.common_buttons:
            hlay_buttons.addWidget(button)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        hlay_buttons.addWidget(spacer)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.btn_log_and_status)
        hlay.addWidget(self.label_project)  # метка для пути проекта
        hlay.addWidget(self.file_json, 3)  # текущий проект
        hlay.addWidget(spacer, 1)
        hlay.addLayout(hlay_buttons)
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

        self.images_dir_helper = new_button(self, "tb", icon="circle_grey")
        self.images_dir_label = new_text(self, self.tr("Images dir:"))
        self.images_dir = AzButtonLineEdit("glyph_folder", the_color, caption=self.tr("Change images dir"),
                                           read_only=True, dir_only=True, slot=self.change_current_image_dir)
        hlay_change_dir = QtWidgets.QHBoxLayout()
        hlay_change_dir.addWidget(self.images_dir_helper)
        hlay_change_dir.addWidget(self.images_dir_label)
        hlay_change_dir.addWidget(self.images_dir)

        hlay_descr = QtWidgets.QHBoxLayout()
        hlay_descr.addWidget(self.project_label, 1)
        hlay_descr.addWidget(self.tb_edit_project_descr)
        # hlay_descr.setSpacing(0)
        vlay_table_descr = QtWidgets.QVBoxLayout()
        vlay_table_descr.addWidget(self.common_table)
        vlay_table_descr.addSpacing(5)
        vlay_table_descr.addLayout(hlay_change_dir)
        vlay_table_descr.addSpacing(5)
        vlay_table_descr.addLayout(hlay_descr)
        vlay_table_descr.addWidget(self.project_description)
        vlay_table_descr.setContentsMargins(0, 0, 0, 0)
        vlay_table_descr.setSpacing(0)

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
        self.table_widget.horizontalHeader().setFixedHeight(36)  # установим широкий заголовок

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
            # header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)  # ResizeToContents
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

        # итоговая настройка ui центрального виджета
        layout_up = QtWidgets.QHBoxLayout()
        layout_up.addWidget(self.table_widget, 15)  # делаем доминантным
        layout_up.addLayout(vlay_table_descr, 9)  # добавляем ему расположение с кнопками и QLabel
        container_up = QtWidgets.QWidget()
        container_up.setLayout(layout_up)
        return container_up

    def setup_down_central_widget(self):
        layout_down = QtWidgets.QHBoxLayout()
        container_down = QtWidgets.QWidget()
        container_down.setLayout(layout_down)
        return container_down

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

    def change_current_image_dir(self):
        """Смена текущего каталога изображений"""
        if self.images_dir.text() == self.sama_data.get_image_path():
            return
        self.check_path_images("new", self.images_dir.text())
        self.log_change_data(self.tr(f"Set new directory for images '{self.images_dir.text()}'"))
        self.signal_message.emit(self.tr(f"Set new directory for images '{self.images_dir.text()}'"))

    def check_path_images(self, status="default", path=None):
        """Проверка 'директории изображений' """
        if status == "empty":
            self.images_dir_helper.setIcon(new_icon("circle_grey"))
            self.images_dir.clear()
            return
        elif status == "default":
            self.images_dir.setText(self.sama_data.get_image_path())
            path = self.images_dir.text()
        elif status == "new":
            self.sama_data.set_path_to_images(path)

        good = True  # по умолчанию всё хорошо
        if not helper.check_file(path):
            self.images_dir_helper.setIcon(new_icon("circle_red"))
            return

        images = self.sama_data.get_images_list()
        for image in images:
            if not helper.check_file(os.path.join(path, image)):
                good = False

        if good:
            self.images_dir_helper.setIcon(new_icon("circle_green"))
        else:
            self.images_dir_helper.setIcon(new_icon("circle_red"))

    def assign_user(self):
        all_images = ", ".join(list(self.sama_data.data["images"].keys()))  # перечень изображений
        dialog = AzInputDialog(self, 2, [self.tr("Set username for dataset:"), self.tr(
            "Leave it as is or correct the assigned image\nlist (for example, 'img006, img028'):")],
                               self.tr("Assign user for for data"), input_type=[0, 0],
                               combo_inputs=["Unknown", all_images], cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем результат: ["User_name", "img06, img28"]
        items = [item.strip() for item in result[1].split(',')]
        count = 0
        for item in items:
            if self.sama_data.get_image_data(item):  # изображение существует
                if self.sama_data.set_image_last_user(item, result[0]):  # проверяем можно ли установить
                    count += 1
        self.log_change_data(self.tr(f"Set user '{result[0]}' for {count} images"))
        self.signal_message.emit(self.tr(f"Set user '{result[0]}' for {count} images"))

    def calc_std_mean(self):
        """Запуск расчета среднего и СКО поканальной яркости датасета. Передается файл SAMA"""      
        path_dir = self.sama_data.get_image_path()

        if not helper.check_file(path_dir):
            self.log_change_data(self.tr(f"Check the dataset images files directory"))
            self.signal_message.emit(self.tr(f"Check the dataset images files directory"))
        # dialog = AzCalcStdMean(self.current_file)  # по умолчанию выбирается проект
        dialog = AzCalcStdMean(self.current_file, input_type=0, user_dir_or_file="D:/data_sets/output_dir/01.jpg" )
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return

        print("mean: ", dialog.mean_dataset, " std: ", dialog.std_dataset)
        self.sama_data.set_dataset_mean_std_for_channels(list(dialog.mean_dataset), list(dialog.std_dataset))
        self.log_change_data(self.tr(f"The mean and standard deviation of the image channels of the dataset are "
                                     f"calculated and written to the project file"))
        self.signal_message.emit(self.tr(f"The mean and standard deviation of the image channels of the dataset are "
                                         f"calculated and written to the project file"))

    def change_balance_calc(self):
        self.find_by_label()
        return
        # do i need to complete dataset evaluate for balance?
        methods = ["Shannon entropy"]
        dialog = AzInputDialog(self, 1, [self.tr("Using method:")],
                               self.tr("Select dataset balance method"), input_type=[1],
                               combo_inputs=[methods], cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()

    def save(self):
        self.save_and_reload(self.current_file, self.tr(f"Project was saved and reload: {self.current_file}"))

    def save_and_reload(self, file, message):
        self.sama_data.save(file)  # сохранение данных и перезагрузка данных
        self.load_project(file, message)

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
        self.images_dir.button.setEnabled(flag)

    def attr_actions_disable(self, message):  # сброс всех форм при загрузке, а также отключение инструментов
        self.current_file = None
        self.toggle_tool_buttons(False)
        self.clear_dataset_info()
        self.table_widget.clear_table()
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
        """ Экспорт общей информации о проекте в текстовый файл """
        file = az_file_dialog(self, self.tr("Export table and dataset data to text file"),
                              self.settings.read_last_dir(), dir_only=False, remember_dir=False, file_to_save=True,
                              filter="txt (*.txt)", initial_filter="txt (*.txt)")
        if not file:
            return
        if len(file) < 2:
            return

        # сохраняем в файл, при этом пропускаем определенные столбцы
        export_data = ["-------------- Common info --------------\n"]  # общая информация
        common_headers = [
            self.common_model.headerData(i, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)
            for i in range(self.common_model.columnCount())]
        common_headers = [item.replace('\n', ' ') for item in common_headers]  # общие заголовки
        common_data = self.common_data[0]
        export_data += [f"{key}{value}\n" for key, value in zip(common_headers, common_data)]
        export_data.append(self.project_label.text() + "\n" + self.project_description.toPlainText() + "\n")
        export_data += ["-------------- Labels info --------------\n"]

        # Экспорт табличных данных
        exclude_columns = list(self.table_widget.special_cols.keys())  # сначала определяем столбцы исключений
        label_headers = []
        for col in range(self.table_widget.columnCount()):
            if col not in exclude_columns:  # пропускаем столбцы из списка исключений
                item = self.table_widget.horizontalHeaderItem(col)
                if item is not None:
                    label_headers.append(item.text() + "\t")
                else:
                    label_headers.append("\t")
        export_data.append("".join(label_headers) + "\n")

        for row in range(self.table_widget.rowCount()):
            label_data = []
            for col in range(self.table_widget.columnCount()):
                if col not in exclude_columns:  # пропускаем столбцы из списка исключений
                    item = self.table_widget.item(row, col)
                    if item is not None:
                        label_data.append(item.text() + "\t")
                    else:
                        label_data.append("\t")
            export_data.append("".join(label_data) + "\n")
        print(export_data)

        helper.save_txt(file, export_data)
        self.signal_message.emit(self.tr(f"Table data export to: {file}"))
        # self.signal_message.emit(self.tr(f"An error occurred while exporting data: {file}"))

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
        if count > 0:
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
        self.sama_data.load(filename)
        self.log_clear()
        self.toggle_descr()  # настраиваем ui описания проекта
        if not self.sama_data.is_correct_file:
            self.attr_actions_disable(
                self.tr("Selected file isn't correct, or haven't data"))
            # Выбранный файл не является корректным либо не содержит необходимых данных
            self.file_json.clear()
            self.check_path_images("empty")
            self.change_log_icon("grey")
            return

        # Все загружено и всё корректно, поэтому записываем его в реестр и начинаем процедуру загрузки
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        self.file_json.setText(filename)
        if self.sama_data.get_project_description() is not None:  # загрузка описания проекта
            self.project_description.setText(self.sama_data.get_project_description())
        self.check_path_images("default")
        self.current_file = filename
        self.settings.write_attributes_input(filename)
        self.toggle_tool_buttons(True)
        self.load_dataset_info()  # загружаем общее инфо о датасете
        self.table_widget.load_table_data(self.sama_data)  # обновляем данные для таблицы
        self.original_image_data = None  # очищаем данные с исходными значениями
        self.log_change_data(message)
        self.change_log_icon("green")
        self.signal_message.emit(message)
        QtWidgets.QApplication.restoreOverrideCursor()

    def toggle_descr(self):
        self.project_description.clear()  # очищаем текст
        if self.tb_edit_project_descr.isChecked():  # остался включённым режим редактирования
            self.tb_edit_project_descr.animateClick(0)

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
        dialog = AzInputDialog(self, 1, [self.tr("Enter pattern (125s_FRA, 147s_DEU, for example)")],
                               input_type=[0],
                               window_title=self.tr("Delete records images with pattern"),
                               cancel_text=self.tr("Cancel"))
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Rejected:  # нажата "Отмена"
            return
        result = dialog.get_inputs()  # получаем введенные данные
        pattern_list = [item.strip() for item in result[0].split(',')]  # разделяем по запятым, удаляем пробелы
        deleted = self.sama_data.remove_images_with_pattern(pattern_list)  # удаляем записи из проекта
        if deleted > 0:
            message = self.tr(f"Removed: {deleted} images records")
            self.log_change_data(message)
            self.signal_message.emit(message)
        else:
            self.signal_message.emit(self.tr("There are no images with pattern to delete"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabAttributesUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes
        if self.common_model:
            self.common_model.setHorizontalHeaderLabels([self.tr("Count of\nimages: "), self.tr("Count of\nlabels: "),
                                                         self.tr("Average\nGSD: "), self.tr("Deviation\nGSD: ")])
        self.table_widget.translate_ui()
        self.table_widget.setHorizontalHeaderLabels(
            [self.tr("Label name"), self.tr("Labels count"), self.tr("Frequency per 100 images"),
             self.tr("% total labels"), self.tr("Average area, pixels"), self.tr('SD of area, pixels'),
             self.tr("Balance"), self.tr("Color"), self.tr("Action")])

        self.label_project.setText(self.tr("Path to file project (*.json):"))
        self.btn_project_tools.setToolTip(self.tr("Project tools"))
        self.images_dir.setToolTip("Change images dir for current project file")
        self.images_dir_label.setText(self.tr("Images dir:"))

        self.btn_copy.setText(self.tr("Make copy of current project"))
        self.btn_export.setText(self.tr("Export current project info"))
        self.btn_save_palette.setText(self.tr("Save palette from current project"))
        self.btn_apply_palette.setText(self.tr("Apply palette for current project"))
        self.btn_save.setText(self.tr("Save changes to the project"))
        self.btn_apply_lrm.setText(self.tr("Set GSD data via folder with *.map"))
        self.btn_remove_empty.setText(self.tr("Remove image entries with missing markup"))
        self.btn_remove_imgs_records.setText(self.tr("Remove image with pattern"))
        self.btn_change_balance_calc.setText(self.tr("Select dataset balance method"))
        self.btn_assign_user.setText(self.tr("Assign user for data"))
        self.btn_calc_std_mean.setText(self.tr("Calculate mean and std for dataset"))

        self.btn_copy.setToolTip(self.tr("Make copy of current project"))
        self.btn_export.setToolTip(self.tr("Export current project info"))
        self.btn_save_palette.setToolTip(self.tr("Save palette from current project"))
        self.btn_apply_palette.setToolTip(self.tr("Apply palette for current project"))
        self.btn_save.setToolTip(self.tr("Save changes to the project"))
        self.btn_apply_lrm.setToolTip(self.tr("Set GSD data from map files in folder to current project"))
        self.btn_remove_empty.setToolTip(self.tr("Remove image entries with missing markup"))
        self.btn_remove_imgs_records.setToolTip(self.tr("Remove image with pattern"))
        self.btn_change_balance_calc.setToolTip(self.tr("Select dataset balance method"))
        self.btn_assign_user.setToolTip(self.tr("Assign user for data"))
        self.btn_calc_std_mean.setToolTip(self.tr("Calculate mean and std for dataset"))

        self.tb_edit_project_descr.setToolTip(self.tr("Toggle edit project description"))
        self.project_label.setText(self.tr("Project description:"))

    # todo: перенести в другое место
    def find_by_label(self):
        val = "04-cat_crack"
        mylist = self.sama_data.get_images_by_label(val)
        print("list: ", mylist)

    # todo: перенести в другое место
    def del_all_but_ex(self):
        exclusions = ""
        excl = [item.strip() for item in exclusions.split(',')]
        deleted = self.sama_data.remove_images(excl, True)  # удаляем записи из проекта
        if deleted:
            print(deleted)


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TabAttributesUI()
    window.show()
    sys.exit(app.exec_())
