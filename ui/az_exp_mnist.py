from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np


def pixelate_rgb(img, window):
    n, m, _ = img.shape
    n, m = n - n % window, m - m % window
    img1 = np.zeros((n, m, 3))
    for x in range(0, n, window):
        for y in range(0, m, window):
            img1[x:x + window, y:y + window] = img[x:x + window, y:y + window].mean(axis=(0, 1))
    return img1


class AzCanvas(QtWidgets.QLabel):
    """
    Холст для рисования цифр, для распознавания при работе MNIST
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

        self.draw28x28 = AzCanvas()
        self.preview = QtWidgets.QLabel()
        self.preview.setPixmap(QtGui.QPixmap(140, 140))
        self.preview.pixmap().fill(QtGui.QColor(QtCore.Qt.GlobalColor.white))

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setSegmentStyle(QtWidgets.QLCDNumber.Filled)  # Устанавливаем стиль сегментов
        self.lcd.setDigitCount(8)  # Устанавливаем количество цифр
        self.lcd.setMode(QtWidgets.QLCDNumber.Dec)  # Устанавливаем режим (Dec, Hex, Bin или Oct)
        self.lcd.setSmallDecimalPoint(True)  # Устанавливаем размер десятичной точки
        self.lcd.display(123.45)  # Отображаем число

        # Устанавливаем разметку для виджетов на вкладке
        gb_draw = QtWidgets.QGroupBox("Draw")
        gb_draw.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        h_draw = QtWidgets.QVBoxLayout()
        h_draw.addWidget(self.draw28x28)
        gb_draw.setLayout(h_draw)

        gb_preview = QtWidgets.QGroupBox("Preview")
        gb_preview.setAlignment(QtCore.Qt.AlignCenter)
        h_preview = QtWidgets.QVBoxLayout()
        h_preview.addWidget(self.preview)
        gb_preview.setLayout(h_preview)

        # for group, frame in ((gb_draw, frame_draw),
        #                      (gb_preview, frame_preview)):
        #     v_layout = QtWidgets.QVBoxLayout(group)
        #     v_layout.addWidget(frame)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(gb_draw)
        h_layout.addWidget(gb_preview)
        h_layout.addWidget(self.lcd)
        h_layout.addStretch(1)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(h_layout)
        # self.layout.addWidget(self.draw28x28)
        # self.layout.addWidget(self.preview)

        self.layout.addStretch(1)

        # Соединения
        self.draw28x28.signal_draw.connect(self.preview_show)

    def preview_show(self, pixmap):  # Пикселизация нарисованного объекта
        the28x28 = pixmap.scaled(28, 28, QtCore.Qt.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        pixelated = the28x28.scaled(28 * 5, 28 * 5, QtCore.Qt.IgnoreAspectRatio,
                                    QtCore.Qt.TransformationMode.FastTransformation)
        pixelated = self.print_grid(pixelated)
        self.preview.setPixmap(pixelated)
        self.update()

    def print_grid(self, pixmap):
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.gray, 1))
        # Рисуем сетку
        for x in range(0, pixmap.width(), 5):
            painter.drawLine(x, 0, x, pixmap.height())
        for y in range(0, pixmap.height(), 5):
            painter.drawLine(0, y, pixmap.width(), y)
        # Заканчиваем рисование
        painter.end()
        return pixmap

