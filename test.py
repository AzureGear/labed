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
