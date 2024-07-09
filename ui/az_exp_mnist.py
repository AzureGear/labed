from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, helper
import matplotlib.pyplot as plt
import numpy as np


# TODO: сделать класс наследуемый от LCD цифр с кружочком вокруг них, который показывает процентное отношение распоз.
# Тип полностью закрытый кружок = 100%, на четверть = 25%.

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
    img1 = np.zeros((n,m))
    for x in range(0, n, window):
        for y in range(0, m, window):
            if img[x:x+window,y:y+window].mean() > threshold:
                img1[x:x+window,y:y+window] = 1
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


class PageMNIST(QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)
        self.name = "MNIST"
        self.settings = AppSettings()
        self.draw28x28 = AzCanvas()
        self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))

        self.preview = QtWidgets.QLabel()
        self.preview.setPixmap(QtGui.QPixmap(140, 140))
        self.preview.pixmap().fill(QtGui.QColor(QtCore.Qt.GlobalColor.white))
        self.preview.setPixmap(self.print_grid(self.preview.pixmap()))

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setSegmentStyle(QtWidgets.QLCDNumber.Filled)  # Устанавливаем стиль сегментов
        self.lcd.setDigitCount(8)  # Устанавливаем количество цифр
        self.lcd.setMode(QtWidgets.QLCDNumber.Dec)  # Устанавливаем режим (Dec, Hex, Bin или Oct)
        self.lcd.setSmallDecimalPoint(True)  # Устанавливаем размер десятичной точки
        self.lcd.display(123.45)  # Отображаем число

        self.tempPB = QtWidgets.QPushButton("Temp")
        self.tempPB.clicked.connect(self.run_neural_network)

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
        h_layout.addWidget(self.lcd)
        h_layout.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(h_layout)
        layout.addWidget(self.tempPB)
        layout.addStretch(1)

        # Соединения
        self.draw28x28.signal_draw.connect(self.preview_show)

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
        self.draw28x28.setToolTip(self.tr('Left click to draw, right click to clear'))
        self.gb_draw.setToolTip(self.tr('Left click to draw, right click to clear'))
        self.gb_draw.setTitle(self.tr('Draw'))
        self.gb_preview.setTitle(self.tr('Preview'))

    def run_neural_network(self):

        # import matplotlib.pyplot as plt
        images, labels = load_dataset(self.settings.read_dataset_mnist())

        weights_input_to_hidden = np.random.uniform(-0.5, 0.5, (20, 784))
        weights_hidden_to_output = np.random.uniform(-0.5, 0.5, (10, 20))
        bias_input_to_hidden = np.zeros((20, 1))
        bias_hidden_to_output = np.zeros((10, 1))

        epochs = 3
        e_loss = 0
        e_correct = 0
        learning_rate = 0.01

        for epoch in range(epochs):
            print(f"Epoch №{epoch}")

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


def load_dataset(path):
    """Загрузить датасет MNIST"""
    if not helper.check_file(path):
        QtWidgets.QMessageBox(None, "There is no MNIST :(")
        return None, None

    with np.load(path) as f:
        # convert from RGB to Unit RGB
        x_train = f['x_train'].astype("float32") / 255

        # reshape from (60000, 28, 28) into (60000, 784)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1] * x_train.shape[2]))

        # labels
        y_train = f['y_train']

        # convert to output layer format
        y_train = np.eye(10)[y_train]

        return x_train, y_train


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
