from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from ui import new_text, new_cbx
from utils import AppSettings, helper, config
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

the_color = config.UI_COLORS.get("experiments_color")


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
        self.setup_ui()  # настройка интерфейса
        self.setStyleSheet("QWidget { border: 1px solid yellow; }")  # проверка отображения виджетов
        self.update_font_color()  # изменение цвета шрифта в зависимости от темы

        # поток QThread
        self.mnist_worker = MNISTWorker()  # экземпляр потока

        self.mnist_worker.started.connect(self.mnist_on_started)  # начало работы
        self.mnist_worker.finished.connect(self.mnist_on_finished)  # завершение работы
        # сигнал mnist_worker'a о текущих действиях
        self.mnist_worker.signal_message.connect(self.mnist_on_change, QtCore.Qt.ConnectionType.QueuedConnection)

        # Соединения
        self.draw28x28.signal_draw.connect(self.preview_show)
        self.tempPB.clicked.connect(self.on_clicked)  # TODO: delete
        self.signal_info.connect(self.add_message_info)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)  # пусть будет итоговым компоновщиком

        self.draw28x28 = AzCanvas()  # холст для рисования
        self.draw28x28.setFixedSize(143, 143)
        self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))

        self.preview = QtWidgets.QLabel()  # холст для просмотра
        self.preview.setPixmap(QtGui.QPixmap(140, 140))
        self.preview.pixmap().fill(QtGui.QColor(QtCore.Qt.GlobalColor.white))
        self.preview.setPixmap(self.print_grid(self.preview.pixmap()))
        self.preview.setFixedSize(143, 143)

        self.info = QtWidgets.QTextEdit(self)  # виджет отображения данных
        self.info.setReadOnly(True)

        # Устанавливаем разметку для виджетов на вкладке
        self.gb_draw = QtWidgets.QGroupBox(self.tr("Draw"))
        self.gb_preview = QtWidgets.QGroupBox(self.tr("Preview"))
        for group, widget in ((self.gb_draw, self.draw28x28),
                              (self.gb_preview, self.preview)):
            group.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            v_lay = QtWidgets.QVBoxLayout()
            v_lay.addWidget(widget)
            group.setLayout(v_lay)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.gb_draw)
        h_layout.addWidget(self.gb_preview)

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

        self.tempPB = QtWidgets.QPushButton("Temp")

        # настройки датасета
        self.platform_label = new_text(self.tr("Platform:"))
        self.cbx_platform = new_cbx(self, ["numpy", "tensorflow"])
        self.epochs_label = new_text(self.tr("Epoch:"))
        self.cbx_epochs = new_cbx(self, ["1", "2", "3", "4", "5", "10", "20"], True, QtGui.QIntValidator(1, 30))
        self.activ_func_label = new_text(self.tr("Activation function:"))
        self.cbx_activ_func = new_cbx(self, ["ReLU"])
        self.number_of_layers_label = new_text(self.tr("Layers number:"))
        self.cbx_number_of_layers = new_cbx(self, ["1", "2", "3", "4", "5", "10"], True, QtGui.QIntValidator(1, 30))
        self.using_dataset_label = new_text(self.tr("MNIST usage, %:"))
        self.cbx_using_dataset = new_cbx(self, ["5", "10", "15", "20", "25", "30", "35", "50", "75", "100"], True,
                                         QtGui.QIntValidator(1, 100))
        self.settings_labels = [self.platform_label, self.epochs_label, self.activ_func_label,
                                self.number_of_layers_label, self.using_dataset_label]
        self.settings_widgets = [self.cbx_platform, self.cbx_epochs, self.cbx_activ_func, self.cbx_number_of_layers,
                                 self.cbx_using_dataset]
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(10) # настраиваем расстояние между элементами ui "исходных параметров"
        # заполняем парами
        for i, (label, widget) in enumerate(zip(self.settings_labels, self.settings_widgets)):
            grid_layout.addWidget(label, 0, i)
            grid_layout.addWidget(widget, 1, i)

        self.gb_settings = QtWidgets.QGroupBox(self.tr("Input settings"))

        self.gb_settings.setLayout(grid_layout)

        # Итоговая сборка
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addLayout(h_layout)  # компонуем рисовальщика, предпросмотр
        v_layout.addLayout(h_layout2)  # и результат расчёта
        h_layout3 = QtWidgets.QHBoxLayout()
        h_layout3.addLayout(v_layout)
        h_layout3.addWidget(self.info, 1)  # делаем вывод максимальным
        layout.addWidget(self.gb_settings)
        layout.addLayout(h_layout3)
        layout.addWidget(self.tempPB)
        layout.addStretch(1)

    @QtCore.pyqtSlot()
    def on_clicked(self):
        self.tempPB.setDisabled(True)  # Делаем кнопку неактивной
        settings = {'platform': self.cbx_platform.currentText(),
                    'activ_funct': self.cbx_activ_func.currentText(),
                    'dataset_using': self.cbx_using_dataset.currentText(),
                    'epochs': self.cbx_epochs.currentText(),
                    'cbx_number_of_layers': self.cbx_number_of_layers.currentText()
                    }
        self.mnist_worker.init_data(**settings)  # инициализируем настройки
        self.mnist_worker.start()  # Запускаем поток

    @QtCore.pyqtSlot()
    def mnist_on_started(self):  # Вызывается при запуске потока
        self.signal_info.emit("Вызван метод on_started ()")

    @QtCore.pyqtSlot()
    def mnist_on_finished(self):  # Вызывается при завершении потока
        self.signal_info.emit("Вызван метод on_finished()")
        self.tempPB.setDisabled(False)  # Делаем кнопку активной

    @QtCore.pyqtSlot(str)
    def mnist_on_change(self, s):
        self.signal_info.emit(s)

    @QtCore.pyqtSlot(str)
    def add_message_info(self, message):  # передача информации в лог
        current_time = datetime.now().time().strftime("%H:%M:%S")
        message = current_time + ": " + message
        self.info.setPlainText(message + "\n" + self.info.toPlainText())

    def update_font_color(self):
        if self.palette().color(QtGui.QPalette.Window).lightness() > 128:
            pass
            # print("light")
        else:
            pass
            # print("dark")

    def preview_show(self, pixmap):  # пикселизация нарисованного объекта
        the28x28 = pixmap.scaled(28, 28, QtCore.Qt.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        pixelated = the28x28.scaled(28 * 5, 28 * 5, QtCore.Qt.IgnoreAspectRatio,
                                    QtCore.Qt.TransformationMode.FastTransformation)
        pixelated = self.print_grid(pixelated)
        self.preview.setPixmap(pixelated)
        self.update()

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
            pen.setWidth(5)
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


class MNISTWorker(QtCore.QThread):
    """Поток обучения, загрузка данных персептрона MNIST"""
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MNISTWorker, self).__init__()
        # QtCore.QThread.__init__(self, parent)
        self.settings = AppSettings()

    def init_data(self, **settings):
        # инициализация начальных параметров через словарь
        self.params = settings

    def run(self):
        self.signal_message.emit(self.tr("Приступаю к загрузке данных"))
        images, labels = self.load_dataset(self.settings.read_dataset_mnist())
        if images is None:
            self.signal_message.emit(self.tr("MNIST file not found, check for source data."))
            return
        # слои следуют: 1 (исходный), 2 (скрытый), 3 (скрытый), ..., выходной слой
        # инициализируем случайные веса второго слоя, 20 строк х 28*28 (784) столбцов
        weights_layer_2 = np.random.uniform(-0.5, 0.5, (20, 784))
        weights_layer_3 = np.random.uniform(-0.5, 0.5, (10, 20))  # веса третьего (выходного) слоя
        bias_layer_2 = np.zeros((20, 1))  # смещение для второго слоя, инициализируем 20 строк х 1 столбец нулей
        bias_layer_3 = np.zeros((10, 1))  # смещения для третьего (выходного) слоя

        epochs = int(self.params["epochs"])
        e_loss = 0
        e_correct = 0  # коррекция ошибки
        learning_rate = 0.01  # скорость обучения

        for epoch in range(epochs):
            self.signal_message.emit(f"Epoch #{epoch}")

            for image, label in zip(images, labels):
                image = np.reshape(image, (-1, 1))  # преобразование массивов исходных данных в [784, 1]
                label = np.reshape(label, (-1, 1))  # [10, 1]

                # 1. Прямое распространение (к скрытому слою)
                # смещение + веса * данные изображения
                # мы перемножаем [20x784] на [784x1] и получаем [20x1]
                hidden_raw = bias_layer_2 + weights_layer_2 @ image  # [20, 1]
                hidden = 1 / (1 + np.exp(-hidden_raw))  # функция активации: сигмоидная [20, 1]

                # прямое распространение (к выходному слою)
                # мы перемножаем [10, 20] на [20, 1] и получаем [10, 1]
                output_raw = bias_layer_3 + weights_layer_3 @ hidden  # [10, 1]
                output = 1 / (1 + np.exp(-output_raw))  # [10, 1]

                # 2. Расчет потерь/ошибок, используем MSE (СКО)
                e_loss += 1 / len(output) * np.sum((output - label) ** 2, axis=0)
                e_correct += int(np.argmax(output) == np.argmax(label))

                # 3. Обратное распространение ошибки (выходной уровень).
                # delta = [10, 1] - [10, 1]
                delta_output = output - label  # дельта = разница между результатом и контрольным значением
                # изменяем веса выходного слоя [10, 20]
                weights_layer_3 += -learning_rate * delta_output @ np.transpose(hidden)
                # изменяем смещения выходного слоя [10, 1]
                bias_layer_3 += -learning_rate * delta_output

                # Обратное распространение ошибки (скрытый слой)
                delta_hidden = np.transpose(weights_layer_3) @ delta_output * (hidden * (1 - hidden))
                weights_layer_2 += -learning_rate * delta_hidden @ np.transpose(image)
                bias_layer_2 += -learning_rate * delta_hidden

            # DONE

            # print some debug info between epochs
            self.signal_message.emit(f"Loss: {round((e_loss[0] / images.shape[0]) * 100, 3)}%")
            self.signal_message.emit(f"Accuracy: {round((e_correct / images.shape[0]) * 100, 3)}%")
            e_loss = 0
            e_correct = 0

        # self.signal_message.emit(f"output: {output}")
        return
        # CHECK CUSTOM
        test_image = plt.imread("custom.jpg", format="jpeg")

        # Grayscale + Unit RGB + inverse colors
        gray = lambda rgb: np.dot(rgb[..., :3], [0.299, 0.587, 0.114])
        test_image = 1 - (gray(test_image).astype("float32") / 255)

        # Reshape
        test_image = np.reshape(test_image, (test_image.shape[0] * test_image.shape[1]))

        # Predict
        image = np.reshape(test_image, (-1, 1))

        # Forward propagation (to hidden layer)
        hidden_raw = bias_layer_2 + weights_layer_2 @ image
        hidden = 1 / (1 + np.exp(-hidden_raw))  # sigmoid
        # Forward propagation (to output layer)
        output_raw = bias_layer_3 + weights_layer_3 @ hidden
        output = 1 / (1 + np.exp(-output_raw))

        # plt.imshow(test_image.reshape(28, 28), cmap="Greys")
        # plt.title(f"NN suggests the CUSTOM number is: {output.argmax()}")
        # plt.show()

    def load_dataset(self, path):
        """
        Загрузить датасет MNIST.
        x_train - изображения в формате grayscale
        y_train - соответствующая изображению цифра
        """
        if not helper.check_file(path):
            return None, None

        with np.load(path) as file:
            x_train = file['x_train'].astype("float32") / 255  # конвертация из RGB в Unit RGB
            # преобразование массива из (60000, 28, 28) в формат (60000, 784)
            x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1] * x_train.shape[2]))

            using_percent = int(self.params["dataset_using"])  # считываем ограничение датасета
            num_rows = int(x_train.shape[0] * using_percent / 100)
            # набираем случайных индексов
            sel_inx = np.random.choice(x_train.shape[0], num_rows, replace=False)  # следим, чтобы не было повторов
            # формируем итоговый набор данных изображений
            x_train = x_train[sel_inx]

            # выходные данные
            y_train = file['y_train']
            y_train = y_train[sel_inx]  # ограничиваем набор датасета при 100% = 60000
            # выходные 1-х матрицы в формате по 10 классов цифр [[0000001000][0100000000]...[0000000010]]]
            y_train = np.eye(10)[y_train]

            # plt.figure(figsize=(10, 5))
            # for i in range(4):
            #     plt.subplot(1, 4, i + 1)
            #     plt.imshow(selected_rows[i], cmap='gray')
            #     plt.title(f"Label: {y_train[i]}")
            #     plt.axis('off')
            # plt.tight_layout()
            # plt.show()

            return x_train, y_train


