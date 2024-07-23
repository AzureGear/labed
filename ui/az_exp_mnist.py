import random
import time

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from ui import new_text, new_cbx, new_button, new_icon, AzTableModel
from utils import AppSettings, helper, config
import matplotlib.pyplot as plt
import numpy as np
from ui.az_math import *
from datetime import datetime

the_color = config.UI_COLORS.get("experiments_color")
ROW_H = 16


# ----------------------------------------------------------------------------------------------------------------------
class PageMNIST(QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал передачи сообщения родительскому виджету
    signal_info = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения в self.info

    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)
        self.name = "MNIST"
        self.settings = AppSettings()
        self.current_img = None  # текущее изображение (без коррекции и пиксельной сетки)
        self.setup_ui()  # настройка интерфейса
        self.restore_last_saved_settings()  # восстановление сохранённых настроек
        # self.setStyleSheet("QWidget { border: 1px solid yellow; }")  # проверка отображения виджетов
        self.update_font_color()  # изменение цвета шрифта в зависимости от темы
        self.clear_digits()

        # поток для расчета нейронной сети QThread
        self.mnist_worker = MNISTWorker()  # экземпляр потока

        # Соединения
        self.mnist_worker.started.connect(self.mnist_on_started)  # начало работы mnist worker
        self.mnist_worker.finished.connect(self.mnist_on_finished)  # завершение работы mnist worker
        # сигнал mnist_worker'a о текущих действиях
        self.mnist_worker.signal_message.connect(self.mnist_on_change, QtCore.Qt.ConnectionType.QueuedConnection)
        self.mnist_worker.signal_model.connect(self.mnist_handler.set_model)
        self.mnist_handler.signal_mnist_handler.connect(self.toggle_use_model)
        # сигналы интерфейса
        self.draw28x28.signal_draw.connect(self.preview_show_draw)
        self.tempPB.clicked.connect(self.on_clicked)  # TODO: delete
        self.signal_info.connect(self.add_message_info)  # передача сообщения в лог

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)  # пусть будет итоговым компоновщиком

        self.info = QtWidgets.QTextEdit(self)  # лог отображения информации
        self.info.setReadOnly(True)

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
        self.slider_brush_size.setMaximum(15)
        self.slider_brush_size.setValue(5)
        self.slider_brush_size.valueChanged[int].connect(self.draw_change_brush_size)
        self.draw_brush_info = new_text(self, "5", alignment="c")
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
        # инструменты: очистить лог
        self.tb_clear_log = new_button(self, "tb", self.tr("Clear log"), "glyph_clear", the_color,
                                       lambda: self.info.clear(), tooltip=self.tr("Clear log"))
        # инструменты: обработать изображение с помощью модели
        self.tb_use_model = new_button(self, "tb", self.tr("Use model"), "glyph_data_graph", the_color,
                                       self.use_model, tooltip=self.tr("Use model for current image"))

        tools = [self.tb_use_model, self.tb_get_random, self.tb_clear_log, self.tb_start_train]
        self.tb_use_model.setEnabled(False)  # по умолчанию отключаем, т.к. никакой модели не загружено
        for tool in tools:
            panel_lay.addWidget(tool)
            tool.setIconSize(QtCore.QSize(config.UI_AZ_MNIST_ICON_PANEL, config.UI_AZ_MNIST_ICON_PANEL))
        panel_lay.addStretch(1)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.gb_draw)
        h_layout.addLayout(brush_size_lay)
        h_layout.addWidget(self.gb_preview)
        h_layout.addLayout(panel_lay)

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
            digit_lbl.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
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

        # настройки датасета
        self.platform_label = new_text(self.tr("Platform:"))
        self.cbx_platform = new_cbx(self, ["numpy", "tensorflow"])
        self.nn_type_label = new_text(self.tr("Neural network type:"))
        self.cbx_nn_type = new_cbx(self, ["perceptron", "CNN"])
        self.epochs_label = new_text(self.tr("Epoch:"))
        self.cbx_epochs = new_cbx(self, ["1", "2", "3", "4", "5", "10", "20"], True, QtGui.QIntValidator(1, 30))
        self.activ_func_label = new_text(self.tr("Activation function:"))
        self.cbx_activ_func = new_cbx(self, ["sigmoid", "ReLU", "linear", "binary step", "leaky ReLU",
                                             "exponential linear unit", "Tanh"])
        self.number_of_layers_label = new_text(self.tr("Layers number:"))
        self.cbx_number_of_layers = new_cbx(self, ["1", "2", "3", "4", "5", "10"], True, QtGui.QIntValidator(1, 30))
        self.using_dataset_label = new_text(self.tr("MNIST usage, %:"))
        self.cbx_using_dataset = new_cbx(self, ["1", "5", "10", "15", "20", "25", "50", "75", "100"], True,
                                         QtGui.QIntValidator(1, 100))
        self.chk_use_random_data = QtWidgets.QCheckBox(self.tr("Shuffle data from MNIST"))
        self.learning_rate_label = new_text(self, self.tr("Learning rate"))
        self.cbx_learning_rate = new_cbx(self, ["0.01", "0.005", "0.001", "0.1", "0.5"], True,
                                         QtGui.QDoubleValidator(0.0001, 1.0, 4))

        self.settings_labels = [self.platform_label, self.nn_type_label, self.epochs_label, self.activ_func_label,
                                self.number_of_layers_label, self.using_dataset_label, self.learning_rate_label]
        self.settings_widgets = [self.cbx_platform, self.cbx_nn_type, self.cbx_epochs, self.cbx_activ_func,
                                 self.cbx_number_of_layers, self.cbx_using_dataset, self.cbx_learning_rate]
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(10)  # настраиваем расстояние между элементами ui "исходных параметров"
        # заполняем парами
        for i, (label, widget) in enumerate(zip(self.settings_labels, self.settings_widgets)):
            grid_layout.addWidget(label, 0, i)
            grid_layout.addWidget(widget, 1, i)
        grid_layout.addWidget(self.chk_use_random_data, 2, 0, 1, 2)

        self.tempPB = QtWidgets.QPushButton("Temp")

        self.gb_settings = QtWidgets.QGroupBox(self.tr("Input settings"))
        self.gb_settings.setLayout(grid_layout)

        # Handler текущей модели MNIST
        self.mnist_handler = MNISTHandler(self)
        lay_handler = QtWidgets.QVBoxLayout()
        # lay_handler.setContentsMargins(0,0,0,0)
        # lay_handler.setSpacing(0)
        lay_handler.addWidget(self.mnist_handler)
        self.gb_model = QtWidgets.QGroupBox(self.tr("Model"))
        self.gb_model.setLayout(lay_handler)
        from ui import set_margins_recursive
        set_margins_recursive(self.gb_model, 0, 0, 0, 0, 0)

        # Итоговая сборка
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addLayout(h_layout)  # компонуем рисовальщика, предпросмотр
        v_layout.addLayout(h_layout2)  # и результат расчёта
        v_layout.addStretch(1)
        h_layout3 = QtWidgets.QHBoxLayout()
        h_layout3.addLayout(v_layout)
        h_layout3.addWidget(self.gb_model)
        h_layout3.addWidget(self.info, 1)  # делаем вывод максимальным
        layout.addWidget(self.gb_settings)
        layout.addLayout(h_layout3)
        layout.addWidget(self.tempPB)
        layout.addStretch(1)

    def get_random_image(self):
        img = load_image_from_dataset(self.settings.read_dataset_mnist())  # извлекаем случайное изображение из датасета
        self.current_img = np.reshape(img.astype("float32") / 255, (-1, 1))
        img = 255 - img  # инвертируем
        # конвертация массива numpy -> QImage
        q_img = QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_Grayscale8)

        # создаем объект QPixmap
        pixmap = QtGui.QPixmap.fromImage(q_img)
        self.preview_show_mnist(pixmap)  # отправляем на отрисовку

    def set_digits(self, result):
        """Установка значений цифры и её вероятности"""
        for i, dig in enumerate(self.digits):
            self.digits[i].set_value(result[i*100])
            self.digits_chance[i].setText(f"{round(result[i],0)}%")

    def clear_digits(self):
        """Очистка значений цифр и их вероятностей"""
        for i, dig in enumerate(self.digits):
            self.digits[i].set_value(0)
            self.digits_chance[i].setText("-")

    @QtCore.pyqtSlot()
    def on_clicked(self):
        for i, dig in enumerate(self.digits):
            self.digits[i].set_value(100)
            self.digits_chance[i].setText("99%")
        pass

    def use_model(self):
        """Обработать изображение с помощью текущей модели и установить значения в виджетах"""
        self.set_digits(self.mnist_handler.use_model(self.current_img))
        

    def show_data(self):  # TODO: del
        with np.load(self.settings.read_dataset_mnist()) as file:
            # x_train: яркость 1 для ячейки, где есть контур цифры, а 0 для пустого значения
            x_train = file['x_train']
            tra = x_train[0]
            y_train = file['y_train']
        plt.figure(figsize=(10, 5))
        for i in range(4):
            plt.subplot(1, 4, i + 1)
            plt.imshow(x_train[i], cmap='gray')
            plt.title(f"Label: {y_train[i]}")
            plt.axis('off')
        plt.tight_layout()
        plt.show()

    @QtCore.pyqtSlot(str)
    def toggle_use_model(self, msg):
        if msg == "model_is_set":
            self.tb_use_model.setEnabled(True)
        else:
            self.tb_use_model.setEnabled(False)

    def start_training(self):
        """Запуск на обучение НС"""
        settings = {"nn_type": self.cbx_nn_type.currentText(),
                    "platform": self.cbx_platform.currentText(),
                    "accuracy": "-",
                    "loss": "-",
                    "activ_funct": self.cbx_activ_func.currentText(),
                    "dataset_using": self.cbx_using_dataset.currentText(),
                    "epochs": self.cbx_epochs.currentText(),
                    "number_of_layers": self.cbx_number_of_layers.currentText(),
                    "shuffle_data": self.chk_use_random_data.isChecked(),
                    "learning_rate": self.cbx_learning_rate.currentText(),
                    }
        self.store_settings()  # запоминаем выбранные настройки
        self.add_message_info("\n", False)
        if self.cbx_nn_type.currentText() == "perceptron":  # тип НС "персептрон"
            self.tb_start_train.setDisabled(True)  # Делаем кнопку неактивной
            self.mnist_worker.init_data(**settings)  # инициализируем настройки
            self.mnist_worker.start()  # Запускаем поток
        elif self.cbx_nn_type == "CNN":  # тип "сверточная" НС
            self.signal_message.emit(self.tr("Not ready yet..."))
            return

    @QtCore.pyqtSlot()
    def mnist_on_started(self):  # Вызывается при запуске потока
        self.signal_info.emit(self.tr("---------- Training start ----------"))

    @QtCore.pyqtSlot()
    def mnist_on_finished(self):  # Вызывается при завершении потока
        self.signal_info.emit(self.tr("----- Model training complete -----"))
        self.tb_start_train.setDisabled(False)  # Делаем кнопку активной

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

    def update_font_color(self):
        if self.palette().color(QtGui.QPalette.Window).lightness() > 128:
            pass
            # print("light")
        else:
            pass
            # print("dark")

    @QtCore.pyqtSlot(int)
    def draw_change_brush_size(self, val):  # изменение размера кисти
        self.draw_brush_info.setText(str(val))
        self.draw28x28.set_pen_size(val)

    def draw_toggle_grid(self):
        """Установка параметра включение/отключение сетки при рисовании"""
        self.preview_show_grid = self.tb_toggle_grid.isChecked()

    @staticmethod
    def print_grid(pixmap):
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

    def convert_pixmap_to_numpy(self, pixmap):
        image = pixmap.toImage()
        width = image.width()
        height = image.height()

        # создаём пустой массив
        array = np.empty((height, width), dtype=np.float32)

        # заполняем пустой массив значениями
        for y in range(height):
            for x in range(width):
                # хотя нас ведь серый, поэтому можно использовать любой цвет, через QColor
                gray_value = QtGui.qGray(image.pixel(x, y))
                array[y, x] = (255 - gray_value) / 255  # инвертируем значения и переводим UnitRGB

        # x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1] * x_train.shape[2]))

        array = np.reshape(array, (-1, 1))
        return None

    def preview_show_draw(self, pixmap):  # пикселизация нарисованного объекта
        the28x28 = pixmap.scaled(28, 28, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                 QtCore.Qt.TransformationMode.SmoothTransformation)  # сжимаем...
        pixelated = the28x28.scaled(28 * 5, 28 * 5, QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                                    QtCore.Qt.TransformationMode.FastTransformation)  # ...и разжимаем
        # записываем изображение в память
        to_mass = pixelated.scaled(28, 28, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                            QtCore.Qt.TransformationMode.FastTransformation)
        self.current_img = self.convert_pixmap_to_numpy(to_mass)

        if self.preview_show_grid:  # определяем необходимость отрисовки сетки
            pixelated = self.print_grid(pixelated)
        self.preview.setPixmap(pixelated)
        self.gb_preview.setTitle(self.tr("Preview: drawing"))
        self.update()

    def preview_show_mnist(self, pixmap):  # отрисовка объекта из датасета MNIST
        mnist_img = pixmap.scaled(28 * 5, 28 * 5, QtCore.Qt.IgnoreAspectRatio,
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

    def store_settings(self):
        """Сохранение настроек"""
        self.settings.write_mnist_epochs(self.cbx_epochs.currentText())
        self.settings.write_mnist_dataset_using(self.cbx_using_dataset.currentText())
        self.settings.write_mnist_learning_rate(self.cbx_learning_rate.currentText())
        self.settings.write_mnist_shuffle_dataset(self.chk_use_random_data.isChecked())
        self.settings.write_mnist_activ_func(self.cbx_activ_func.currentText())

    def tr(self, text):
        return QtCore.QCoreApplication.translate("PageMNIST", text)

    def translate_ui(self):
        self.platform_label.setText(self.tr("Platform:"))
        self.epochs_label.setText(self.tr("Epoch:"))
        self.activ_func_label.setText(self.tr("Activation function:"))
        self.number_of_layers_label.setText(self.tr("Layers number:"))
        self.using_dataset_label.setText(self.tr("Dataset usage, %:"))
        self.gb_settings.setTitle(self.tr("Input settings"))
        self.gb_draw.setTitle(self.tr('Draw'))
        self.gb_preview.setTitle(self.tr('Preview'))


# ----------------------------------------------------------------------------------------------------------------------
class AzCanvas(QtWidgets.QLabel):
    """
    Холст рисования цифр, для распознавания при работе MNIST
    """
    signal_draw = QtCore.pyqtSignal(QtGui.QPixmap)  # сигнал завершения отрисовки

    def __init__(self):
        super().__init__()
        pixmap = QtGui.QPixmap(140, 140)  # кратно 28 в пять раз
        self.clear(pixmap)
        self.setPixmap(pixmap)
        self.draw = False  # рисование
        self.last_x, self.last_y = None, None  # координаты точки рисования
        self.pen_color = QtCore.Qt.GlobalColor.black
        self.pen_size = 5

    def set_pen_size(self, size):
        """Смена толщины кисти для рисования"""
        if size > 15:
            size = 15
        elif size < 1:
            size = 1
        self.pen_size = size

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:  # Ставим добро на рисование
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
        if event.button() == QtCore.Qt.RightButton:  # Очищаем
            self.clear(self.pixmap())
        self.draw = False
        self.last_x = None
        self.last_y = None
        self.signal_draw.emit(self.pixmap())  # отправляем сигнал-картинку

    def clear(self, pixmap):  # очистка холста = по сути заливка всего белым цветом
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
        painter.setPen(QtGui.QPen(self._bg_circle_color, self._thickness - 1, QtCore.Qt.SolidLine))
        if self._fill_bg_circle:
            painter.setBrush(QtGui.QBrush(self._bg_circle_color, QtCore.Qt.SolidPattern))
        elif not self._fill_bg_circle:
            painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(self._thickness, self._thickness, self._circular_size, self._circular_size)
        if self._round_edge:
            painter.setPen(QtGui.QPen(self._color, self._thickness, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        elif not self._round_edge:
            painter.setPen(QtGui.QPen(self._color, self._thickness, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawArc(self._thickness, self._thickness, self._circular_size, self._circular_size, self._a * 16,
                        self._alen * 16)

        # az_realization
        digit_str = str(self._digit)
        font = QtGui.QFont('Tahoma', self._digit_size)  # Lucida Console,
        metrics = QtGui.QFontMetrics(font)
        x = (self.width() - metrics.width(digit_str)) // 2
        y = (self.height() - metrics.height()) // 2 + metrics.ascent()
        painter.setFont(font)
        painter.setPen(self._base_color)
        painter.drawText(x, y, digit_str)
        # painter.drawText(self.rect(), QtCore.Qt.AlignCenter, str(self._digit))

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._circular_size = (self.width() - (self._thickness * 2)) if self.width() < self.height() else (
                self.height() - (self._thickness * 2))

    def get_value(self):
        return self._value

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
        self.model_params = None  # параметры модели
        self.model_data = None  # данные модели

        self.label_status = new_text(self.tr("Model not loaded"))
        self.btn_status = new_button(self, "tb", icon="circle_grey", color=None, icon_size=16,
                                     tooltip=self.tr("Model status"))
        self.table_params = QtWidgets.QTableView()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.btn_status)
        hlayout.addWidget(self.label_status)
        finish_lay = QtWidgets.QVBoxLayout(self)
        finish_lay.addLayout(hlayout)
        finish_lay.addWidget(self.table_params)

    @QtCore.pyqtSlot(tuple)
    def set_model(self, data):
        """Установка новой модели, данные приходят в виде кортежа: ({словаря параметров} и {словаря данных модели}).
        Данные модели это {"data":(bias_layer1, weights_layer1, activ_func1), (bias_layer2, ...), ... }"""
        self.model_params, self.model_data = data
        self.set_table_data()  # настраиваем отображение параметров модели в таблице
        # self.model = {"bias":bias_list, weights_list, activ_list}
        # TODO: какая-то проверка модели, если всё ок то
        now = datetime.now().strftime("%H:%M:%S")
        self.change_status(self.tr(f"Model was set at {now}"), "green", "model_is_set")

    def use_model(self, image_data):
        """Использование обученной модели для определения данных. Входные данные image_data - изображение переведенное
        в формат numpy, в значениях пикселей от 0 до 1: [784, 1]"""
        image = image_data
        [bias_list, weights_list, activ_funcs_list] = zip(*self.model_data["data"])  # распаковываем данные нейросети
        current_layer = image
        for bias, weights, activ_func in zip(bias_list, weights_list, activ_funcs_list):
            layer = bias + weights @ current_layer
            result = get_activ_func(activ_func, layer)
            current_layer = result
        return current_layer
        # image = np.reshape(test_image, (-1, 1))
        #
        # # Forward propagation (to hidden layer)
        # hidden_raw = bias_layer_1 + weights_layer_1 @ image
        # hidden = 1 / (1 + np.exp(-hidden_raw))  # sigmoid
        # # Forward propagation (to output layer)
        # output_raw = bias_layer_2 + weights_layer_2 @ hidden
        # output = 1 / (1 + np.exp(-output_raw))

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
        self.label_status.setText(message)
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


# ----------------------------------------------------------------------------------------------------------------------
class MNISTWorker(QtCore.QThread):
    """Поток обучения, загрузка данных персептрона MNIST"""
    signal_message = QtCore.pyqtSignal(str)  # передача сообщения
    signal_model = QtCore.pyqtSignal(tuple)  # сигнал передачи модели

    def __init__(self, parent=None):
        super(MNISTWorker, self).__init__()
        # QtCore.QThread.__init__(self, parent)
        self.settings = AppSettings()

    def init_data(self, **params):
        # инициализация начальных параметров через словарь
        self.params = params

    def run(self):
        images, labels = load_dataset(self.settings.read_dataset_mnist(), self.params["dataset_using"],
                                      self.params["shuffle_data"])
        if images is None:
            self.signal_message.emit(self.tr("MNIST file not found, check for source data."))
            return
        self.signal_message.emit(self.tr(f"Loaded {len(labels)} images from MNIST"))
        # слои следуют: 1 (исходный), 2 (скрытый), 3 (скрытый), ..., выходной слой
        # инициализируем случайные веса второго слоя, 20 строк х 28*28 (784) столбцов
        weights_layer_1 = np.random.uniform(-0.5, 0.5, (20, 784))
        weights_layer_2 = np.random.uniform(-0.5, 0.5, (10, 20))  # веса третьего (выходного) слоя
        bias_layer_1 = np.zeros((20, 1))  # смещение для второго слоя, инициализируем 20 строк х 1 столбец нулей
        bias_layer_2 = np.zeros((10, 1))  # смещения для третьего (выходного) слоя
        # определяем используемую функцию активации
        activ_func = self.params["activ_funct"]

        epochs = int(self.params["epochs"])
        e_loss = 0
        e_correct = 0  # коррекция ошибки
        learning_rate = float(self.params["learning_rate"])  # скорость обучения

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
                loss = round((e_loss[0] / images.shape[0]) * 100, 2)
                acc = round((e_correct / images.shape[0]) * 100, 2)
                self.params["loss"] = str(loss) + "%"
                self.params["accuracy"] = str(acc) + "%"
            # DONE

            self.signal_message.emit(self.tr(f"Epoch {epoch + 1}: loss {loss}%; accuracy: {acc}%"))

            e_loss = 0
            e_correct = 0

        # Подготавливаем данные для отправки
        # структура данных: ({словарь параметров}, {данные обученной модели})
        data = (self.params,
                {"data": [(bias_layer_1, weights_layer_1, activ_func), (bias_layer_2, weights_layer_2, activ_func)]})
        self.signal_model.emit(data)
        return
        # self.signal_message.emit(f"output: {output}")

        # TODO: use_not_in_set! цикл.
        test_image = random.choice(images)

        # CHECK CUSTOM
        # test_image = plt.imread("custom.jpg", format="jpeg")

        # Grayscale + Unit RGB + inverse colors
        # gray = lambda rgb: np.dot(rgb[..., :3], [0.299, 0.587, 0.114])
        # test_image = 1 - (gray(test_image).astype("float32") / 255)

        # Reshape custom
        # test_image = np.reshape(test_image, (test_image.shape[0] * test_image.shape[1]))
        # Predict
        image = np.reshape(test_image, (-1, 1))

        # Forward propagation (to hidden layer)
        hidden_raw = bias_layer_1 + weights_layer_1 @ image
        hidden = 1 / (1 + np.exp(-hidden_raw))  # sigmoid
        # Forward propagation (to output layer)
        output_raw = bias_layer_2 + weights_layer_2 @ hidden
        output = 1 / (1 + np.exp(-output_raw))

        print(output.argmax())
        # plt.imshow(test_image.reshape(28, 28), cmap="Greys")
        # plt.title(f"NN suggests the CUSTOM number is: {output.argmax()}")
        # plt.show()


# ----------------------------------------------------------------------------------------------------------------------
def load_image_from_dataset(path, shuffle=True):
    """
    Статическая функция, возвращает одно изображение MNIST
    Параметры: path - путь к файлу *.npz; shuffle - использование данных в случайном порядке;
    """
    if not helper.check_file(path):
        return None
    with np.load(path) as file:
        if shuffle:
            return random.choice(file['x_train'])
        else:
            return file['x_train'][0]

        # def get_random_element(array):
        #     random_index = np.random.choice(len(array))
        #     return array[random_index]
        #
        # def get_specific_element(array, index):
        #     return array[index]


# ----------------------------------------------------------------------------------------------------------------------
def load_dataset(path, using_percent=100, shuffle=False):
    """
    Статическая функция загрузки датасета MNIST, возвращает перечень изображений и значений для них:
    x_train - изображения в формате: яркость 255 для ячейки, где есть контур цифры; 0 для пустого значения
    y_train - соответствующая изображению цифра в формате int.
    Параметры: path - путь к файлу *.npz; using_percent - объем используемого датасета;
    shuffle - использование данных в случайном порядке
    """
    if not helper.check_file(path):
        return None, None

    with np.load(path) as file:
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

        # формируем итоговый набор данных изображений
        x_train = x_train[sel_inx]

        # выходные данные
        y_train = file['y_train']
        y_train = y_train[sel_inx]  # ограничиваем набор датасета при 100% = 60000
        # выходные 1-х матрицы в формате по 10 классов цифр [[0000001000][0100000000]...[0000000010]]]
        y_train = np.eye(10)[y_train]

        return x_train, y_train


# ----------------------------------------------------------------------------------------------------------------------


# def test():
#     import numpy as np
#     import matplotlib.pyplot as plt
#
#     import utils
#
#     images, labels = utils.load_dataset()
#
#     w_i_h = np.random.uniform(-0.5, 0.5, (20, 784))
#     w_h_o = np.random.uniform(-0.5, 0.5, (10, 20))
#     b_i_h = np.zeros((20, 1))
#     b_h_o = np.zeros((10, 1))
#
#     learn_rate = 0.01
#     nr_correct = 0
#     loss = 0
#     epochs = 3
#     for epoch in range(epochs):
#         for img, l in zip(images, labels):
#             img = np.reshape(img, (-1, 1))
#             l = np.reshape(l, (-1, 1))
#
#             # Forward propagation input -> hidden
#             h_pre = b_i_h + w_i_h @ img
#             h = 1 / (1 + np.exp(-h_pre))
#             # Forward propagation hidden -> output
#             o_pre = b_h_o + w_h_o @ h
#             o = 1 / (1 + np.exp(-o_pre))
#
#             # Cost / Error calculation
#             loss += 1 / len(o) * np.sum((o - l) ** 2, axis=0)
#             nr_correct += int(np.argmax(o) == np.argmax(l))
#
#             # Backpropagation output -> hidden (cost function derivative)
#             delta_o = o - l
#             w_h_o += -learn_rate * delta_o @ np.transpose(h)
#             b_h_o += -learn_rate * delta_o
#             # Backpropagation hidden -> input (activation function derivative)
#             delta_h = np.transpose(w_h_o) @ delta_o * (h * (1 - h))
#             w_i_h += -learn_rate * delta_h @ np.transpose(img)
#             b_i_h += -learn_rate * delta_h
#
#         # Show accuracy for this epoch
#         print(f"Loss: {round((loss[0] / images.shape[0]) * 100, 2)}%")
#         print(f"Acc: {round((nr_correct / images.shape[0]) * 100, 2)}%")
#         nr_correct = 0
#         loss = 0
#
#     exit(0)
#
#     # Show results
#     while True:
#         index = int(input("Enter a number (0 - 59999): "))
#         img = images[index]
#         plt.imshow(img.reshape(28, 28), cmap="Greys")
#
#         img.shape += (1,)
#         # Forward propagation input -> hidden
#         h_pre = b_i_h + w_i_h @ img.reshape(784, 1)
#         h = 1 / (1 + np.exp(-h_pre))
#         # Forward propagation hidden -> output
#         o_pre = b_h_o + w_h_o @ h
#         o = 1 / (1 + np.exp(-o_pre))
#
#         plt.title(f"Subscribe if its a {o.argmax()} :)")
#         plt.show()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = PageMNIST()
    w.show()
    app.exec()

# with np.load(self.settings.read_dataset_mnist()) as file:
#     img = file['x_train'][0]
# # конвертируем в формат numpy