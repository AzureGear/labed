
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    toolBox = AnimatedToolBox()
    for i in range(8):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        for b in range((i + 1) * 2):
            layout.addWidget(QtWidgets.QPushButton('Button {}'.format(b + 1)))
        layout.addStretch()
        toolBox.addItem(container, 'Box {}'.format(i + 1))
    toolBox.show()
    sys.exit(app.exec())

#####################################################
# Полезное!
# tab_widget.setStyleSheet('background: rgb(%d, %d, %d); margin: 1px; font-size: 14px;'
#                                  % (randint(244, 255), randint(244, 255), randint(244, 255)))

#####################################################

# from functools import partial
# def add(x, y):
#     return x + y
# add_partials = []
# for i in range(1, 10):
#     function = partial(add, i)  # делаем функцию (1+y), (2+y) и т.д. до 10
#     add_partials.append(function)  # добавляем модифицированную функцию к листу add_partials
#     print('Sum of {} and 2 is {}'.format(i, add_partials[i - 1](2))) # вызываем функцию для при y = 2

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
