from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, dn_crop, UI_COLORS, config, helper
from ui import new_button, AzButtonLineEdit, AzSpinBox, AzTableModel, AzManualSlice, coloring_icon
from datetime import datetime
import time
import os

the_color = UI_COLORS.get("processing_color")


class TabSliceUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Страница QTabWidget раздела Автоматической нарезки данных
    color_active, icon_inactive цвета иконок активные и неактивные соответственно
    Example: tab_page = TabSliceUI(QtCore.Qt.GlobalColor.red, QtCore.Qt.GlobalColor.white, self)
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabSliceUI, self).__init__(parent)
        self.crop_options = None
        self.settings = AppSettings()  # настройки программы
        self.name = "Slice"
        if color_active:
            self.icon_active = coloring_icon("glyph_slice", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_slice", color_inactive)
        self.json_obj = None
        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)  # вертикальный разделитель
        slice_auto_form = QtWidgets.QFormLayout()  # форма для расположения виджетов "автоматического разрезания"

        # Общая строка в форме
        self.slice_input_file_label = QtWidgets.QLabel("Path to file project *.json:")  # метка исходного файла
        self.slice_input_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                      caption="Select project file to auto slicing",
                                                      read_only=True, dir_only=False, filter="Projects files (*.json)",
                                                      slot=self.slice_load_projects_data,
                                                      initial_filter="json (*.json)")
        self.slice_input_file_path.setText(self.settings.read_slicing_input())  # строка для исходного файла
        self.slice_input_file_path.textChanged.connect(
            lambda: self.settings.write_slicing_input(self.slice_input_file_path.text()))  # автосохранение

        # 1 строка в форме Автоматизированного разрезания
        self.slice_output_file_check = QtWidgets.QCheckBox("Set user output file path other than default:")
        self.slice_output_file_path = AzButtonLineEdit("glyph_folder", the_color,
                                                       caption="Output file",
                                                       read_only=True, dir_only=True)

        # 2 строка в форме Автоматизированного разрезания
        self.slice_scan_size_label = QtWidgets.QLabel("Scan size:")  # метка для сканирующего окна
        # размер сканирующего окна
        self.slice_scan_size = AzSpinBox(min_val=config.MIN_CROP_SIZE, min_wide=53, max_val=config.MAX_CROP_SIZE)
        self.slice_overlap_window_label = QtWidgets.QLabel("Scanning window overlap percentage:")
        self.slice_scan_size.setValue(self.settings.read_slice_crop_size())

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

        # 3 строка в форме Автоматизированного разрезания
        self.slice_output_file_path.setEnabled(False)
        self.slice_output_file_check.clicked.connect(self.slice_toggle_output_file)  # соединяем - требуется настройка
        self.slice_output_file_path.setText(self.settings.read_default_output_dir())  # строка для выходного файла
        # кнопка получения результатов - автоматическое кадрирование
        self.slice_exec = new_button(self, "pb", " Automatically crop images", "glyph_slice", the_color,
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

        # нижний виджет - ручная обработка
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
        self.setCentralWidget(wid)
        self.autocrop_worker = AutoCropWorker()  # экземпляр потока авторазрезания

        # проверяем есть ли сохранённый ранее файл проекта, и загружаем его автоматически
        if len(self.slice_input_file_path.text()) > 0:
            self.slice_load_projects_data()

        self.slice_scan_size.valueChanged.connect(self.manual_wid.set_crop_data)  # синхронизируем изменение...
        self.manual_wid.signal_crop.connect(self.slice_scan_size.setValue)  # ...значения кадрирования

        # инициализируем параметры кадрирования и соединяем со всеми возможными способами изменить их
        self.slice_init_options_for_crop()
        self.slice_output_file_path.textChanged.connect(self.slice_options_for_crop_update)  # output_name
        self.slice_scan_size.valueChanged.connect(self.slice_options_for_crop_update)  # crop_size
        if self.slice_tab_labels.model():
            self.slice_tab_labels.model().dataChanged.connect(self.slice_options_for_crop_update)  # polygons overlap
        self.slice_overlap_window.valueChanged.connect(self.slice_options_for_crop_update)  # window overlap
        self.slice_edge.valueChanged.connect(self.slice_options_for_crop_update)  # edge
        self.slice_smart_crop.toggled.connect(self.slice_options_for_crop_update)  # smart

        # Соединения для потока
        self.autocrop_worker.finished.connect(self.autocrop_on_finished)  # завершение работы autocrop worker
        self.autocrop_worker.signal_progress.connect(self.show_progress)  # прогресс работы autocrop worker

    @QtCore.pyqtSlot()
    def autocrop_on_finished(self):
        self.slice_exec.setEnabled(True)
        if self.autocrop_worker.result:
            if self.autocrop_worker.result > 0:
                self.signal_message.emit(
                    "Авто-кадрирование завершено. Общее количество изображений: %s" % self.autocrop_worker.result)
            elif self.autocrop_worker.result < 0:
                self.signal_message.emit("В проекте разметке присутствуют ошибки. Авто-кадрирование невозможно.")
            else:  # self.autocrop_worker.result == 0:
                self.signal_message.emit("Авто-кадрирование изображений не выполнено. Изображения отсутствуют")

        else:
            self.signal_message.emit("Авто-кадрирование не выполнено")

    @QtCore.pyqtSlot(str)
    def show_progress(self, progress):
        self.signal_message.emit(progress)

    @QtCore.pyqtSlot(str)
    def default_dir_changed(self, path):
        if not self.slice_output_file_check.isChecked():
            self.slice_output_file_path.setText(path)

    def slice_options_for_crop_update(self):  # регулярное обновление словаря с параметрами разрезания
        self.crop_options["crop_size"] = self.slice_scan_size.value()
        if self.slice_tab_labels.isHidden():
            self.crop_options["percent_overlap_polygons"] = None
        else:
            pols_overlap_percent = []
            model = self.slice_tab_labels.model()
            if model:
                for row in range(model.rowCount(-198)):  # -198 чтобы тебя запутать))
                    # процент указан во втором столбце, роль "Редактирования" включает "Отображение"
                    pols_overlap_percent.append(
                        (model.data(model.index(row, 1), QtCore.Qt.ItemDataRole.DisplayRole)) / 100)
            self.crop_options["percent_overlap_polygons"] = pols_overlap_percent
        self.crop_options["percent_overlap_scan"] = self.slice_overlap_window.value() / 100
        self.crop_options["edge"] = self.slice_edge.value()
        self.crop_options["smart_cut"] = not self.slice_smart_crop.isChecked()
        self.crop_options["output_name"] = self.slice_output_file_path.text()  # только название каталога
        self.manual_wid.crop_options = self.crop_options  # обновляем данные для виджета Ручного кадрирования

    def slice_init_options_for_crop(self):  # заполняем словарь параметрами для кадрирования
        self.crop_options = {"hand_cut": False}
        self.slice_options_for_crop_update()

    @QtCore.pyqtSlot()
    def slice_exec_run(self):  # процедура авторазрезания
        if self.autocrop_worker.isRunning():
            self.signal_message.emit("Авто-кадрирование уже запущено...")
        else:
            self.slice_exec.setEnabled(False)
            self.signal_message.emit("Запуск авто-кадрирования...")
            self.crop_options["json_path"] = os.path.dirname(self.slice_input_file_path.text())
            self.crop_options["json_name"] = os.path.basename(self.slice_input_file_path.text())
            self.autocrop_worker.get_params(**self.crop_options)  # передаём параметры авто-кадрирования в поток
            self.autocrop_worker.start()  # Запускаем поток

    def slice_load_projects_data(self):  # загрузка файла проекта
        if self.json_obj is not None:
            if self.slice_input_file_path.text() == self.json_obj.FullNameJsonFile:
                return  # Файл не трогали, изменений нет
        self.json_obj = dn_crop.DNjson(self.slice_input_file_path.text())  # Файл проекта, реализация Дениса
        if not self.json_obj.input_file_exists:  # такого файла уже нет
            self.slice_disable("Отсутствует выбранный ранее файл")
            return
        if not self.json_obj.good_file:
            self.slice_disable("Выбранный файл не является корректным либо не содержит необходимых данных")
            return
        self.slice_exec.setEnabled(True)
        model_data = []  # данные для отображения
        self.slice_tab_labels.show()
        for label in self.json_obj.labels:
            # [наименование метки, процент перекрытия]
            model_data.append([label, int(self.slice_overlap_pols_default.text())])
        self.slice_tab_labels.setModel(
            AzTableModel(model_data, header_data=["Наименование класса (метки)", "Процент перекрытия"], edit_column=1))
        if self.slice_tab_labels.model():
            self.slice_tab_labels.model().dataChanged.connect(self.slice_options_for_crop_update)
        header = self.slice_tab_labels.horizontalHeader()  # настраиваем отображение столбцов
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.manual_wid.update_input_data(self.json_obj)  # Передаём данные, в т.ч. для настройки панели Ручной резки

    def slice_disable(self, message):
        self.signal_message.emit(message)
        self.slice_tab_labels.hide()
        self.slice_exec.setEnabled(False)  # отключаем возможность Разрезать
        self.manual_wid.update_input_data(None)  # передаём "Отсутствие" данных для настройки панели Ручной резки

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

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabSliceUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Slice
        self.slice_input_file_label.setText(self.tr("Path to file project *.json:"))
        self.slice_output_file_check.setText(self.tr("Set user output file path other than default:"))
        self.slice_scan_size_label.setText(self.tr("Scan size:"))
        self.slice_overlap_window_label.setText(self.tr("Scanning window overlap percentage:"))
        self.slice_overlap_pols_default_label.setText(self.tr("Default overlap percentage for classes:"))
        self.slice_edge_label.setText(self.tr("Offset from the edge"))
        self.slice_smart_crop.setText(self.tr("Simplified grid framing (no smart grouping)"))
        self.slice_exec.setText(self.tr(" Automatically crop images"))
        self.slice_open_result.setText(self.tr(" Open results"))
        self.slice_up_group.setTitle(self.tr("Automatic image cropping"))
        self.slice_down_group.setTitle(self.tr("Manual visual image cropping"))
        self.manual_wid.translate_ui()


# ----------------------------------------------------------------------------------------------------------------------

class AutoCropWorker(QtCore.QThread):
    """Поток для выполнения автоматического разрезания"""
    signal_progress = QtCore.pyqtSignal(str)

    def __init__(self):
        super(AutoCropWorker, self).__init__()
        self.params = None
        self.result = None
        self.dn_crop = None

    def get_params(self, **params):
        # инициализация начальных параметров через словарь
        self.params = params

    @QtCore.pyqtSlot(str)
    def forward_signal(self, message):
        self.signal_progress.emit(message)  # перенаправление сигналов

    def run(self):
        start_time = time.time()  # отмечаем начало работы
        date_time = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        new_name = os.path.join(str(self.params["output_name"]), "cropped_%s.json" % date_time)
        self.dn_crop = dn_crop.DNImgCut(self.params["json_path"], self.params["json_name"])  # объект класса для АК
        self.dn_crop.signal_progress.connect(self.forward_signal)
        # выполняем кадрирование (нарезку)
        self.result = self.dn_crop.CutAllImgs(self.params["crop_size"],
                                              self.params["percent_overlap_polygons"],
                                              self.params["percent_overlap_scan"],
                                              new_name,
                                              self.params["edge"],
                                              self.params["smart_cut"],
                                              self.params["hand_cut"])

        end_time = time.time()  # завершение работы
        print(f"Время работы алгоритма автоматического кадрирования: {helper.format_time(end_time - start_time, 'ru')}")


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


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = TabSliceUI()
    w.show()
    app.exec()
