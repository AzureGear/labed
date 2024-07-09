from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from utils import AppSettings, helper, config
import matplotlib.pyplot as plt
import numpy as np

the_color = config.UI_COLORS.get("experiments_color")


# TODO: сделать класс наследуемый от LCD цифр с кружочком вокруг них, который показывает процентное отношение распоз.
# Тип полностью закрытый кружок = 100%, на четверть = 25%.

class PageMNIST(QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)
        self.name = "MNIST"
        self.settings = AppSettings()
        layout = QtWidgets.QVBoxLayout(self)  # пусть будет итоговым компоновщиком

        self.draw28x28 = AzCanvas()  # холст для рисования
        self.draw28x28.setFixedSize(143, 143)
        self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))

        self.preview = QtWidgets.QLabel()  # холст для просмотра
        self.preview.setPixmap(QtGui.QPixmap(140, 140))
        self.preview.pixmap().fill(QtGui.QColor(QtCore.Qt.GlobalColor.white))
        self.preview.setPixmap(self.print_grid(self.preview.pixmap()))
        self.preview.setFixedSize(143, 143)

        # Устанавливаем разметку для виджетов на вкладке
        self.gb_draw = QtWidgets.QGroupBox("Draw")
        self.gb_preview = QtWidgets.QGroupBox("Preview")
        for group, widget in ((self.gb_draw, self.draw28x28),
                              (self.gb_preview, self.preview)):
            group.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            v_lay = QtWidgets.QVBoxLayout()
            v_lay.addWidget(widget)
            group.setLayout(v_lay)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.gb_draw)
        h_layout.addWidget(self.gb_preview)
        h_layout.addStretch(1)

        # настройка цифр
        h_layout2 = QtWidgets.QHBoxLayout()  # компоновщик для "Цифр" и их вероятностей
        self.digits = {}  # словарь цифр, например 6: RoundProgressbar
        self.digits_chance = {}  # словарь вероятностей распознавания, например 6: QLabel.text
        for i in range(10):  # автоматом делаем все 10 цифр
            digit_v = QtWidgets.QVBoxLayout(self)
            digit_v.setSpacing(0)
            digit_v.setContentsMargins(2, 0, 2, 0)
            digit_lbl = QtWidgets.QLabel(f"{(i * 10 + 10):.0f}%")
            digit_lbl.setFixedHeight(14)
            digit_lbl.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
            digit_lbl.setIndent(0)

            the_digit = RoundProgressbar(self, QtGui.QColor(the_color), thickness=2, value=10 * i + 10,
                                         maximum=100, digit=i, digit_size=12)
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


        grid_layout = QtWidgets.QGridLayout()
        self.platform_label = QtWidgets.QLabel(self.tr("Platform"))

        self.epoch_label = QtWidgets.QLabel(self.tr("Platform"))

        self.activ_func_label = QtWidgets.QLabel(self.tr("Platform"))

        self.number_of_layers_label = QtWidgets.QLabel(self.tr("Platform"))

        self.using_dataset_label = QtWidgets.QLabel(self.tr("Platform"))


        # Итоговая сборка
        layout.addLayout(h_layout)
        layout.addWidget(self.tempPB)
        layout.addLayout(h_layout2)
        layout.addStretch(1)

        # Изменение цвета шрифта в зависимости от темы
        self.update_font_color()
        # Соединения
        self.draw28x28.signal_draw.connect(self.preview_show)
        self.tempPB.clicked.connect(self.run_neural_network)  # TODO: delete

    def update_font_color(self):
        if self.palette().color(QtGui.QPalette.Window).lightness() > 128:
            print("light")
        else:
            print("dark")

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
        pass
        # self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))
        # self.gb_draw.setToolTip(self.tr('Left click to draw, right click to clear'))
        # self.gb_draw.setTitle(self.tr('Draw'))
        # self.gb_preview.setTitle(self.tr('Preview'))

    def run_neural_network(self):

        # import matplotlib.pyplot as plt
        images, labels = load_dataset(self.settings.read_dataset_mnist())
        if images is None:
            self.signal_message.emit(self.tr("MNIST file not found, check for source data."))
            return
        weights_input_to_hidden = np.random.uniform(-0.5, 0.5, (20, 784))
        weights_hidden_to_output = np.random.uniform(-0.5, 0.5, (10, 20))
        bias_input_to_hidden = np.zeros((20, 1))
        bias_hidden_to_output = np.zeros((10, 1))

        epochs = 3
        e_loss = 0
        e_correct = 0
        learning_rate = 0.01

        for epoch in range(epochs):
            print(f"Epoch #{epoch}")

            for image, label in zip(images, labels):
                image = np.reshape(image, (-1, 1))
                label = np.reshape(label, (-1, 1))

                # Forward propagation (to hidden layer)
                hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ image
                hidden = 1 / (1 + np.exp(-hidden_raw))  # sigmoid

                # Forward propagation (to output layer)
                output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
                output = 1 / (1 + np.exp(-output_raw))

                # Loss / Error calculation
                e_loss += 1 / len(output) * np.sum((output - label) ** 2, axis=0)
                e_correct += int(np.argmax(output) == np.argmax(label))

                # Backpropagation (output layer)
                delta_output = output - label
                weights_hidden_to_output += -learning_rate * delta_output @ np.transpose(hidden)
                bias_hidden_to_output += -learning_rate * delta_output

                # Backpropagation (hidden layer)
                delta_hidden = np.transpose(weights_hidden_to_output) @ delta_output * (hidden * (1 - hidden))
                weights_input_to_hidden += -learning_rate * delta_hidden @ np.transpose(image)
                bias_input_to_hidden += -learning_rate * delta_hidden

            # DONE

            # print some debug info between epochs
            print(f"Loss: {round((e_loss[0] / images.shape[0]) * 100, 3)}%")
            print(f"Accuracy: {round((e_correct / images.shape[0]) * 100, 3)}%")
            e_loss = 0
            e_correct = 0

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
        hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ image
        hidden = 1 / (1 + np.exp(-hidden_raw))  # sigmoid
        # Forward propagation (to output layer)
        output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
        output = 1 / (1 + np.exp(-output_raw))

        # plt.imshow(test_image.reshape(28, 28), cmap="Greys")
        # plt.title(f"NN suggests the CUSTOM number is: {output.argmax()}")
        # plt.show()


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

    def __init__(self, project_data, export_dir, format='yolo_seg', export_map=None, dataset_name='dataset',
                 variant_idx=0, splits=None, split_method='names', sim=0,
                 is_filter_null=False, new_image_size=None):
        """
        variant_idx = 0 Train/Val/Test
        1 - Train/Val
        2 - Only Train
        3 - Only Val
        4 - Only Test
        """



def load_dataset(path):
    """Загрузить датасет MNIST"""
    if not helper.check_file(path):
        return None, None

    with np.load(path) as file:
        # конвертация из RGB в Unit RGB
        x_train = file['x_train'].astype("float32") / 255

        # преобразование массива из (60000, 28, 28) в формат (60000, 784)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1] * x_train.shape[2]))

        # выходные данные
        y_train = file['y_train']

        # 60000 выходных 1-х матриц в формате по 10 классов цифр [[0000001000][0100000000]...[0000000010]]]
        y_train = np.eye(10)[y_train]

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
