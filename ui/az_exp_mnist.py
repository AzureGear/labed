from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from ui import new_text, new_cbx, new_button, new_icon, AzTableModel, az_file_dialog
from utils import AppSettings, helper, config
from datetime import datetime
from utils.az_math import *
import numpy as np
import random
import os

the_color = config.UI_COLORS.get("experiments_color")
ROW_H = 16


# ----------------------------------------------------------------------------------------------------------------------
class PageMNIST(QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал передачи сообщения родительскому виджету
    inner_signal = QtCore.pyqtSignal(str)  # внутренний сигнал
    signal_info = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения в self.info

    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)
        self.name = "MNIST"
        self.settings = AppSettings()
        self.current_img = None  # текущее изображение (без коррекции и пиксельной сетки)
        self.setup_ui()  # настройка интерфейса
        self.restore_last_saved_settings()  # восстановление сохранённых настроек
        # self.setStyleSheet("QWidget { border: 1px solid red; }")  # проверка отображения виджетов
        self.clear_digits()

        # поток для расчета нейронной сети QThread
        self.mnist_worker = MNISTWorker()  # экземпляр потока

        # Соединения
        self.mnist_worker.started.connect(self.mnist_on_started)  # начало работы mnist worker
        self.mnist_worker.finished.connect(self.mnist_on_finished)  # завершение работы mnist worker
        # сигнал mnist_worker'a о текущих действиях
        self.mnist_worker.inner_signal.connect(self.mnist_on_change, QtCore.Qt.QueuedConnection)
        self.mnist_worker.signal_model.connect(self.mnist_handler.set_model)
        self.mnist_handler.signal_mnist_handler.connect(self.toggle_use_model)
        # сигналы интерфейса
        self.draw28x28.signal_draw.connect(self.preview_show_draw)
        self.signal_info.connect(self.add_message_info)  # передача сообщения в лог

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)  # пусть будет итоговым компоновщиком

        self.info = QtWidgets.QTextEdit(self)  # лог отображения информации
        self.info.setReadOnly(True)
        self.info.setFont(QtGui.QFont("Consolas", 10))

        self.draw28x28 = AzCanvas()  # холст для рисования
        self.draw28x28.setFixedSize(143, 143)
        self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))

        self.preview = QtWidgets.QLabel()  # холст для просмотра
        self.preview.setPixmap(QtGui.QPixmap(140, 140))
        self.preview.pixmap().fill(QtGui.QColor(QtCore.Qt.GlobalColor.white))
        self.preview.setPixmap(self.print_grid(self.preview.pixmap()))
        self.preview.setFixedSize(143, 143)
        self.preview_show_grid = True  # флаг рисования пиксельной границы

        # слайдер изменения толщины кисти рисования
        self.slider_brush_size = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical, self)
        self.slider_brush_size.setMinimum(1)
        self.slider_brush_size.setMaximum(20)
        self.slider_brush_size.setValue(7)
        self.slider_brush_size.valueChanged[int].connect(self.draw_change_brush_size)
        self.draw_brush_info = new_text(self, str(self.slider_brush_size.value()), alignment="c")
        # переключить сетку
        self.tb_toggle_grid = new_button(self, "tb", self.tr("Toggle grid"), "glyph_grid", the_color,
                                         self.draw_toggle_grid, True, True, tooltip=self.tr("Toggle grid"))

        brush_size_lay = QtWidgets.QVBoxLayout()
        slider_lay = QtWidgets.QHBoxLayout()
        slider_lay.addWidget(self.slider_brush_size)
        brush_size_lay.addWidget(self.draw_brush_info)
        brush_size_lay.addLayout(slider_lay)
        brush_size_lay.addWidget(self.tb_toggle_grid)

        # Устанавливаем разметку для виджетов на вкладке
        self.gb_draw = QtWidgets.QGroupBox(self.tr("Draw"))
        self.gb_preview = QtWidgets.QGroupBox(self.tr("Preview"))
        for group, widget in ((self.gb_draw, self.draw28x28),
                              (self.gb_preview, self.preview)):
            group.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            v_lay = QtWidgets.QVBoxLayout()
            v_lay.addWidget(widget)
            group.setLayout(v_lay)

        panel_lay = QtWidgets.QVBoxLayout()  # панель для работы с датасетом
        # инструменты: запустить обучение
        self.tb_start_train = new_button(self, "tb", self.tr("Start train"), "glyph_train", the_color,
                                         self.start_training, False, False, tooltip=self.tr("Start train"))
        # инструменты: загрузить случайное изображение
        self.tb_get_random = new_button(self, "tb", self.tr("Load random image"), "glyph_dice", the_color,
                                        self.get_random_image, False, False, tooltip=self.tr("Load random image"))
        # инструменты: прогнать модель по тестовому набору MNIST
        self.tb_test_model = new_button(self, "tb", self.tr("Test model with MNIST"), "glyph_pen_code", the_color,
                                        self.test_model, tooltip=self.tr("Test model with MNIST"))
        # инструменты: обработать изображение с помощью модели
        self.tb_use_model = new_button(self, "tb", self.tr("Use model"), "glyph_data_graph", the_color,
                                       self.use_model, tooltip=self.tr("Use model for current image"))

        tools = [self.tb_use_model, self.tb_get_random, self.tb_test_model, self.tb_start_train]
        self.tb_use_model.setEnabled(False)  # Т.к. изначально никакой модели не загружено, отключаем использование...
        self.tb_test_model.setEnabled(False)  # ...и тестирование
        for tool in tools:
            panel_lay.addWidget(tool)
            tool.setIconSize(QtCore.QSize(config.UI_AZ_MNIST_ICON_PANEL, config.UI_AZ_MNIST_ICON_PANEL))
        panel_lay.addStretch(1)

        h_layout = QtWidgets.QHBoxLayout()  # компоновщик рисования, предпросмотра и инструментов
        h_layout.addWidget(self.gb_draw)
        h_layout.addLayout(brush_size_lay)
        h_layout.addWidget(self.gb_preview)
        h_layout.addLayout(panel_lay)

        # инструменты 2: очистить лог
        self.tb_clear_log = new_button(self, "tb", self.tr("Clear log"), "glyph_clear", the_color,
                                       lambda: self.info.clear(), tooltip=self.tr("Clear log"))
        self.tb_show_model_data = new_button(self, "tb", self.tr("Show model data"), "glyph_clear", the_color,
                                             self.show_model_data, True, tooltip=self.tr("Show model data"))
        panel_lay2 = QtWidgets.QVBoxLayout()
        tools2 = [self.tb_clear_log]
        for tool2 in tools2:
            panel_lay2.addWidget(tool2)
            tool2.setIconSize(QtCore.QSize(config.UI_AZ_MNIST_ICON_PANEL, config.UI_AZ_MNIST_ICON_PANEL))
        panel_lay2.addStretch(1)

        # настройка цифр
        h_layout2 = QtWidgets.QHBoxLayout()  # компоновщик для "Цифр" и их вероятностей
        self.digits = {}  # словарь цифр, например 6: RoundProgressbar
        self.digits_chance = {}  # словарь вероятностей распознавания, например 6: QLabel.text
        for i in range(10):  # автоматом делаем все 10 цифр
            digit_v = QtWidgets.QVBoxLayout(self)
            digit_v.setSpacing(0)
            digit_v.setContentsMargins(0, 0, 0, 0)
            digit_lbl = QtWidgets.QLabel(f"{(i * 10 + 10):.0f}%")
            digit_lbl.setFixedHeight(14)
            digit_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
            digit_lbl.setIndent(0)

            the_digit = RoundProgressbar(self, QtGui.QColor(the_color), thickness=2, value=10 * i + 10,
                                         maximum=100, digit=i, digit_size=11)
            the_digit.setFixedSize(config.UI_AZ_MNIST_DIGITS_SIZE, config.UI_AZ_MNIST_DIGITS_SIZE)
            self.digits[i] = the_digit
            self.digits_chance[i] = digit_lbl
            digit_v.addWidget(digit_lbl)
            digit_v.addWidget(the_digit)
            digit_v.addStretch(1)

            line = QtWidgets.QFrame()  # добавляем линию-разделитель
            line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
            line.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
            # размещаем всё
            h_layout2.addLayout(digit_v)
            if i < 9:
                h_layout2.addWidget(line)
        h_layout2.addStretch(1)

        self.gb_settings = QtWidgets.QGroupBox(self.tr("Input settings"))
        self.tab_inputs = QtWidgets.QTabWidget()
        self.tab_inputs.setStyleSheet("QTabBar::tab { width: 200px; }")

        tab_perceptron = QtWidgets.QWidget()
        tab_perceptron.setLayout(self.ui_perceptron())
        tab_cnn = QtWidgets.QWidget()

        self.tab_inputs.addTab(tab_perceptron, "Perceptron...")
        self.tab_inputs.addTab(tab_cnn, "Convolutional neural network...")
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.tab_inputs)
        self.gb_settings.setLayout(lay)

        # Handler текущей модели MNIST
        self.mnist_handler = MNISTHandler(self)
        lay_handler = QtWidgets.QVBoxLayout()
        lay_handler.addWidget(self.mnist_handler)
        self.gb_model = QtWidgets.QGroupBox(self.tr("Model"))
        self.gb_model.setLayout(lay_handler)
        from ui import set_margins_recursive
        set_margins_recursive(self.gb_model, 0, 0, 0, 0, 0)

        self.gb_result = QtWidgets.QGroupBox(self.tr("Results"))  # результаты
        lay_result = self.ui_result()
        self.gb_result.setLayout(lay_result)

        # Итоговый компоновщик
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addLayout(h_layout)  # компонуем рисовальщика, предпросмотр
        v_layout.addLayout(h_layout2)  # и результат расчёта
        v_layout.addStretch(1)
        h_layout3 = QtWidgets.QHBoxLayout()
        h_layout3.addLayout(v_layout)
        h_layout3.addWidget(self.gb_model)
        h_layout3.addLayout(panel_lay2)
        h_layout3.addWidget(self.info, 1)  # делаем вывод максимальным
        layout.addWidget(self.gb_settings)
        layout.addLayout(h_layout3)
        layout.addWidget(self.gb_result, 1)

    def ui_result(self):
        h_lay = QtWidgets.QHBoxLayout()
        self.tb_add_and_test_model = new_button(self, "tb", self.tr("Test model and add to table"), "glyph_add2",
                                                the_color, self.add_and_test_model,
                                                icon_size=config.UI_AZ_MNIST_ICON_PANEL,
                                                tooltip=self.tr("Test model and add to table"))
        self.headers_results = [self.tr("Type"),
                                self.tr("Platform"),
                                self.tr("Unique id"),
                                self.tr("Epochs"),
                                self.tr("Layers"),
                                self.tr("layers splitting"),
                                self.tr("Learning rate"),
                                self.tr("Activate function"),
                                self.tr("Dataset using"),
                                self.tr("Shuffle data"),
                                self.tr("Loss for training"),
                                self.tr("Accuracy for training"),
                                self.tr("Accuracy for test"),
                                self.tr("Unique id")]
        self.table_results = QtWidgets.QTableView()
        self.model_results = AzTableModel([["", "", "", "", "", "", "", "", "", "", "", "", "", ""]],
                                          self.headers_results)
        self.table_results.setModel(self.model_results)
        self.adjust_table_results()
        h_lay.addWidget(self.tb_add_and_test_model)
        h_lay.addStretch(1)
        v_lay = QtWidgets.QVBoxLayout()
        v_lay.addLayout(h_lay)
        v_lay.addWidget(self.table_results)
        return v_lay

    def adjust_table_results(self):
        if self.model_results.columnCount() > 0:  # для столбцов
            header = self.table_results.horizontalHeader()
            for col in range(self.model_results.columnCount()):
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        if self.model_results.rowCount() > 0:  # для строк
            for row in range(self.model_results.rowCount()):  # выравниваем высоту
                self.table_results.setRowHeight(row, 16)

    def ui_perceptron(self):
        self.platform_label = new_text(self.tr("Platform:"))
        self.cbx_platform = new_cbx(self, ["numpy"])
        self.epochs_label = new_text(self.tr("Epoch:"))
        self.cbx_epochs = new_cbx(self, ["1", "2", "3", "4", "5", "10", "20"], True, QtGui.QIntValidator(1, 30))
        self.activ_func_label = new_text(self.tr("Activation function:"))
        # перечень функций в словаре формируем автоматически
        self.cbx_activ_func = new_cbx(self, activation_functions.keys())
        self.number_of_layers_label = new_text(self.tr("Layers number:"))
        self.cbx_number_of_layers = new_cbx(self, ["1", "2", "3", "4", "5", "10"], True, QtGui.QIntValidator(1, 30))
        self.cbx_number_of_layers.setToolTip(self.tr("The input layer is ignored. If one layer is specified, it will "
                                                     "also be the output layer (784x10)."))

        self.using_dataset_label = new_text(self.tr("Dataset usage, %:"))
        self.cbx_using_dataset = new_cbx(self, ["1", "5", "10", "15", "20", "25", "50", "75", "100"], True,
                                         QtGui.QIntValidator(1, 100))
        self.chk_use_random_data = QtWidgets.QCheckBox(self.tr("Shuffle data from MNIST"))
        self.learning_rate_label = new_text(self, self.tr("Learning rate:"))
        self.cbx_learning_rate = new_cbx(self, ["0.01", "0.005", "0.001", "0.1", "0.5"], True,
                                         QtGui.QDoubleValidator(0.0001, 1.0, 4))
        self.layers_splitting_label = new_text(self, self.tr("Layers splitting:"))
        self.cbx_layers_splitting = new_cbx(self, interpolation_functions.keys())

        self.settings_labels = [self.platform_label, self.epochs_label, self.activ_func_label,
                                self.number_of_layers_label, self.learning_rate_label, self.using_dataset_label,
                                self.layers_splitting_label]
        self.settings_widgets = [self.cbx_platform, self.cbx_epochs, self.cbx_activ_func, self.cbx_number_of_layers,
                                 self.cbx_learning_rate, self.cbx_using_dataset, self.cbx_layers_splitting]

        grid_layout = QtWidgets.QGridLayout()
        # заполняем парами
        for i, (label, widget) in enumerate(zip(self.settings_labels, self.settings_widgets)):
            grid_layout.addWidget(label, 0, i)
            grid_layout.addWidget(widget, 1, i)
        grid_layout.addWidget(self.chk_use_random_data, 0, grid_layout.columnCount())

        grid_layout.setSpacing(0)  # настраиваем расстояние между элементами ui "исходных параметров"
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        return grid_layout

    def add_and_test_model(self):
        # TODO: добавить полный тест на тестовых данных MNIST
        pass

    def get_random_image(self):
        img = load_image_from_dataset(self.settings.read_dataset_mnist())  # извлекаем случайное изображение из датасета
        self.current_img = np.reshape(img.astype("float32") / 255, (-1, 1))
        img = 255 - img  # инвертируем
        # конвертация массива numpy -> QImage
        q_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_Grayscale8)

        # создаем объект QPixmap
        pixmap = QtGui.QPixmap.fromImage(q_img)
        self.preview_show_mnist(pixmap)  # отправляем на отрисовку

    @staticmethod
    def load_test(path):
        with np.load(path) as file:
            x_test = file['x_test'].astype("float32") / 255  # конвертация из RGB в Unit RGB
            # преобразование массива из (60000, 28, 28) в формат (60000, 784)
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1] * x_test.shape[2]))
            # выходные данные
            y_test = file['y_test']
            # y_test = y_test[sel_inx]  # ограничиваем набор датасета при 100% = 60000
            y_test = np.eye(10)[y_test]
            return x_test, y_test

    def test_model(self):
        x_test, y_test = self.load_test(self.settings.read_dataset_mnist())

        print("in progress...")

    def show_model_data(self):
        print("show model...")

    def set_digits(self, result):
        """Установка значений цифры и её вероятности"""
        for i, dig in enumerate(self.digits):
            self.digits[i].set_base_color(QtGui.QColor(128, 128, 128))  # ставим всем обычный цвет
            self.digits[i].set_value(result[i])
            if result[i] < 0.5:
                self.digits_chance[i].setText("-")
            else:
                self.digits_chance[i].setText(f"{round(result[i])}%")
        if self.settings.read_ui_theme() == "light":  # в зависимости от текущей темы выбираем цвет
            current_color = the_color
        else:
            current_color = the_color
        # для цифры с максимальной величиной устанавливаем яркий цвет шрифта
        self.digits[int(np.argmax(result))].set_base_color(QtGui.QColor(current_color))

    def clear_digits(self):
        """Очистка значений цифр и их вероятностей"""
        for i, dig in enumerate(self.digits):
            self.digits[i].set_value(0)
            self.digits_chance[i].setText("-")

    def use_model(self):
        """Обработать изображение с помощью текущей модели и установить значения в виджетах"""
        self.set_digits(self.mnist_handler.use_model(self.current_img))

    @QtCore.pyqtSlot(str)
    def toggle_use_model(self, msg):
        """Обработка событий модели"""
        if msg == "model_is_set":
            self.tb_use_model.setEnabled(True)
            self.tb_test_model.setEnabled(True)
        elif msg == "model_is_saved":
            self.signal_info.emit(self.tr(f"Model saved: {self.mnist_handler.model_params['uniq_id']}"))
        elif msg == "model_was_load":
            self.signal_info.emit(self.tr(f"Model loaded: {self.mnist_handler.model_params['uniq_id']}"))
        else:
            self.tb_test_model.setEnabled(False)
            self.tb_use_model.setEnabled(False)

    def start_training(self):
        """Запуск на обучение НС"""
        settings = {"uniq_id": helper.generate_random_name(),
                    "nn_type": self.tab_inputs.tabText(self.tab_inputs.currentIndex()),
                    "platform": self.cbx_platform.currentText(),
                    "accuracy": "-",
                    "loss": "-",
                    "activ_funct": self.cbx_activ_func.currentText(),
                    "layers_splitting": self.cbx_layers_splitting.currentText(),
                    "dataset_using": self.cbx_using_dataset.currentText(),
                    "epochs": self.cbx_epochs.currentText(),
                    "number_of_layers": self.cbx_number_of_layers.currentText(),
                    "shuffle_data": self.chk_use_random_data.isChecked(),
                    "learning_rate": self.cbx_learning_rate.currentText(),
                    }

        self.store_settings()  # запоминаем выбранные настройки
        self.add_message_info("\n", False)

        if self.tab_inputs.tabText(self.tab_inputs.currentIndex()) == "Perceptron":  # тип НС "перцептрон"
            self.tb_start_train.setEnabled(False)  # Делаем кнопку неактивной
            self.mnist_worker.get_params(**settings)  # инициализируем настройки
            self.mnist_worker.start()  # Запускаем поток
        elif self.tab_inputs.tabText(self.tab_inputs.currentIndex()) == "Convolutional neural network":  # тип CNN
            self.inner_signal.emit(self.tr("Not ready yet..."))  # TODO: CNN
            return

    @QtCore.pyqtSlot()
    def mnist_on_started(self):  # Вызывается при запуске потока
        self.signal_info.emit(self.tr("------------------ Training start ------------------"))
        self.mnist_handler.change_icon("red")  # меняем иконку, сигнализируя, что идет процесс и...
        self.mnist_handler.tb_load.setEnabled(False)  # ...отключаем возможность загружать сохранённую модель

    @QtCore.pyqtSlot()
    def mnist_on_finished(self):  # Вызывается при завершении потока
        self.signal_info.emit(self.tr("-------------- Model training complete -------------"))
        self.tb_start_train.setEnabled(True)  # Делаем кнопку сохранения активной
        self.mnist_handler.tb_load.setEnabled(True)

    @QtCore.pyqtSlot(str)
    def mnist_on_change(self, s):
        self.signal_info.emit(s)

    @QtCore.pyqtSlot(str)
    def add_message_info(self, message, show_time=True):  # передача информации в лог
        current_time = datetime.now().time().strftime("%H:%M:%S") + ": "
        if not show_time:
            current_time = ""
        message = current_time + message
        self.info.setPlainText(message + "\n" + self.info.toPlainText())

    @QtCore.pyqtSlot(int)
    def draw_change_brush_size(self, val):
        """Изменение размера кисти"""
        self.draw_brush_info.setText(str(val))
        self.draw28x28.set_pen_size(val)

    def draw_toggle_grid(self):
        """Установка параметра включение/отключение сетки при рисовании"""
        self.preview_show_grid = self.tb_toggle_grid.isChecked()

    @staticmethod
    def print_grid(pixmap):
        """Отрисовка сетки"""
        # увеличиваем на 1 пиксель, чтобы сетка была ровной
        new_pixmap = QtGui.QPixmap(pixmap.width() + 1, pixmap.height() + 1)
        painter = QtGui.QPainter(new_pixmap)
        painter.drawPixmap(0, 0, pixmap.width(), pixmap.height(), pixmap)  # рисуем старую в новом
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.gray, 1))
        # рисуем сетку
        for x in range(0, new_pixmap.width(), 5):
            painter.drawLine(x, 0, x, new_pixmap.height())
        for y in range(0, new_pixmap.height(), 5):
            painter.drawLine(0, y, new_pixmap.width(), y)
        painter.end()
        return new_pixmap

    @staticmethod
    def convert_pixmap_to_numpy(pixmap):
        """Конвертация из картинки QPixmap (оттенки серого) в один столбец (массив numpy[-1, 1])"""
        image = pixmap.toImage()
        width, height = image.height(), image.width()  # ширина и высота
        array = np.empty((height, width), dtype=np.float32)  # создаём пустой массив

        # заполняем пустой массив значениями
        for y in range(height):
            for x in range(width):
                # хотя нас ведь серый, поэтому можно использовать любой цвет, через QColor
                gray_value = QtGui.qGray(image.pixel(x, y))
                array[y, x] = (255 - gray_value) / 255  # инвертируем значения и переводим UnitRGB
        array = np.reshape(array, (-1, 1))
        return array

    def preview_show_draw(self, pixmap):  # пикселизация нарисованного объекта
        the28x28 = pixmap.scaled(28, 28, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                 QtCore.Qt.TransformationMode.SmoothTransformation)  # сжимаем...
        pixelated = the28x28.scaled(28 * 5, 28 * 5, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                                    QtCore.Qt.TransformationMode.FastTransformation)  # ...и разжимаем
        # снова преобразуем к 28х28
        to_mass = pixelated.scaled(28, 28, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.FastTransformation)
        self.current_img = self.convert_pixmap_to_numpy(to_mass)  # записываем изображение в память

        if self.preview_show_grid:  # определяем необходимость отрисовки сетки
            pixelated = self.print_grid(pixelated)
        self.preview.setPixmap(pixelated)
        self.gb_preview.setTitle(self.tr("Preview: drawing"))
        self.update()

    def preview_show_mnist(self, pixmap):  # отрисовка объекта из датасета MNIST
        mnist_img = pixmap.scaled(28 * 5, 28 * 5, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                                  QtCore.Qt.TransformationMode.FastTransformation)
        if self.preview_show_grid:  # отрисовка сетки
            mnist_img = self.print_grid(mnist_img)
        self.preview.setPixmap(mnist_img)
        self.gb_preview.setTitle(self.tr("Preview: MNIST"))
        self.update()

    def restore_last_saved_settings(self):
        """Восстановление настроек"""
        self.cbx_epochs.setCurrentText(self.settings.read_mnist_epochs())
        self.cbx_using_dataset.setCurrentText(self.settings.read_mnist_dataset_using())
        self.cbx_learning_rate.setCurrentText(self.settings.read_mnist_learning_rate())
        self.chk_use_random_data.setChecked(self.settings.read_mnist_shuffle_dataset())
        self.cbx_activ_func.setCurrentText(self.settings.read_mnist_activ_func())
        self.cbx_number_of_layers.setCurrentText(self.settings.read_mnist_layers_number())

    def store_settings(self):
        """Сохранение настроек"""
        self.settings.write_mnist_epochs(self.cbx_epochs.currentText())
        self.settings.write_mnist_dataset_using(self.cbx_using_dataset.currentText())
        self.settings.write_mnist_learning_rate(self.cbx_learning_rate.currentText())
        self.settings.write_mnist_shuffle_dataset(self.chk_use_random_data.isChecked())
        self.settings.write_mnist_activ_func(self.cbx_activ_func.currentText())
        self.settings.write_mnist_layers_number(self.cbx_number_of_layers.currentText())

    def tr(self, text):
        return QtCore.QCoreApplication.translate("PageMNIST", text)

    def translate_ui(self):
        self.mnist_handler.translate_ui()
        self.model_results.setHorizontalHeaderLabels([self.tr("Type"),
                                                      self.tr("Platform"),
                                                      self.tr("Unique id"),
                                                      self.tr("Epochs"),
                                                      self.tr("Layers"),
                                                      self.tr("layers splitting"),
                                                      self.tr("Learning rate"),
                                                      self.tr("Activate function"),
                                                      self.tr("Dataset using"),
                                                      self.tr("Shuffle data"),
                                                      self.tr("Loss for training"),
                                                      self.tr("Accuracy for training"),
                                                      self.tr("Accuracy for test"),
                                                      self.tr("Unique id")])
        # self.adjust_table_results()

        self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))
        self.tab_inputs.setTabText(0, self.tr("Perceptron"))
        self.tab_inputs.setTabText(1, self.tr("Convolutional neural network"))

        self.gb_settings.setTitle(self.tr("Input settings"))
        self.gb_draw.setTitle(self.tr('Draw'))
        self.gb_preview.setTitle(self.tr('Preview'))
        self.tb_toggle_grid.setToolTip(self.tr("Toggle grid"))

        self.tb_start_train.setToolTip(self.tr("Start train"))
        self.tb_get_random.setToolTip(self.tr("Load random image"))
        self.tb_clear_log.setToolTip(self.tr("Clear log"))
        self.tb_use_model.setToolTip(self.tr("Use model for current image"))

        self.gb_model.setTitle(self.tr("Model"))
        self.gb_result.setTitle(self.tr("Results"))

        self.platform_label.setText(self.tr("Platform:"))
        self.epochs_label.setText(self.tr("Epoch:"))
        self.activ_func_label.setText(self.tr("Activation function:"))
        self.number_of_layers_label.setText(self.tr("Layers number:"))
        self.cbx_number_of_layers.setToolTip(self.tr("The input layer is ignored. If one layer is specified, it will "
                                                     "also be the output layer (784x10)."))
        self.using_dataset_label.setText(self.tr("Dataset usage, %:"))
        self.chk_use_random_data.setText(self.tr("Shuffle data from MNIST"))
        self.learning_rate_label.setText(self.tr("Learning rate:"))
        self.layers_splitting_label.setText(self.tr("Layers splitting:"))


