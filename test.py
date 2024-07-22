# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# change_color = "#238b45"
# self.project_description.setStyleSheet(f"*{{background-color: {bg_color}; border: 1px solid #d90909;;}}")
# ----------------------------------------------------------------------------------------------------------------------
# indexes = self.image_table.selectionModel().selectedIndexes()
# print(len(indexes))
# for index in indexes:
#     role = QtCore.Qt.ItemDataRole.DisplayRole  # or Qt.DecorationRole
#     print(self.image_table.model().data(self.image_table.model().index(index.row(), 1)))
#     # print(self.image_table.model().data(index, role))
#     # print(self.image_table.model().data(self.image_table.index .index(index.row(), 0)))
#     # QTableView, Selection, QModelIndexes
# ----------------------------------------------------------------------------------------------------------------------
# # example for pandas QTableView
# import sys
# from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import Qt
# import pandas as pd
#
#
# class TableModel(QtCore.QAbstractTableModel):
#
#     def __init__(self, data):
#         super(TableModel, self).__init__()
#         self._data = data
#
#     def data(self, index, role):
#         if role == Qt.DisplayRole:
#             value = self._data.iloc[index.row(), index.column()]
#             return str(value)
#
#     def rowCount(self, index):
#         return self._data.shape[0]
#
#     def columnCount(self, index):
#         return self._data.shape[1]
#
#     def headerData(self, section, orientation, role):
#         # section is the index of the column/row.
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Horizontal:
#                 return str(self._data.columns[section])
#
#             if orientation == Qt.Vertical:
#                 return str(self._data.index[section])
#
#
# class MainWindow(QtWidgets.QMainWindow):
#
#     def __init__(self):
#         super().__init__()
#
#         self.table = QtWidgets.QTableView()
#
#         data = pd.DataFrame([
#           [1, 9, 2],
#           [1, 0, -1],
#           [3, 5, 2],
#           [3, 3, 2],
#           [5, 8, 9],
#         ], columns = ['A', 'B', 'C'], index=['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'])
#
#         self.model = TableModel(data)
#         self.table.setModel(self.model)
#
#         self.setCentralWidget(self.table)
#
#
# app=QtWidgets.QApplication(sys.argv)
# window=MainWindow()
# window.show()
# app.exec_()
# ----------------------------------------------------------------------------------------------------------------------
import re

# s = "asdasdasdaasdasdad03.jpg"
# pattern = r"^([^_]+)_([^_]+)"
# match = re.search(pattern, s)
# result1 = match.group(0)
# result2 = match.group(2)
# print(len(match))  # Выведет "19981"

