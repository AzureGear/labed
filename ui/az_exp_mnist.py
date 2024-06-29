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

    def __init__(self):
        super().__init__()
        pixmap = QtGui.QPixmap(140, 140)  # кратно 28 в пять раз
        self.clear(pixmap)
        self.setPixmap(pixmap)
        self.draw = False  # рисование
        self.last_x, self.last_y = None, None
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

    def clear(self, pixmap):  # очистка холста = по сути заливка всего белым цветом
        pixmap.fill(QtCore.Qt.GlobalColor.white)
        self.update()


class PageMNIST(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)

        # Создаем текстовое поле для примера
        self.name = "MNIST"
        # Устанавливаем разметку для виджетов на вкладке
        self.layout = QtWidgets.QVBoxLayout(self)
        self.draw28x28 = AzCanvas()
        self.button = QtWidgets.QPushButton("Push")
        self.resizedPixmap = QtWidgets.QLabel()
        self.resizedPixmap.setPixmap(QtGui.QPixmap(140, 140))
        self.resizedPixmap.pixmap().fill(QtGui.QColor(QtCore.Qt.GlobalColor.white))
        self.button.clicked.connect(self.push_click)
        self.layout.addWidget(self.draw28x28)
        self.layout.addWidget(self.resizedPixmap)
        self.layout.addWidget(self.button)

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setSegmentStyle(QtWidgets.QLCDNumber.Filled)  # Устанавливаем стиль сегментов
        self.lcd.setDigitCount(8)  # Устанавливаем количество цифр
        self.lcd.setMode(QtWidgets.QLCDNumber.Dec)  # Устанавливаем режим (Dec, Hex, Bin или Oct)
        self.lcd.setSmallDecimalPoint(True)  # Устанавливаем размер десятичной точки
        self.lcd.display(123.45)  # Отображаем число
        self.layout.addWidget(self.lcd)

        self.layout.addStretch(1)

    def push_click(self):
        small_img = self.draw28x28.pixmap().scaled(28, 28, QtCore.Qt.KeepAspectRatio,
                                                   QtCore.Qt.TransformationMode.SmoothTransformation)
        big_again = small_img.scaled(28 * 5, 28 * 5, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.TransformationMode.FastTransformation)
        painter = QtGui.QPainter(big_again)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.gray, 1))
        # Рисуем сетку
        for x in range(0, big_again.width(), 5):
            painter.drawLine(x, 0, x, big_again.height())
        for y in range(0, big_again.height(), 5):
            painter.drawLine(0, y, big_again.width(), y)
        # Заканчиваем рисование
        painter.end()
        self.resizedPixmap.setPixmap(big_again)
        self.update()