# ----------------------------------------------------------------------------------------------------------------------
class AzCanvas(QtWidgets.QLabel):
    """
    Холст рисования цифр, для распознавания при работе MNIST
    """
    signal_draw = QtCore.pyqtSignal(QtGui.QPixmap)  # сигнал завершения отрисовки

    def __init__(self):
        super().__init__()
        pixmap = QtGui.QPixmap(140, 140)  # кратно 28 в пять раз
        self.clear_canvas(pixmap)
        self.setPixmap(pixmap)
        self.draw = False  # рисование
        self.last_x, self.last_y = None, None  # координаты точки рисования
        self.pen_color = QtCore.Qt.GlobalColor.black
        self.pen_size = 7

    def set_pen_size(self, size):
        """Смена толщины кисти для рисования"""
        size = min(max(size, 1), 30)
        self.pen_size = size

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:  # Ставим добро на рисование
            self.draw = True

    def mouseMoveEvent(self, event):  # рисование
        if self.draw:  # флаг активен
            if self.last_x is None:  # вначале нет событий
                self.last_x = event.x()
                self.last_y = event.y()
                return

            painter = QtGui.QPainter(self.pixmap())  # устанавливаем картину для рисования
            pen = painter.pen()  # инструмент
            pen.setWidth(self.pen_size)
            pen.setColor(self.pen_color)  # цвет
            painter.setPen(pen)  # берем инструмент
            painter.drawLine(self.last_x, self.last_y, event.x(), event.y())
            painter.end()
            self.update()

            # Обновляем текущие значения координат
            self.last_x = event.x()
            self.last_y = event.y()

    def mouseReleaseEvent(self, event):  # завершение рисунка, а по ПКМ - очистка
        if event.button() == QtCore.Qt.MouseButton.RightButton:  # Очищаем
            self.clear_canvas(self.pixmap())
        self.draw = False
        self.last_x = None
        self.last_y = None
        self.signal_draw.emit(self.pixmap())  # отправляем сигнал-картинку

    def clear_canvas(self, pixmap):  # очистка холста = по сути заливка всего белым цветом
        pixmap.fill(QtCore.Qt.GlobalColor.white)
        self.update()


