# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------

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

# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from PyQt5.QtGui import QPainter, QPainterPath
# from PyQt5.QtCore import QSize
# from PyQt5 import QtCore, QtGui, QtWidgets
# from random import randint
#
# ded = [
#     [(140, 140), (570, 525)],
#     [(20, 20), (350, 525), (100, 300), (20, 20)],
#     [(50, 50), (280, 175), (150, 240)],
#     [(80, 80), (210, 225), (300, 300), (340, 40)],
#     [(510, 110), (340, 275), (490, 390), (510, 110)]]
#
#
# class GraphicsView(QtWidgets.QGraphicsView):
#     def __init__(self, parent=None):
#         super(GraphicsView, self).__init__(parent)
#         self.setScene(QtWidgets.QGraphicsScene(self))
#         self.resize(1000, 600)
#
#         self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
#         self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
#         self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
#         self.setFrameShape(QtWidgets.QFrame.NoFrame)
#
#     def wheelEvent(self, event):
#         """ Увеличение или уменьшение масштаба. """
#         zoomInFactor = 1.25
#         zoomOutFactor = 1 / zoomInFactor
#
#         # Save the scene pos
#         oldPos = self.mapToScene(event.pos())
#
#         # Zoom
#         if event.angleDelta().y() > 0:
#             zoomFactor = zoomInFactor
#         else:
#             zoomFactor = zoomOutFactor
#         self.scale(zoomFactor, zoomFactor)
#
#         # Get the new position
#         newPos = self.mapToScene(event.pos())
#
#         # Move scene to old position
#         delta = newPos - oldPos
#         self.translate(delta.x(), delta.y())
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#         self.w = GraphicsView(self)
#         image = QtGui.QPixmap("test.jpg")
#         self.pic = QtWidgets.QGraphicsPixmapItem()
#         self.pic.setPixmap(image)
#         self.w.scene().addItem(self.pic)
#         self.drawLine()
#         # self.pixmap_item.setPixmap(pixmap)
#
#     def initUI(self):
#         self.setMinimumSize(QSize(200, 200))
#         self.resize(1000, 600)
#
#     #    def paintEvent(self, e):
#     #        qp = QPainter()
#     #        qp.begin(self)
#     #        qp.setRenderHint(QPainter.Antialiasing)
#     #        self.drawLine(qp)
#     #        qp.end()
#
#     def drawLine(self, qp=None):  # + =None
#         path = QPainterPath()
#
#         def draw_trajectory(line):
#             for i, (x, y) in enumerate(line):
#                 if i == 0:
#                     path.moveTo(x, y)
#                 else:
#                     path.lineTo(x, y)
#
#         for line in ded:
#             draw_trajectory(line)
#
#             #            qp.drawPath(path)
#
#             self.w.scene().addPath(  # +++
#                 path,
#                 QtGui.QPen(QtGui.QColor(230, 230, 230)),
#                 QtGui.QBrush(QtGui.QColor(*[randint(0, 255) for _ in range(4)]))
#             )
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     w = MainWindow()
#     w.show()
#     sys.exit(app.exec_())

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
#
# def show_image(self, to_right: bool = True):
#     filename = None
#     if len(self.image_list) <= 0:
#         return
#     if self.current_file is None:  # ни разу после загрузки датасета не выбирался файл
#         filename = self.image_list[0]  # значит ставим первый
#     else:
#         index = self.image_list.index(self.current_file)
#         if not to_right:
#             if index - 1 >= 0:
#                 filename = self.image_list[index - 1]
#         else:
#             if index + 1 < len(self.image_list):
#                 filename = self.image_list[index + 1]
#         self.files_list.setCurrentRow()
# ------------------------------------
#
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

# ================================================================================================
# try:
#  обычный код
# except KeyboardInterrupt:
#  код при завершении програмы через ctrl + c

# class AzAction(QtWidgets.QAction):  # действие с переменой цвета иконки, когда она активна
#     def __init__(self, text, icon, icon_checked, parent=None):
#         super().__init__(newIcon(icon), text, parent)
#         self.icon_default = newIcon(icon)
#         self.icon_activate = newIcon(icon_checked)
#         self.setCheckable(True)
#         self.toggled.connect(self.tog1)
#
#     def toggle(self):
#         pass
#
#     def tog1(self):
#         if self.isChecked():
#             self.setIcon(self.icon_activate)
#         else:
#             self.setIcon(self.icon_default)