def pixelate_rgb(img, window):
    """Пикселизация изображения"""
    n, m, _ = img.shape
    n, m = n - n % window, m - m % window
    img1 = np.zeros((n, m, 3))
    for x in range(0, n, window):
        for y in range(0, m, window):
            img1[x:x + window, y:y + window] = img[x:x + window, y:y + window].mean(axis=(0, 1))
    return img1


def pixelate_bin(img, window, threshold):
    n, m = img.shape
    n, m = n - n % window, m - m % window
    img1 = np.zeros((n, m))
    for x in range(0, n, window):
        for y in range(0, m, window):
            if img[x:x + window, y:y + window].mean() > threshold:
                img1[x:x + window, y:y + window] = 1
    return img1


def convert_to_grey():
    # convert image to grayscale
    img = np.dot(plt.imread('test.png'), [0.299, 0.587, 0.114])

    fig, ax = plt.subplots(1, 3, figsize=(15, 10))

    plt.tight_layout()
    ax[0].imshow(pixelate_bin(img, 5, .2), cmap='gray')
    ax[1].imshow(pixelate_bin(img, 5, .3), cmap='gray')
    ax[2].imshow(pixelate_bin(img, 5, .45), cmap='gray')

    # remove frames
    [a.set_axis_off() for a in ax.flatten()]
    plt.subplots_adjust(wspace=0.03, hspace=0)


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