# ----------------------------------------------------------------------------------------------------------------------
# import sys
# from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView
# from PyQt5.uic import loadUi
# from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
#
# class CustomTableModel(QAbstractTableModel):
#     def __init__(self, data, parent=None):
#         QAbstractTableModel.__init__(self, parent)
#         self._data = data
#
#     def rowCount(self, parent=QModelIndex()):
#         return len(self._data)
#
#     def columnCount(self, parent=QModelIndex()):
#         if self._data:
#             return len(self._data[0])
#         else:
#             return 0
#
#     def data(self, index, role=Qt.DisplayRole):
#         if index.isValid() and role == Qt.DisplayRole:
#             return self._data[index.row()][index.column()]
#         return None
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.tableView = QtWidgets.QTableView()
#         data = [
#             ["Item 1", "Description 1", "Category 1"],
#             ["Item 2", "Description 2", "Category 2"],
#             ["Item 3", "Description 3", "Category 3"],
#             ["Item 4", "Description 4", "Category 4"],
#             ["Item 5", "Description 5", "Category 5"],
#             ["Item 6", "Description 6", "Category 6"],
#             ["Item 7", "Description 7", "Category 7"],
#             ["Item 8", "Description 8", "Category 8"],
#         ]
#
#         table_model = CustomTableModel(data)
#         self.tableView.setModel(table_model)
#
#         # Set selection behavior and selection mode
#         self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
#
#         self.setCentralWidget(self.tableView)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec_())
# ----------------------------------------------------------------------------------------------------------------------
# from PyQt5 import QtWidgets, QtGui, QtCore
# import sys
#
# class MyApp(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.initUI()
#
#     def initUI(self):
#         self.layout = QtWidgets.QVBoxLayout(self)
#         self.layout.setContentsMargins(10, 10, 10, 10)
#         self.layout.setSpacing(10)
#         self.layout.setStyleSheet("border: 2px solid black;")
#
#         for i in range(3):
#             button = QtWidgets.QPushButton(f"Button {i+1}", self)
#             self.layout.addWidget(button)
#
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#
#     ex = MyApp()
#     ex.show()
#
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------
# from PyQt5 import QtCore, QtWidgets
#
#
# class MyThread(QtCore.QThread):
#     mysignal = QtCore.pyqtSignal(str)
#
#     def __init__(self, parent=None):
#         QtCore.QThread.__init__(self, parent)
#
#     def run(self):
#         for i in range(1, 21):
#             self.sleep(3)  # "Засыпаем" на 3 секунды
#             # Передача данных из потока через сигнал
#             self.mysignal.emit("i = %s" % i)
#
#
# class MyWindow(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         QtWidgets.QWidget.__init__(self, parent)
#         self.label = QtWidgets.QLabel("Нажмите кнопку для запуска потока")
#         self.label.setAlignment(QtCore.Qt.AlignHCenter)
#         self.button = QtWidgets.QPushButton("Запустить процесс")
#         self.vbox = QtWidgets.QVBoxLayout()
#         self.vbox.addWidget(self.label)
#         self.vbox.addWidget(self.button)
#         self.setLayout(self.vbox)
#         self.mythread = MyThread()  # Создаем экземпляр класса
#         self.button.clicked.connect(self.on_clicked)
#         self.mythread.started.connect(self.on_started)
#         self.mythread.finished.connect(self.on_finished)
#         self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
#
#     def on_clicked(self):
#         self.button.setDisabled(True)  # Делаем кнопку неактивной
#         self.mythread.start()  # Запускаем поток
#
#     def on_started(self):  # Вызывается при запуске потока
#         self.label.setText("Вызван метод on_started ()")
#
#     def on_finished(self):  # Вызывается при завершении потока
#         self.label.setText("Вызван метод on_finished()")
#         self.button.setDisabled(False)  # Делаем кнопку активной
#
#     def on_change(self, s):
#         self.label.setText(s)
#
#
# if __name__ == "__main__":
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     window = MyWindow()
#     window.setWindowTitle("Использование класса QThread")
#     window.resize(300, 70)
#     window.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
# from PyQt5.QtCore import Qt, QRect
# from PyQt5.QtGui import QPainter, QColor, QPen
#
# class MyWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         # Create two QLabel widgets
#         self.label1 = QLabel("Label 1")
#         self.label2 = QLabel("Label 2")
#
#         # Create a vertical box layout and add the labels
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.label1)
#         self.layout.addWidget(self.label2)
#
#         # Set the layout on the widget
#         self.setLayout(self.layout)
#
#         # Set the margin and spacing of the layout to 0
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.layout.setSpacing(0)
#
#         # Set the widget's background color to white
#         self.setAutoFillBackground(True)
#         palette = self.palette()
#         palette.setColor(palette.Window, Qt.white)
#         self.setPalette(palette)
#
#     def paintEvent(self, event):
#         # Call the base class paintEvent method
#         super().paintEvent(event)
#
#         # Create a QPainter object
#         painter = QPainter(self)
#
#         # Set the pen to a red, thin line
#         pen = QPen(QColor(255, 0, 0), 1)
#         painter.setPen(pen)
#
#         # Get the rectangles for the labels
#         label1_rect = self.label1.geometry()
#         label2_rect = self.label2.geometry()
#
#         # Draw the rectangles for the labels
#         painter.drawRect(label1_rect)
#         painter.drawRect(label2_rect)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     # Create an instance of the custom widget
#     widget = MyWidget()
#
#     # Set the window title and size
#     widget.setWindowTitle("My Widget")
#     widget.resize(300, 200)
#
#     # Show the widget and start the Qt event loop
#     widget.show()
#     sys.exit(app.exec_())
# ----------------------------------------------------------------------------------------------------------------------

# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
#
# class NoMouseButtonMoveRectItem(QGraphicsRectItem):
#     moving = False
#     def mousePressEvent(self, event):
#         super().mousePressEvent(event)
#         if event.button() == Qt.LeftButton:
#             # by defaults, mouse press events are not accepted/handled,
#             # meaning that no further mouseMoveEvent or mouseReleaseEvent
#             # will *ever* be received by this item; with the following,
#             # those events will be properly dispatched
#             event.accept()
#             self.pressPos = event.screenPos()
#
#     def mouseMoveEvent(self, event):
#         if self.moving:
#             # map the position to the parent in order to ensure that the
#             # transformations are properly considered:
#             currentParentPos = self.mapToParent(
#                 self.mapFromScene(event.scenePos()))
#             originParentPos = self.mapToParent(
#                 self.mapFromScene(event.buttonDownScenePos(Qt.LeftButton)))
#             self.setPos(self.startPos + currentParentPos - originParentPos)
#         else:
#             super().mouseMoveEvent(event)
#
#     def mouseReleaseEvent(self, event):
#         super().mouseReleaseEvent(event)
#         if (event.button() != Qt.LeftButton
#             or event.pos() not in self.boundingRect()):
#                 return
#
#         # the following code block is to allow compatibility with the
#         # ItemIsMovable flag: if the item has the flag set and was moved while
#         # keeping the left mouse button pressed, we proceed with our
#         # no-mouse-button-moved approach only *if* the difference between the
#         # pressed and released mouse positions is smaller than the application
#         # default value for drag movements; in this way, small, involuntary
#         # movements usually created between pressing and releasing the mouse
#         # button will still be considered as candidates for our implementation;
#         # if you are *not* interested in this flag, just ignore this code block
#         distance = (event.screenPos() - self.pressPos).manhattanLength()
#         if (not self.moving and distance > QApplication.startDragDistance()):
#             return
#         # end of ItemIsMovable support
#
#         self.moving = not self.moving
#         # the following is *mandatory*
#         self.setAcceptHoverEvents(self.moving)
#         if self.moving:
#             self.startPos = self.pos()
#             self.grabMouse()
#         else:
#             self.ungrabMouse()
#
#
# if __name__ == '__main__':
#     import sys
#     from random import randrange, choice
#     app = QApplication(sys.argv)
#     scene = QGraphicsScene()
#     view = QGraphicsView(scene)
#     view.resize(QApplication.primaryScreen().size() * 2 / 3)
#     # create random items that support click/release motion
#     for i in range(10):
#         item = NoMouseButtonMoveRectItem(0, 0, 100, 100)
#         item.setPos(randrange(500), randrange(500))
#         item.setPen(QColor(*(randrange(255) for _ in range(3))))
#         if choice((0, 1)):
#             item.setFlags(item.ItemIsMovable | item.ItemIsSelectable)
#             QGraphicsSimpleTextItem('Movable flag', item)
#         else:
#             item.setBrush(QColor(*(randrange(255) for _ in range(3))))
#         scene.addItem(item)
#     view.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5.Qt import *
# from PyQt5 import QtWidgets
# from PyQt5 import QtGui
#
# the_color = Qt.yellow
#
#
# class RectItem(QGraphicsRectItem):
#     def __init__(self, qrectf):
#         super().__init__()
#         self.qrectf = qrectf
#         self.setRect(self.qrectf)
#         self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
#
#         self.line = QGraphicsLineItem(self)
#         self.line.setPen(QPen(Qt.red, 2, Qt.SolidLine))
#         self.line.setLine(0, 0, 50, 50)
#         self.line2 = QGraphicsLineItem(self)
#         self.line2.setPen(QPen(Qt.green, 2, Qt.SolidLine))
#         self.line2.setLine(QLineF(0, 50, 50, 0))
#
#     def mouseMoveEvent(self, event):
#         self.moveBy(event.pos().x() - event.lastPos().x(),
#                     event.pos().y() - event.lastPos().y())
#
#
# class PointWithRect(QGraphicsRectItem):
#     """
#     Класс для хранения точки-центра с рамкой вокруг по значению Crop-size'а
#     Принимает точку (QPointF) и величину кадрирования (int)
#     """
#
#     def __init__(self, point: QPointF, crop_size):
#         super().__init__()
#         self.point = point  # сохраняем значение центральной точки
#         self.crop_size = crop_size  # значение величины кадрирования, например 1280, или 256
#         self.line = QGraphicsLineItem(self)
#         self.line.setPen(QtGui.QPen(the_color, 1, Qt.SolidLine))  # диагональная линия
#         self.line.setLine(point[0] - crop_size / 2.5, point[1] - crop_size / 2.5,
#                           point[0] + crop_size / 2.5, point[1] + crop_size / 2.5)
#         self.line2 = QGraphicsLineItem(self)
#         self.line2.setPen(QtGui.QPen(the_color, 1, Qt.SolidLine))  # диагональная линия 2
#         self.line2.setLine(point[0] + crop_size / 2.5, point[1] - crop_size / 2.5,
#                            point[0] - crop_size / 2.5, point[1] + crop_size / 2.5)
#
#         rect = QRectF(point[0] - crop_size / 2, point[1] - crop_size / 2, crop_size, crop_size)
#         self.setRect(rect)
#         self.setPen(QtGui.QPen(the_color, 2, Qt.SolidLine))
#         self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
#
#     def mouseMoveEvent(self, event):
#         self.moveBy(event.pos().x() - event.lastPos().x(),
#                     event.pos().y() - event.lastPos().y())
#
#
# class Scene(QGraphicsScene):
#     def __init__(self):
#         super().__init__()
#
#         self.setSceneRect(0, 0, 400, 400)
#         self.qrectf = None
#         self.list_rect = []
#         self.num_old = 0  # прошлый номер для полигонов
#
#     def add_rect(self, num):  # добавление квадратов
#         if num == 0:  # очистить сцену
#             self.clear()
#         elif num > self.num_old:
#             for i in range(self.num_old, num):
#                 rect = RectItem(QRectF(0, 0, 50, 50))
#                 # rect.moveBy(25, 100)
#                 self.list_rect.append(rect)
#                 self.addItem(rect)
#         elif num < self.num_old:
#             for i in range(num, self.num_old):
#                 self.removeItem(self.list_rect[-1])
#                 self.list_rect.pop()
#         else:
#             pass
#         self.num_old = num
#
#     def add_circle(self):
#         point = PointWithRect([125.441, 122.111], 33)
#         self.addItem(point)
#         # item = QtWidgets.QGraphicsEllipseItem(44, 85, 2, 2)
#         # item.setPen(QPen(Qt.yellow, 15, Qt.SolidLine))
#         # self.addItem(item)
#
#
# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.scene = Scene()
#         self.canvas = QGraphicsView()
#         self.canvas.setScene(self.scene)
#         # self.qrectf = QRectF(0, 0, 50, 50)
#         self.spinbox = QSpinBox()
#         self.spinbox.setRange(0, 8)  # +
#         self.spinbox.valueChanged.connect(self.spinbox_event)
#
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.canvas)
#         layout.addWidget(self.spinbox)
#
#         # self.scene.add_qrectf(self.qrectf)
#
#     def spinbox_event(self):
#         self.scene.add_rect(self.spinbox.value())
#         self.scene.add_circle()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = Window()
#     w.show()
#     app.exec()

# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5.Qt import *
# class RectItem(QGraphicsRectItem):
#     def __init__(self, qrectf):
#         super().__init__()
#
#         self.qrectf = qrectf
#         self.setRect(self.qrectf)
#         self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
#
#         self.line = QGraphicsLineItem(self)
#         self.line.setPen(QPen(Qt.red, 2, Qt.SolidLine))
#         self.line.setLine(0, 0, 50, 50)
#         self.line2 = QGraphicsLineItem(self)
#         self.line2.setPen(QPen(Qt.green, 2, Qt.SolidLine))
#         self.line2.setLine(QLineF(0, 50, 50, 0))
#
#     def mouseMoveEvent(self, event):
#         self.moveBy(event.pos().x() - event.lastPos().x(),
#                     event.pos().y() - event.lastPos().y())
#
#
# class Scene(QGraphicsScene):
#     def __init__(self):
#         super().__init__()
#
#         self.setSceneRect(0, 0, 400, 400)
#         self.qrectf = None
#         self.list_rect = []
#         self.num_old = 0  # прошлый номер для полигонов
#
#     def add_qrectf(self, qrectf):
#         self.qrectf = qrectf  # принимаем QRectF
#
#     def add_rect(self, num):  # добавление квадратов
#         if num == 0:  # очистить сцену
#             self.clear()
#         elif num > self.num_old:
#             for i in range(self.num_old, num):
#                 rect = RectItem(self.qrectf)
#                 rect.moveBy(25, 100)
#                 self.list_rect.append(rect)
#                 self.addItem(rect)
#         elif num < self.num_old:
#             for i in range(num, self.num_old):
#                 self.removeItem(self.list_rect[-1])
#                 self.list_rect.pop()
#         else:
#             pass
#         self.num_old = num
#
#     def add_circle(self):
#         rad = 1
#         self.addEllipse(rad, rad, rad * 2, rad * 2, Qt.QPen(Qt.green), Qt.green)
#
#
# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.scene = Scene()
#         self.canvas = QGraphicsView()
#         self.canvas.setScene(self.scene)
#         self.qrectf = QRectF(0, 0, 50, 50)
#         self.spinbox = QSpinBox()
#         self.spinbox.setRange(0, 8)  # +
#         self.spinbox.valueChanged.connect(self.spinbox_event)
#
#         layout = QHBoxLayout(self)
#         layout.addWidget(self.canvas)
#         layout.addWidget(self.spinbox)
#
#         self.scene.add_qrectf(self.qrectf)
#
#     def spinbox_event(self):
#         self.scene.add_rect(self.spinbox.value())
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = Window()
#     w.show()
#     app.exec()

