from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, UI_COLORS, config
from ui import new_button

import os

the_color = UI_COLORS.get("processing_color")

class TabAttributesUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Виджет типа страницы QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, parent=None):
        super(TabAttributesUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Attributes"
        self.table_widget = AzTableAttributes()
        self.setCentralWidget(self.table_widget)

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabAttributesUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Attributes
        self.name = self.tr("Attributes")
        self.setToolTip(self.tr("Поиск и редактирование снимков по атрибутам разметки"))

class AzTableAttributes(QtWidgets.QTableWidget()):
    """
    Таблица для взаимодействия с QTabWidget для работы с MNIST
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, parent=None):
        super(AzTableAttributes, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setRowCount(5)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3", "Actions"])
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        items = [["Item 1", "A", "20"],
                 ["Item 2", "C", "15"],
                 ["Item 3", "B", "18"],
                 ["Item 4", "D", "10"],
                 ["Item 5", "E", "5"]]

        for row, item in enumerate(items):
            for col, text in enumerate(item):
                new_item = QtWidgets.QTableWidgetItem(text)
                self.setItem(row, col, new_item)

            button = QtWidgets.QPushButton("...")
            button.clicked.connect(lambda ch, row=row: self.show_context_menu(row))
            self.setCellWidget(row, 3, button)

        self.setSortingEnabled(True)  # Allow sorting in the table

    def show_context_menu(self, row):
        menu = QtWidgets.QMenu()

        rename_action = QtWidgets.QAction(QtGui.QIcon("icon_rename.png"), "Rename", menu)
        rename_action.triggered.connect(lambda ch, row=row: self.rename_item(row))
        menu.addAction(rename_action)

        delete_action = QtWidgets.QAction(QtGui.QIcon("icon_delete.png"), "Delete", menu)
        delete_action.triggered.connect(lambda ch, row=row: self.delete_item(row))
        menu.addAction(delete_action)

        pos = QtGui.QCursor.pos()
        menu.exec_(pos)

    def rename_item(self, row):
        text, ok = QtWidgets.QInputDialog.getText(self, "Rename Item", "Enter new name:")
        if ok and text:
            self.table_widget.item(row, 0).setText(text)

    def delete_item(self, row):
        self.table_widget.removeRow(row)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = TabAttributesUI()
    window.setWindowTitle("Sortable Table with PyQt5")
    window.show()

    sys.exit(app.exec_())