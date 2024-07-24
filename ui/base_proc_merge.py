from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, convert_labelme_to_sama, merge_sama_to_sama, UI_COLORS, UI_READ_LINES, config, \
    natural_order
from ui import new_act, new_text, new_cbx, az_file_dialog, AzButtonLineEdit, coloring_icon
from datetime import datetime
import os

the_color = UI_COLORS.get("processing_color")


class TabMergeUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Страница QTabWidget раздела Обработки для Объединения/конвертации данных
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabMergeUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Merge"
        self.tool_tip_title = "Converting and merging datasets projects"
        if color_active:
            self.icon_active = coloring_icon("glyph_merge", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_merge", color_inactive)

        self.setup_ui()  # настраиваем интерфейс

    def setup_ui(self):
        # Действия для страницы
        self.merge_actions = (
            new_act(self, "Add files", "glyph_add", the_color, self.merge_add_files),
            new_act(self, "Remove files", "glyph_delete3", the_color, self.merge_remove_files),
            new_act(self, "Select all", "glyph_check_all", the_color, self.merge_select_all),
            new_act(self, "Clear list", "glyph_delete2", the_color, self.merge_clear),
            new_act(self, "Merge selected files", "glyph_merge", the_color, self.merge_combine),
            new_act(self, "Open output dir", "glyph_folder_clear", the_color, self.merge_open_output))
        self.merge_output_label = new_text(self, self.tr("Output type:"))
        self.merge_output_list = new_cbx(self, config.UI_OUTPUT_TYPES)  # список выходных данных
        self.merge_files_list = QtWidgets.QListWidget()  # перечень добавляемых файлов
        self.merge_files_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.merge_preview_data = QtWidgets.QScrollArea()  # контейнер для предпросмоторщика файлов
        self.merge_preview_data.setWidgetResizable(True)
        self.merge_label = QtWidgets.QLabel()  # предпросмоторщик файлов
        self.merge_preview_data.setWidget(self.merge_label)
        self.merge_input_label = new_text(self, self.tr("Input type:"))
        self.merge_input_list = new_cbx(self, config.UI_INPUT_TYPES)  # список входных данных
        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)  # создаём разделитель
        split.addWidget(self.merge_files_list)  # куда помещаем перечень файлов...
        split.addWidget(self.merge_preview_data)  # ...и пробоотборщик этих файлов
        split.setChildrenCollapsible(False)  # отключаем полное сворачивание виджетов внутри разделителя
        split.setSizes((90, 30))
        self.merge_files_list.itemSelectionChanged.connect(
            self.merge_selection_files_change)  # изменение выделенного объекта
        self.merge_toolbar = QtWidgets.QToolBar(self.tr("Toolbar for merging project files"))
        self.merge_toolbar.setIconSize(
            QtCore.QSize(config.UI_AZ_PROC_MERGE_ICON_PANEL, config.UI_AZ_PROC_MERGE_ICON_PANEL))
        self.merge_toolbar.setFloatable(False)
        self.merge_toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали

        self.toolbar_items = (self.merge_actions[0], self.merge_actions[1], None, self.merge_actions[2],
                              self.merge_actions[3], None, self.merge_input_label, self.merge_input_list, None,
                              self.merge_output_label, self.merge_output_list, None, self.merge_actions[4], None,
                              self.merge_actions[5])
        for item in self.toolbar_items:  # добавляем объекты на панель
            if item:
                if isinstance(item, QtWidgets.QAction):
                    self.merge_toolbar.addAction(item)
                elif isinstance(item, QtWidgets.QWidget):
                    self.merge_toolbar.addWidget(item)
            else:
                self.merge_toolbar.addSeparator()

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
        self.addToolBar(self.merge_toolbar)  # добавляем панель меню
        self.setCentralWidget(wid)  # устанавливаем главный виджет страницы "Слияние"
        self.merge_toggle_instruments()  # устанавливаем доступные инструменты

    @QtCore.pyqtSlot(str)
    def default_dir_changed(self, path):
        if not self.merge_output_file_check.isChecked():
            self.merge_output_file_path.setText(path)

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
        QtWidgets.QApplication.restoreOverrideCursor()
        self.merge_toggle_instruments()

    def merge_toggle_instruments(self):
        """Включает/отключает инструменты"""
        # сначала всё отключим по умолчанию
        for i in range(1, 5):
            self.merge_actions[i].setEnabled(False)
        if self.merge_files_list.count() > 0:
            self.merge_actions[2].setEnabled(True)  # включаем кнопку "очистить список"
            self.merge_actions[3].setEnabled(True)  # включаем кнопку "выделить всё"
        if len(self.merge_files_list.selectedItems()) > 0:  # имеются выбранные файлы
            self.merge_actions[1].setEnabled(True)  # включаем кнопку "удалить выбранные"
            if len(self.merge_files_list.selectedItems()) > 1:  # выбрано более двух файлов
                self.merge_actions[4].setEnabled(True)

    def merge_add_files(self):
        sel_files = az_file_dialog(self, "Select project files to add", self.settings.read_last_dir(), dir_only=False,
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
            self.signal_message.emit(self.tr("Начинаю процедуру объединения/конвертирования"))
            sel_items = self.merge_files_list.selectedItems()
            data = [item.text() for item in sel_items if os.path.isfile(item.text())]
            unique = sorted(set(data), key=natural_order)
            if len(unique) <= 1:
                self.signal_message.emit(self.tr("Выбраны дубликаты"))
                return

            input_type = self.merge_input_list.currentText()  # тип исходных данных
            if input_type == "LabelMe.json":
                new_name = os.path.join(self.merge_output_dir,
                                        "converted_%s.json" % datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                if convert_labelme_to_sama(unique, new_name):  # метод возвращающий True|False в зависимости от успеха
                    self.merge_files_list.clearSelection()
                    self.signal_message.emit(self.tr(f"Файлы успешно объединены и конвертированы в файл: '{new_name}'"))
                else:
                    self.signal_message.emit(self.tr("Ошибка при конвертации данных. Проверьте исходные файлы."))

            elif input_type == "SAMA.json":
                new_name = os.path.join(self.merge_output_dir,
                                        "merged_%s.json" % datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                merge = merge_sama_to_sama(unique, new_name, False)
                if merge == 0:
                    self.signal_message.emit(self.tr(f"Файлы успешно объединены в файл: '{new_name}'"))
                elif merge > 0:
                    self.signal_message.emit(f"Файлы объединены с ошибками ({merge} ошибок): '{new_name}'")
                else:
                    self.signal_message.emit(self.tr(
                        f"Ошибка при объединении данных. Проверьте исходные файлы либо параметры конвертации.'"))

        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def merge_select_all(self):
        self.merge_files_list.selectAll()

    def merge_open_output(self):
        os.startfile(self.merge_output_dir)  # открываем каталог средствами системы

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabMergeUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Merge
        self.merge_actions[0].setText(self.tr("Add files"))
        self.merge_actions[1].setText(self.tr("Remove files"))
        self.merge_actions[2].setText(self.tr("Select all"))
        self.merge_actions[3].setText(self.tr("Clear list"))
        self.merge_actions[4].setText(self.tr("Merge selected files"))
        self.merge_actions[5].setText(self.tr("Open output folder"))
        self.merge_output_label.setText(self.tr("Output type:"))
        self.merge_output_file_check.setText(self.tr("Set user output file path other than default:"))
        self.merge_toolbar.setWindowTitle(self.tr("Toolbar for merging project files"))
        self.merge_input_label.setText(self.tr("Input type:"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = TabMergeUI()
    w.show()
    app.exec()