# ----------------------------------------------------------------------------------------------------------------------

# # Автоматическое изменение размера картинки автомасштабирование
# from PyQt5.Qt import *
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         centralWidget = QWidget()
#         self.setCentralWidget(centralWidget)
#
#         self.label = QLabel()
#         self.pixmap = QPixmap("test.jpg")
#         self.label.setPixmap(self.pixmap.scaled(self.label.size(),
#                                                 Qt.KeepAspectRatio, Qt.SmoothTransformation))
#
#         self.label.setSizePolicy(QSizePolicy.Expanding,
#                                  QSizePolicy.Expanding)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.label.setMinimumSize(100, 100)
#
#         self.pushButton = QPushButton('Выбрать изображение')
#         self.pushButton.clicked.connect(self.load_image)
#
#         layout = QGridLayout(centralWidget)
#         layout.addWidget(self.label)
#         layout.addWidget(self.pushButton)
#
#     def load_image(self):
#         imagePath, _ = QFileDialog.getOpenFileName(
#             self,
#             "Select Image",
#             ".",
#             "Image Files (*.png *.jpg *.jpeg *.bmp)")
#         if imagePath:
#             self.pixmap = QPixmap(imagePath)
#             self.label.setPixmap(self.pixmap.scaled(
#                 self.label.size(),
#                 Qt.KeepAspectRatio,
#                 Qt.SmoothTransformation
#             ))
#
#     def resizeEvent(self, event):
#         scaledSize = self.label.size()
#         scaledSize.scale(self.label.size(), Qt.KeepAspectRatio)
#         if not self.label.pixmap() or scaledSize != self.label.pixmap().size():
#             self.updateLabel()
#
#     def updateLabel(self):
#         self.label.setPixmap(self.pixmap.scaled(
#             self.label.size(),
#             Qt.KeepAspectRatio,
#             Qt.SmoothTransformation
#         ))
#
#
# if __name__ == "__main__":
#     import sys
#
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------

# # Разница между сигналами в pySide и PyQt5
# # my_custom_signal = pyqtSignal()  # PyQt5
# my_custom_signal = Signal()  # PySide2
#
# my_other_signal = pyqtSignal(int)  # PyQt5
# my_other_signal = Signal(int)  # PySide2

# ----------------------------------------------------------------------------------------------------------------------
# hor_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
# Спейсер, спайсер