# ----------------------------------------------------------------------------------------------------------------------
class RoundProgressbar(QtWidgets.QWidget):
    def __init__(
            self,
            parent=None,
            color: QtGui.QColor = QtGui.QColor(170, 0, 255),
            size: int = 100,
            thickness: int = 10,
            value: int = 24,
            maximum: int = 100,
            round_edge: bool = False,
            bg_circle_color: QtGui.QColor = QtGui.QColor(0, 0, 0, 0),
            fill_bg_circle: bool = False,
            digit: int = 0,
            digit_size: int = 20,
            base_color: QtGui.QColor = QtGui.QColor(128, 128, 128)
    ):
        if parent is not None:
            super().__init__(parent=parent)
        elif parent is None:
            super().__init__()
        self._circular_size = size
        self._thickness = thickness
        self.resize(self._circular_size + (self._thickness * 2), self._circular_size + (self._thickness * 2))
        self._color = color
        self._maximum = maximum
        self._value = value
        self._alen = (self._value / self._maximum) * 360
        self._a = -(self._alen - 90)
        self._round_edge = round_edge
        self._bg_circle_color = bg_circle_color
        self._fill_bg_circle = fill_bg_circle
        self._digit = digit  # цифра
        self._digit_size = digit_size  # размер шрифта (использую шрифт Tahoma)
        self._base_color = base_color  # цвет шрифта

    def paintEvent(self, paint_event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(self._bg_circle_color, self._thickness - 1, QtCore.Qt.PenStyle.SolidLine))
        if self._fill_bg_circle:
            painter.setBrush(QtGui.QBrush(self._bg_circle_color, QtCore.Qt.BrushStyle.SolidPattern))
        elif not self._fill_bg_circle:
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawEllipse(self._thickness, self._thickness, self._circular_size, self._circular_size)
        if self._round_edge:
            painter.setPen(QtGui.QPen(self._color, self._thickness, QtCore.Qt.PenStyle.SolidLine,
                                      QtCore.Qt.PenCapStyle.RoundCap))
        elif not self._round_edge:
            painter.setPen(QtGui.QPen(self._color, self._thickness, QtCore.Qt.PenStyle.SolidLine,
                                      QtCore.Qt.PenCapStyle.FlatCap))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawArc(self._thickness, self._thickness, self._circular_size, self._circular_size, int(self._a * 16),
                        int(self._alen * 16))

        # ------------- az_realization -------------
        digit_str = str(self._digit)
        font = QtGui.QFont('Tahoma', self._digit_size)  # Lucida Console,
        metrics = QtGui.QFontMetrics(font)
        x = (self.width() - metrics.width(digit_str)) // 2
        y = (self.height() - metrics.height()) // 2 + metrics.ascent()
        painter.setFont(font)
        painter.setPen(self._base_color)
        painter.drawText(x, y, digit_str)
        # painter.drawText(self.rect(), QtCore.Qt.AlignCenter, str(self._digit))
        # ------------- end az_realization -------------
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._circular_size = (self.width() - (self._thickness * 2)) if self.width() < self.height() else (
                self.height() - (self._thickness * 2))

    def get_value(self):
        return self._value

    def set_base_color(self, color: QtGui.QColor):
        self._base_color = color
        self.update()

    @QtCore.pyqtSlot(int)
    def set_value(self, value: int):
        self._value = value
        self._alen = (self._value / self._maximum) * 360
        self._a = -(self._alen - 90)
        self.update()

    value = pyqtProperty(int, get_value, set_value)

    def get_maximum(self):
        return self._maximum

    @QtCore.pyqtSlot(int)
    def set_maximum(self, value: int):
        self._maximum = value
        self._alen = (self._value / self._maximum) * 360
        self._a = -(self._alen - 90)
        self.update()

    maximum = pyqtProperty(int, get_maximum, set_maximum)

    def get_thickness(self):
        return self._thickness

    @QtCore.pyqtSlot(int)
    def set_thickness(self, value: int):
        self._thickness = value
        self._circular_size = (self.width() - (self._thickness * 2)) if self.width() < self.height() else (
                self.height() - (self._thickness * 2))
        self.update()

    thickness = pyqtProperty(int, get_thickness, set_thickness)

    def get_color(self):
        return self._color

    @QtCore.pyqtSlot(QtGui.QColor)
    def set_color(self, color: QtGui.QColor):
        self._color = color
        self.update()

    color = pyqtProperty(QtGui.QColor, get_color, set_color)

    def get_bg_circle_color(self):
        return self._bg_circle_color

    @QtCore.pyqtSlot(QtGui.QColor)
    def set_bg_circle_color(self, color: QtGui.QColor):
        self._bg_circle_color = color
        self.update()

    background_circle_color = pyqtProperty(QtGui.QColor, get_bg_circle_color, set_bg_circle_color)

    def get_round_edge(self):
        return self._round_edge

    @QtCore.pyqtSlot(bool)
    def set_round_edge(self, value: bool):
        self._round_edge = value
        self.update()

    round_edge = pyqtProperty(bool, get_round_edge, set_round_edge)

    def get_fill_bg_circle(self):
        return self._fill_bg_circle

    @QtCore.pyqtSlot(bool)
    def set_fill_bg_circle(self, value: bool):
        self._fill_bg_circle = value
        self.update()

    fill_background_circle = pyqtProperty(bool, get_fill_bg_circle, set_fill_bg_circle)


