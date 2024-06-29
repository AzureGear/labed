from PyQt5 import QtWidgets, QtGui, QtCore


class PageMNIST(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PageMNIST, self).__init__(parent)

        # Создаем текстовое поле для примера
        self.text_field = QtWidgets.QTextEdit(self)
        self.name = "MNIST"
        # Устанавливаем разметку для виджетов на вкладке
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text_field)

# class Window(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         # Создаём изображение 28x28 пикселей, заполненное белым цветом
#         image = np.ones((28, 28, 3), dtype=np.uint8) * 255
#
#         # Преобразуем изображение в формат QImage
#         qimage = QImage(image, 28, 28, QImage.Format_RGB888)
#
#         # Увеличиваем изображение в 3 раза
#         scaled_image = qimage.scaled(28 * 3, 28 * 3, Qt.IgnoreAspectRatio, Qt.FastTransformation)
#
#         # Создаём виджет QLabel для отображения изображения
#         self.label = QLabel()
#         self.pixmap = QPixmap.fromImage(scaled_image)
#         self.label.setPixmap(self.pixmap)
#         self.label.setFixedSize(scaled_image.width(), scaled_image.height())
#
#         # Добавляем виджет в главное окно
#         self.setCentralWidget(self.label)
#
#         # Создаём меню
#         menu = QMenu("Menu", self)
#         self.menuBar().addMenu(menu)
#
#         # Создаём действие для рисования
#         self.draw_action = QAction("Draw", self)
#         self.draw_action.setCheckable(True)
#         self.draw_action.triggered.connect(self.toggle_draw)
#         menu.addAction(self.draw_action)
#
#         # Создаём флаг для рисования
#         self.drawing = False
#
#         # Создаём объект QPainter для рисования на изображении
#         self.painter = QPainter(self.pixmap)
#         self.pen = QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
#
#         # Отображаем сетку
#         grid_size = 10
#         for i in range(1, 28):
#             x = i * grid_size * 3
#             y = 0
#             w = 1
#             h = 28 * grid_size * 3
#             self.painter.setPen(Qt.lightGray)
#             self.painter.drawLine(x, y, x, y + h)
#             self.painter.drawLine(y, x, y + w, x)
#
#     def toggle_draw(self):
#         self.drawing = not self.drawing
#
#     def mousePressEvent(self, event):
#         if self.drawing:
#             self.last_point = event.pos()
#
#     def mouseMoveEvent(self, event):
#         if self.drawing and event.buttons() & Qt.LeftButton:
#             self.painter.setPen(self.pen)
#             self.painter.drawLine(self.last_point, event.pos())
#             self.last_point = event.pos()
#             self.update()
#
#     def mouseReleaseEvent(self, event):
#         if self.drawing:
#             self.painter.setPen(self.pen)
#             self.painter.drawLine(self.last_point, event.pos())
#             self.last_point = None
#             self.update()

# import sys
# from PyQt5.QtWidgets import QWidget, QApplication
# from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QImage
# from PyQt5.QtCore import Qt
#
#
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.flag = False
#         self.resize(200, 200)
#         self.image = QImage(self.width(), self.height(), QImage.Format_Grayscale8)
#         self.image.fill(QColor(255, 255, 255))
#         self.show()
#
#     def mousePressEvent(self, event):
#         self.clear()
#         if event.button() == Qt.LeftButton:
#             self.flag = True
#             self.paint = QPainter(self.image)
#             self.ellips(event)
#
#     def paintEvent(self, event):
#         paint = QPainter(self)
#         paint.drawImage(0, 0, self.image)
#
#     def mouseMoveEvent(self, event):
#         if self.flag:
#             # print(event.pos())
#             self.ellips(event)
#
#     def mouseReleaseEvent(self, event) -> None:
#         if event.button() == Qt.RightButton:
#             self.clear()
#         elif event.button() == Qt.LeftButton:
#             self.flag = False
#         self.update()
#
#     def ellips(self, event):
#         self.paint.setBrush(QColor('black'))
#         self.paint.drawEllipse(event.pos(), 3, 3)
#         self.update()
#
#     def clear(self):
#         self.image.fill(QColor(255, 255, 255))
#
# app = QApplication(sys.argv)
# w = Example()
# sys.exit(app.exec_())