# def getFileName(self):
#     filename, filetype = QFileDialog.getOpenFileName(self,
#                                                      "Выбрать файл",
#                                                      ".",
#                                                      "Text Files(*.txt);;JPEG Files(*.jpeg);;\
#                                                      PNG Files(*.png);;GIF File(*.gif);;All Files(*)")
#     self.plainTextEdit.appendHtml("<br>Выбрали файл: <b>{}</b> <br> <b>{:*^54}</b>"
#                                   "".format(filename, filetype))
#
#
# def getFileNames(self):
#     filenames, ok = QFileDialog.getOpenFileNames(self,
#                                                  "Выберите несколько файлов",
#                                                  ".",
#                                                  "All Files(*.*)")
#     self.plainTextEdit.appendHtml("""<br>Выбрали несколько файлов:
#                                    <b>{}</b> <br> <b>{:*^80}</b>"""
#                                   "".format(filenames, ok))
#
# ----------------------------------------------------------------------------------------------------------------------
# Отображение картинок, текста и проч. - было добавлено в init
# test_img = os.path.join(current_folder, "..", "test.jpg")
# scene = QGraphicsScene()  # Создание графической сцены
# graphicView = QGraphicsView(scene)  # Создание инструмента для отрисовки графической сцены
# graphicView.setGeometry(200, 220, 400, 400)  # Задание местоположения и размера графической сцены
# picture = QPixmap(test_img)  # Создание объекта QPixmap
# image_container = QGraphicsPixmapItem()  # Создание "пустого" объекта QGraphicsPixmapItem
# image_container.setPixmap(picture)  # Задание изображения в объект QGraphicsPixmapItem
# image_container.setOffset(0, 0)  # Позиция объекта QGraphicsPixmapItem
# # Добавление объекта QGraphicsPixmapItem на сцену
# scene.addItem(image_container)
#
# # Создание объекта QGraphicsSimpleTextItem
# text = QGraphicsSimpleTextItem('Пример текста')
# # text.setX(0) # Задание позиции текста
# # text.setY(200)
# scene.addItem(text)  # Добавление текста на сцену
# layout.addWidget(graphicView)
#
# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5.Qt import *
#
#
# class GraphicsView(QGraphicsView):
#     def __init__(self):
#         super(GraphicsView, self).__init__()
#         self.resize(400, 400)
#
#         self.scene = QGraphicsScene()
#         self.scene.setSceneRect(0, 0, 400, 400)
#
#         self.pic = QGraphicsPixmapItem()
#         self.pic.setPixmap(QPixmap('Ok.png').scaled(60, 60))
#         # позволяет выбирать его и перемещать
#         self.pic.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
#         # установить смещение изображения от начала координат сцены
#         self.pic.setOffset(170, 170)
#
#         self.text = QGraphicsTextItem()
#         self.text.setPlainText('Hello QGraphicsPixmapItem')
#         self.text.setDefaultTextColor(QColor('#91091e'))  # для установки цвета текста
#         # setPos - для установки положения текстовых примитивов относительно начала координат сцены
#         self.text.setPos(130, 230)
#
#         self.scene.addItem(self.pic)
#         self.scene.addItem(self.text)
#         self.setScene(self.scene)
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.centralWidget = QWidget()
#         self.setCentralWidget(self.centralWidget)
#
#         self.graphicsView = GraphicsView()  # создаём QGraphicView
#         self.open_im = QPushButton('Add image')
#         self.open_im.clicked.connect(self.addImage)
#
#         layout = QVBoxLayout(self.centralWidget)
#         layout.addWidget(self.graphicsView)
#         layout.addWidget(self.open_im)
#
#     def addImage(self):
#         #        pixmap = QGraphicsItem(QPixmap(fname))
#         #        form.srcGraphicsView.addItem(pixmap)
#         fname, _ = QFileDialog.getOpenFileName(
#             self, 'Open file', '.', 'Image Files (*.png *.jpg *.bmp)')
#         if fname:
#             pic = QGraphicsPixmapItem()
#             pic.setPixmap(QPixmap(fname).scaled(160, 160))
#             pic.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
#             pic.setOffset(12, 12)
#             self.graphicsView.scene.addItem(pic)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     demo = MainWindow()  # Demo()
#     demo.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------

# try:
#  обычный код
# except KeyboardInterrupt:
#  код при завершении програмы через ctrl + c

# ----------------------------------------------------------------------------------------------------------------------
# if __name__ == '__main__':
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     toolBox = AnimatedToolBox()
#     for i in range(8):
#         container = QtWidgets.QWidget()
#         layout = QtWidgets.QVBoxLayout(container)
#         for b in range((i + 1) * 2):
#             layout.addWidget(QtWidgets.QPushButton('Button {}'.format(b + 1)))
#         layout.addStretch()
#         toolBox.addItem(container, 'Box {}'.format(i + 1))
#     toolBox.show()
#     sys.exit(app.exec())

# ----------------------------------------------------------------------------------------------------------------------


# tab_widget.setStyleSheet('background: rgb(%d, %d, %d); margin: 1px; font-size: 14px;'
#                                  % (randint(244, 255), randint(244, 255), randint(244, 255)))
# style = current_folder + "/tabwidget.qss"
# with open(style, "r") as fh:
#     self.setStyleSheet(fh.read())

# ----------------------------------------------------------------------------------------------------------------------