# ----------------------------------------------------------------------------------------------------------------------
class MNISTHandler(QtWidgets.QWidget):
    """
    Виджет для хранения и отображения текущей модели (обученной НС) MNIST
    """
    signal_mnist_handler = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MNISTHandler, self).__init__(parent)
        self.settings = AppSettings()
        self.model_params = None  # параметры модели
        self.model_data = None  # данные модели
        self.current_status = None

        self.label_status = new_text(self.tr("Model not loaded"))
        self.current_status = self.label_status.text()
        self.btn_status = new_button(self, "tb", icon="circle_grey", color=None, icon_size=16,
                                     tooltip=self.tr("Model status"))
        self.tb_save = new_button(self, "tb", self.tr("Save current model"), "glyph_save2", the_color, self.save_model,
                                  icon_size=16, tooltip=self.tr("Save current model"))
        self.tb_load = new_button(self, "tb", self.tr("Load last saved model"), "glyph_folder_recent", the_color,
                                  self.load_model, icon_size=16,
                                  tooltip=self.tr("Load last saved model"))
        self.table_params = QtWidgets.QTableView()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.btn_status)
        hlayout.addWidget(self.label_status)
        hlayout.addWidget(self.tb_save)
        hlayout.addWidget(self.tb_load)
        finish_lay = QtWidgets.QVBoxLayout(self)
        finish_lay.addLayout(hlayout)
        finish_lay.addWidget(self.table_params)
        self.tb_save.setEnabled(False)  # отключаем модель, сохранять пока нечего

    def save_model(self):
        """Сохранение модели со случайным именем из 5 символов, по умолчанию в каталоге с MNIST, в виде словаря"""
        if os.path.exists(os.path.dirname(self.settings.read_dataset_mnist())):  # проверяем есть ли каталог с MNIST?
            # тогда сохраняем модель там
            new_name = os.path.join(os.path.dirname(self.settings.read_dataset_mnist()),
                                    self.model_params["uniq_id"] + ".pkl")

        else:  # иначе вызываем диалог
            new_name = az_file_dialog(self, self.tr("Select dir to save model"), self.settings.read_last_dir(),
                                      dir_only=True)
            if not new_name:  # нажата кнопка "Отмена"
                return
            new_name = os.path.join(new_name, self.model_params["uniq_id"] + ".pkl")

        helper.save_pickle(new_name, {"params": self.model_params, "model_data": self.model_data})  # сохраняем
        self.settings.write_mnist_model_file(new_name)  # запоминаем
        self.signal_mnist_handler.emit("model_is_saved")  # сообщаем, что модель сохранена

    def load_model(self):
        """Загрузка сохранённой модели"""
        if os.path.exists(self.settings.read_mnist_model_file()):  # сначала смотрим, есть ли сохраненные?
            data = helper.load_pickle(self.settings.read_mnist_model_file())  # загружаем данные
        else:
            sel_file = az_file_dialog(self, self.tr("Load MNIST model *.pkl"), self.settings.read_last_dir(),
                                      dir_only=False, filter="Pickle (*.pkl)", initial_filter="pickle (*.pkl)")
            if not helper.check_files(sel_file):  # нажали "Отмена"
                return
            data = helper.load_pickle(sel_file[0])
        self.set_model((data["params"], data["model_data"]))  # устанавливаем модель
        self.signal_mnist_handler.emit("model_was_load")

    @QtCore.pyqtSlot(tuple)
    def set_model(self, data):
        """Установка новой модели, данные приходят в виде кортежа: ({словаря параметров} и {словаря данных модели}).
        Данные модели это {"data":(bias_layer1, weights_layer1, activ_func1), (bias_layer2, ...), ... }"""
        self.model_params, self.model_data = data
        self.set_table_data()  # настраиваем отображение параметров модели в таблице
        now = datetime.now().strftime("%H:%M:%S")
        self.change_status(self.tr(f"Model was set at {now}"), "green", "model_is_set")
        self.tb_save.setEnabled(True)

    def use_model(self, image_data):
        """Использование обученной модели для определения данных. Входные данные image_data - изображение переведенное
        в формат numpy, в значениях пикселей от 0 до 1: [1, 784]"""
        image = image_data
        [bias_list, weights_list, activ_funcs_list] = zip(*self.model_data["data"])  # распаковываем данные нейросети
        current_layer = image
        for bias, weights, activ_func in zip(bias_list, weights_list, activ_funcs_list):
            layer = bias + weights @ current_layer
            activ_layer = get_activ_func(activ_func, layer)
            current_layer = activ_layer
        result = [elem[0] * 100 for elem in current_layer]  # формируем результаты
        return result

    def set_table_data(self):
        """Настраиваем таблицу"""
        # создаем список кортежей (key, [item]) и с помощью zip(*), распаковываем кортеж в два отдельных списка
        vertical_headers, data = zip(*[(key, [item]) for key, item in self.model_params.items()])
        model = AzTableModel(data, ["Model settings"], vertical_data=vertical_headers,
                             no_rows_captions=True)  # модель для QTableView
        self.table_params.setModel(model)
        # наводим красоту
        if model.rowCount() > 0:  # для строк
            for row in range(model.rowCount()):  # выравниваем высоту
                self.table_params.setRowHeight(row, ROW_H)
        if model.columnCount() > 0:
            header = self.table_params.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def change_status(self, message, color, handler_info):
        """Изменение статуса: сообщения в QLabel, цвета иконки и отправление сигнала о готовности"""
        self.current_status = message
        self.label_status.setText(self.current_status)
        self.change_icon(color)
        self.signal_mnist_handler.emit(handler_info)

    def change_icon(self, color):
        if color == "red":
            icon = "circle_red"
        elif color == "green":
            icon = "circle_green"
        else:
            icon = "circle_grey"
        self.btn_status.setIcon(new_icon(icon))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("MNISTHandler", text)

    def translate_ui(self):
        self.label_status.setText(self.tr(self.current_status))
        self.btn_status.setToolTip(self.tr("Model status"))
        self.tb_save.setToolTip(self.tr("Save current model"))
        self.tb_load.setToolTip(self.tr("Load last saved model"))
        self.btn_status.setToolTip(self.tr("Model status"))