# /*QTabWidget::tab-bar {
#     left: 13px;
# }
#
# QTabBar::tab {
#   background: rgb(230, 230, 230);
#   border: 1px solid lightgray;
# }
#
# QTabBar::tab:selected {
#   font: bold;
#   background: rgb(245, 245, 245);
#   margin-bottom: -4px;
# }
#
# QTabWidget::pane {
#    border: none;
# }*/


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

#####################################################
# Полезное!
# tab_widget.setStyleSheet('background: rgb(%d, %d, %d); margin: 1px; font-size: 14px;'
#                                  % (randint(244, 255), randint(244, 255), randint(244, 255)))
# style = current_folder + "/tabwidget.qss"
# with open(style, "r") as fh:
#     self.setStyleSheet(fh.read())

#####################################################

# from functools import partial
# def add(x, y):
#     return x + y
# add_partials = []
# for i in range(1, 10):
#     function = partial(add, i)  # делаем функцию (1+y), (2+y) и т.д. до 10
#     add_partials.append(function)  # добавляем модифицированную функцию к листу add_partials
#     print('Sum of {} and 2 is {}'.format(i, add_partials[i - 1](2))) # вызываем функцию для при y = 2
############################################################
# colors = ('red', 'green', 'black', 'blue')
# for i, color in enumerate(colors):
#     self.tab_widget.addTab(QWidget(), 'Tab #{}'.format(i + 1))
#     self.tab_widget.tabBar().setTabTextColor(i, QColor(color))

#####################################################
#
# #!/usr/bin/python
# # -*- coding: utf-8 -*-
#
# # Imports
# # ------------------------------------------------------------------------------
# import sys
# from qdarktheme.qtpy.QtCore import QDir, Qt, Slot, QTranslator
# from qdarktheme.qtpy.QtGui import QAction, QActionGroup, QCursor
# from qdarktheme.qtpy.QtWidgets import QApplication, QGridLayout, QToolBar, QToolButton, QWidget, QMainWindow, \
#     QStackedWidget, QListWidget, \
#     QStatusBar, QMenuBar, QSizePolicy, QMessageBox, QLabel, QMenu
# from utils import config
# from PyQt5 import QtWidgets
# from utils.settings_handler import AppSettings
# import qdarktheme
# from functools import partial
#
# class Person():
#     def __init__(self, name="", age=None):
#         self.name = name
#         self.age = age
#
#     def getName(self):
#         return self.name
#
# # Main Widget
# # ------------------------------------------------------------------------------
# class ExampleWidget(QWidget):
#
#     def __init__(self,):
#         super(ExampleWidget, self).__init__()
#
#         self.initUI()
#
#
#     def initUI(self):
#         # formatting
#         self.setWindowTitle("Example")
#
#         # context menu
#         self.main_menu = QMenu()
#
#         self.sub_menu = QMenu("Great")
#         self.main_menu.addMenu(self.sub_menu)
#
#
#         names = ["Joe","Kevin","Amy","Doug","Jenny"]
#
#         # sub-menu
#         for index, name in enumerate(names):
#             fancyName = "%s - %s" % (index, name)
#             action = self.sub_menu.addAction( fancyName )
#             action.setData(Person(name=name))
#             action.triggered.connect(partial(self.menu_action, action))
#
#         # widgets
#         self.factionsList = QListWidget()
#
#         # signal
#         self.factionsList.setContextMenuPolicy(Qt.CustomContextMenu)
#         self.factionsList.customContextMenuRequested.connect(self.on_context_menu_factions)
#
#         # layout
#         self.mainLayout = QGridLayout(self)
#         self.mainLayout.addWidget(self.factionsList, 1, 0)
#         self.show()
#
#     def menu_action(self, item):
#         itmData = item.data()
#         print(itmData.getName())
#
#
#     def on_context_menu_factions(self, pos):
#         self.main_menu.exec_(QCursor.pos() )
#
#
# # Main
# # ------------------------------------------------------------------------------
# if __name__ == "__main__":
#
#     app = QApplication(sys.argv)
#     ex = ExampleWidget()
#     res = app.exec_()
#     sys.exit(res)

####################################################################

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

# self.merge_output_tb = QtWidgets.QToolButton()  # выходной путь; по нажатии меняется на выбранный пользователем
# self.merge_output_tb.setCheckable(True)  # кнопка "нажимательная"
# self.merge_output_tb.setText("Каталог по умолчанию:" + "\n" + self.settings.read_default_output_dir())
# self.merge_output_tb.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)  # только текст от кнопки
# self.merge_output_tb.toggled.connect(self.merge_output_tb_toggled)  # связываем с методом смены каталога