# from functools import partial
# def add(x, y):
#     return x + y
# add_partials = []
# for i in range(1, 10):
#     function = partial(add, i)  # делаем функцию (1+y), (2+y) и т.д. до 10
#     add_partials.append(function)  # добавляем модифицированную функцию к листу add_partials
#     print('Sum of {} and 2 is {}'.format(i, add_partials[i - 1](2))) # вызываем функцию для при y = 2

# ----------------------------------------------------------------------------------------------------------------------

# colors = ('red', 'green', 'black', 'blue')
# for i, color in enumerate(colors):
#     self.tab_widget.addTab(QWidget(), 'Tab #{}'.format(i + 1))
#     self.tab_widget.tabBar().setTabTextColor(i, QColor(color))

# ----------------------------------------------------------------------------------------------------------------------

# import sys
# from PyQt5 import QtCore, QtGui, QtWidgets
#
#
# class Demo(QtWidgets.QWidget):
#     def __init__(self):
#         super(Demo, self).__init__()
#         self.button = QtWidgets.QPushButton()
#         self.label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
#
#         self.combo = QtWidgets.QComboBox(self)
#         self.combo.currentIndexChanged.connect(self.change_func)
#
#         self.trans = QtCore.QTranslator(self)   # переводчик
#
#         self.v_layout = QtWidgets.QVBoxLayout(self)
#         self.v_layout.addWidget(self.combo)
#         self.v_layout.addWidget(self.button)
#         self.v_layout.addWidget(self.label)
#
#         options = ([('English', ''), ('français', 'eng-fr'), ('中文', 'eng-chs'), ])
#
#         for i, (text, lang) in enumerate(options):
#             self.combo.addItem(text)
#             self.combo.setItemData(i, lang)
#         self.retranslateUi()
#
#     @QtCore.pyqtSlot(int)
#     def change_func(self, index):
#         data = self.combo.itemData(index)
#         if data:
#             self.trans.load(data)
#             QtWidgets.QApplication.instance().installTranslator(self.trans)
#         else:
#             QtWidgets.QApplication.instance().removeTranslator(self.trans)
#
#     def changeEvent(self, event):
#         if event.type() == QtCore.QEvent.LanguageChange:
#             self.retranslateUi()
#         super(Demo, self).changeEvent(event)
#
#     def retranslateUi(self):
#         self.button.setText(QtWidgets.QApplication.translate('Demo', 'Start'))
#         self.label.setText(QtWidgets.QApplication.translate('Demo', 'Hello, World'))
#
#
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     demo = Demo()
#     demo.show()
#     sys.exit(app.exec_())

# ----------------------------------------------------------------------------------------------------------------------
# Отображение границы виджета
# self.label_info.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
# self.label_file_path.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)


# ----------------------------------------------------------------------------------------------------------------------
# class _TableModel(QtCore.QAbstractTableModel):  # Реализация qdarktheme
#     def __init__(self) -> None:
#         super().__init__()
#         self._data = [[i * 10 + j for j in range(4)] for i in range(5)]
#
#     def data(self, index: QtCore.QModelIndex, role: int):
#         if role == QtCore.Qt.ItemDataRole.DisplayRole:
#             return self._data[index.row()][index.column()]
#         if role == QtCore.Qt.ItemDataRole.CheckStateRole and index.column() == 1:
#             return QtCore.Qt.CheckState.Checked if index.row() % 2 == 0 else QtCore.Qt.CheckState.Unchecked
#         if role == QtCore.Qt.ItemDataRole.EditRole and index.column() == 2:
#             return self._data[index.row()][index.column()]  # pragma: no cover
#         return None
#
#     def rowCount(self, index) -> int:  # noqa: N802
#         return len(self._data)
#
#     def columnCount(self, index) -> int:  # noqa: N802
#         return len(self._data[0])
#
#     def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
#         flag = super().flags(index)
#         if index.column() == 1:
#             flag |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
#         elif index.column() in (2, 3):
#             flag |= QtCore.Qt.ItemFlag.ItemIsEditable
#         return flag  # type: ignore
#
#     def headerData(  # noqa: N802
#             self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
#         if role != QtCore.Qt.ItemDataRole.DisplayRole:
#             return None
#         if orientation == QtCore.Qt.Orientation.Horizontal:
#             return ["Normal", "Checkbox", "Spinbox", "LineEdit"][section]
#         return section * 100
# ----------------------------------------------------------------------------------------------------------------------