# ----------------------------------------------------------------------------------------------------------------------
class MNISTWorker(QtCore.QThread):
    """Поток обучения, загрузка данных персептрона MNIST"""
    # TODO: добавить время обучения
    inner_signal = QtCore.pyqtSignal(str)  # передача сообщения
    signal_model = QtCore.pyqtSignal(tuple)  # сигнал передачи модели

    def __init__(self, parent=None):
        super(MNISTWorker, self).__init__()
        # QtCore.QThread.__init__(self, parent)
        self.params = None
        self.settings = AppSettings()
        self.layers = []
        self.epochs = []

    def get_training_info(self):
        self.training_info = self.tr(f"type: {self.params['nn_type']}; "
                                     f"epochs: {self.params['epochs']}; "
                                     f"activation: {self.params['activ_funct']}; "
                                     f"layers count: {self.params['number_of_layers']}; "
                                     f"shuffle mnist: {self.params['shuffle_data']}; "
                                     f"learning rate: {self.params['learning_rate']}; "
                                     f"dataset limit: {self.params['dataset_using']}%; "
                                     f"layers splitting: {self.params['layers_splitting']}; "
                                     f"platform: {self.params['platform']}; "
                                     f"layers: {self.params['layers']}; "
                                     f"unique id: {self.params['uniq_id']}")
        return self.training_info

    def get_params(self, **params):
        # инициализация начальных параметров через словарь
        self.params = params

    def run(self):
        # self.train_and_send_simple()  # можно посмотреть на более простую реализацию персептрона...
        # return  # ...с 1 входным слоем и 2 скрытыми слоями (784, 20, 10)

        images, labels, unused_inx = load_dataset(self.settings.read_dataset_mnist(), self.params["dataset_using"],
                                                  self.params["shuffle_data"], )
        if images is None:
            self.inner_signal.emit(self.tr("MNIST file not found, check for source data."))
            return
        # Определяем размерность слоёв в зависимости от их количества и типа разбиения. Всегда min = 10, max = 784
        layers_sep = use_interpolation_func(self.params["layers_splitting"], 10, 784,
                                            int(self.params["number_of_layers"]))
        layers_sep = list(reversed([int(item) for item in layers_sep]))  # инвертируем и приводим к целым

        # Параметры обучения
        self.epochs.clear()  # очищаем списки эпох и слоёв не в конце, а...
        self.layers.clear()  # ...здесь, чтобы быть уверенным
        activ_func = self.params["activ_funct"]  # функция активации
        epochs = int(self.params["epochs"])  # количество эпох
        learning_rate = float(self.params["learning_rate"])  # скорость обучения
        for i in range(1, len(layers_sep)):  # собираем слои персептрона (если их несколько)
            perc = PerceptronLayer(height=layers_sep[i], width=layers_sep[i - 1], act_func=activ_func)
            self.layers.append(perc)
        self.params["layers"] = layers_sep
        self.get_training_info()  # формируем информацию о параметрах обучения...
        self.inner_signal.emit(self.tr(f"Training settings: {self.training_info}"))  # ...и отправляем её

        for epoch in range(epochs):
            epoch_loss = 0
            epoch_correct = 0
            for image, label in zip(images, labels):
                image = np.reshape(image, (-1, 1))
                label = np.reshape(label, (-1, 1))

                #  1. Прямое распространение от исходного слоя:
                self.layers[0].vals = self.layers[0].bias + self.layers[0].weights @ image
                self.layers[0].vals = get_activ_func(self.layers[0].act_func, self.layers[0].vals)  # активация

                if len(self.layers) > 1:  # более 1 скрытого слоя: прямое распространения для остальных скрытых слоёв
                    for i in range(1, len(self.layers)):
                        self.layers[i].vals = self.layers[i].bias + self.layers[i].weights @ self.layers[i - 1].vals
                        self.layers[i].vals = get_activ_func(self.layers[i].act_func, self.layers[i].vals)

                # 2. Расчет потерь/ошибок, используем MSE (СКО)
                epoch_loss += 1 / len(self.layers[-1].vals) * np.sum((self.layers[-1].vals - label) ** 2,
                                                                     axis=0)
                epoch_correct += int(np.argmax(self.layers[-1].vals) == np.argmax(label))  # счетчик предсказаний

                # 3. Обратное распространение ошибки (выходной уровень).
                # Разница между результатом и контрольным значением для последнего слоя
                self.layers[-1].delta = self.layers[-1].vals - label

                if len(self.layers) > 1:  # более 1 скрытого слоя: обратное распространения для остальных скрытых слоёв
                    for i in range(len(self.layers) - 1, 0, -1):  # завершаем на 2 слое от начала
                        self.layers[i].weights += -learning_rate * self.layers[i].delta @ np.transpose(
                            self.layers[i - 1].vals)
                        self.layers[i].bias += -learning_rate * self.layers[i].delta
                        self.layers[i - 1].delta = np.transpose(self.layers[i].weights) @ self.layers[i].delta * (
                                self.layers[i - 1].vals * (1 - self.layers[i - 1].vals))
                # первый слой
                self.layers[0].weights += -learning_rate * self.layers[0].delta @ np.transpose(image)
                self.layers[0].bias += -learning_rate * self.layers[0].delta

                # 4. Расчёт ошибок
                self.params["loss"] = str(round((epoch_loss[0] / images.shape[0]) * 100, 2)) + "%"
                self.params["accuracy"] = str(round((epoch_correct / images.shape[0]) * 100, 2)) + "%"
                # Изображение обработано

            # Эпоха завершена
            epochs_loss = round((epoch_loss[0] / images.shape[0]) * 100, 2)
            epoch_correct = round((epoch_correct / images.shape[0]) * 100, 2)
            self.inner_signal.emit(self.tr(f"Epoch {epoch + 1}: loss {epochs_loss}%; accuracy: {epoch_correct}%"))
            self.epochs.append((epoch_loss, epoch_correct))  # добавляем данные об ошибках этой эпохи

        # Подготавливаем данные для отправки
        self.params["layers"] = str(self.params["layers"])
        # self.params["layers"] = "; ".join(self.params["layers"])
        # структура данных: ({словарь параметров}, {данные обученной модели})
        data = (self.params, {"data": [(layer.bias, layer.weights, layer.act_func) for layer in self.layers],
                              "unused_inx": unused_inx})

        self.signal_model.emit(data)  # отправляем модель

    def train_and_send_simple(self):
        images, labels, unused_inx = load_dataset(self.settings.read_dataset_mnist(), self.params["dataset_using"],
                                                  self.params["shuffle_data"])
        if images is None:
            self.inner_signal.emit(self.tr("MNIST file not found, check for source data."))
            return
        self.inner_signal.emit(self.tr(f"Loaded {len(labels)} images from MNIST"))
        # слои следуют: 1 (исходный), 2 (скрытый), 3 (скрытый), ..., выходной слой
        # инициализируем случайные веса второго слоя, 20 строк х 28*28 (784) столбцов
        weights_layer_1 = np.random.uniform(-0.5, 0.5, (20, 784))
        bias_layer_1 = np.zeros((20, 1))  # смещение для второго слоя, инициализируем 20 строк х 1 столбец нулей

        weights_layer_2 = np.random.uniform(-0.5, 0.5, (10, 20))  # веса третьего (выходного) слоя
        bias_layer_2 = np.zeros((10, 1))  # смещения для третьего (выходного) слоя

        self.get_training_info()
        # определяем используемую функцию активации
        activ_func = self.params["activ_funct"]

        epochs = int(self.params["epochs"])
        e_loss = 0
        e_correct = 0  # коррекция ошибки
        learning_rate = float(self.params["learning_rate"])  # скорость обучения
        self.inner_signal.emit(self.tr(f"Training settings: {self.training_info}"))
        for epoch in range(epochs):
            for image, label in zip(images, labels):
                image = np.reshape(image, (-1, 1))  # преобразование массивов исходных данных в [784, 1]
                label = np.reshape(label, (-1, 1))  # [10, 1]

                # 1. Прямое распространение (к скрытому слою)
                # смещение + веса * данные изображения
                # мы перемножаем [20x784] на [784x1] и получаем [20x1]
                hidden_raw = bias_layer_1 + weights_layer_1 @ image  # [20, 1]
                hidden = get_activ_func(activ_func, hidden_raw)  # функция активации: выбираем через словарь [20, 1]

                # прямое распространение (к выходному слою)
                # мы перемножаем [10, 20] на [20, 1] и получаем [10, 1]
                output_raw = bias_layer_2 + weights_layer_2 @ hidden  # [10, 1]
                output = get_activ_func(activ_func, output_raw)  # [10, 1]

                # 2. Расчет потерь/ошибок, используем MSE (СКО)
                e_loss += 1 / len(output) * np.sum((output - label) ** 2, axis=0)
                e_correct += int(np.argmax(output) == np.argmax(label))

                # 3. Обратное распространение ошибки (выходной уровень).
                # delta = [10, 1] - [10, 1]
                delta_output = output - label  # дельта = разница между результатом и контрольным значением
                # изменяем веса выходного слоя [10, 20]
                weights_layer_2 += -learning_rate * delta_output @ np.transpose(hidden)
                # изменяем смещения выходного слоя [10, 1]
                bias_layer_2 += -learning_rate * delta_output

                # Обратное распространение ошибки (скрытый слой)
                delta_hidden = np.transpose(weights_layer_2) @ delta_output * (hidden * (1 - hidden))
                weights_layer_1 += -learning_rate * delta_hidden @ np.transpose(image)
                bias_layer_1 += -learning_rate * delta_hidden

                # 4. Расчёт ошибок
                loss = str(round((e_loss[0] / images.shape[0]) * 100, 2)) + "%"
                acc = str(round((e_correct / images.shape[0]) * 100, 2)) + "%"
                print(f"loss: {loss}; accuracy: {acc}")
            # Обучение завершено

            self.inner_signal.emit(self.tr(f"Epoch {epoch + 1}: loss {round((e_loss[0] / images.shape[0]) * 100, 2)}%"
                                           f"; accuracy: {round((e_correct / images.shape[0]) * 100, 2)}%"))
            e_loss = 0
            e_correct = 0

        # Подготавливаем данные для отправки
        # структура данных: ({словарь параметров}, {данные обученной модели})
        data = (self.params,
                {"data": [(bias_layer_1, weights_layer_1, activ_func), (bias_layer_2, weights_layer_2, activ_func)],
                 "unused_inx": unused_inx})
        self.signal_model.emit(data)  # отправляем модель

        self.epochs.clear()  # очищаем списки эпох...
        self.layers.clear()  # ...и слоёв


