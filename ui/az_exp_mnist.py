from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np


# TODO: сделать класс наследуемый от LCD цифр с кружочком вокруг них, который показывает процентное отношение распоз.
# Тип полностью закрытый кружок = 100%, на четверть = 25%.

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

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(h_layout)
        self.layout.addStretch(1)

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