# ----------------------------------------------------------------------------------------------------------------------
class PerceptronLayer:  # Idea by Francesco Cagnin (integeruser)
    def __init__(self, height, width, act_func, init_func="random"):
        """
        В numpy идут сначала строки, затем столбцы
        height - высота массива (количество строк), rows;
        width - ширина массива (количество столбцов), cols;
        act_func - функция активации;
        init_func - функция инициализации весов;
        """
        super().__init__()
        self.depth = 1
        self.height = height  # height - высота массива (количество строк)
        self.width = width  # width - ширина массива (количество столбцов)
        self.init_func = init_func  # функция инициализации первичных значений весов
        self.weights = use_init_weights_func(init_func, (height, width))  # веса
        self.bias = np.zeros((height, 1))  # смещения
        self.act_func = act_func  # функция активации
        self.vals = None  # прямое распространение
        self.delta = None


# ----------------------------------------------------------------------------------------------------------------------
def load_image_from_dataset(path, shuffle=True, index=0):
    """
    Статическая функция, возвращает одно изображение MNIST
    Параметры: path - путь к файлу *.npz; shuffle - использование данных в случайном порядке; index - для выбора
    конкретного изображения. Изображение возвращается в формате 28*28 точек с яркостью от 0 до 255
    """
    if not helper.check_file(path):
        return None
    with np.load(path) as file:
        if shuffle:
            return random.choice(file['x_train'])
        else:
            index = min(max(index, 0), 60000)  # ограничиваем
            return file['x_train'][index]


# ----------------------------------------------------------------------------------------------------------------------
def load_dataset(path, using_percent=100, shuffle=False):
    """
    Загрузка датасета MNIST, возвращает перечень изображений, значений для них и перечень неиспользуемых индексов:
    x_train - изображения в формате: яркость 255 для ячейки, где есть контур цифры; 0 для пустого значения
    y_train - метка, соответствующая изображению цифра в формате int.
    Параметры: path - путь к файлу *.npz; using_percent - объем используемого датасета;
    shuffle - использование данных в случайном порядке
    """
    if not helper.check_file(path):
        return None, None

    with np.load(path) as file:
        unused_inx = None  # неиспользуемые индексы
        # преобразуем яркость 1 для ячейки, где есть контур цифры; 0 для пустого значения
        x_train = file['x_train'].astype("float32") / 255  # конвертация из RGB в Unit RGB
        # преобразование массива из (60000, 28, 28) в формат (60000, 784)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1] * x_train.shape[2]))

        # ограничение датасета: отвечает using_percent (при необходимости)
        num_rows = int(x_train.shape[0] * int(using_percent) / 100)
        # определяем флаг "случайных" данных
        if shuffle:
            # набираем случайных индексов
            sel_inx = np.random.choice(x_train.shape[0], num_rows, replace=False)  # следим, чтобы не было повторов
        else:
            sel_inx = np.arange(0, num_rows)
        unused_inx = set(range(x_train.shape[0])) - set(sel_inx)

        # формируем итоговый набор данных изображений
        x_train = x_train[sel_inx]

        # выходные данные
        y_train = file['y_train']
        y_train = y_train[sel_inx]  # ограничиваем набор датасета при 100% = 60000
        #                                                           6          1     ...      8
        # выходные 1-х матрицы в формате по 10 классов цифр [[0000001000][0100000000]...[0000000010]]]
        y_train = np.eye(10)[y_train]

        return x_train, y_train, unused_inx


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = PageMNIST()
    w.show()
    app.exec()
