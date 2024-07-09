from PyQt5 import QtWidgets, QtGui, QtCore
from utils import AppSettings, dn_crop, UI_COLORS, config
from ui import new_button, AzButtonLineEdit, AzSpinBox, AzTableModel, AzManualSlice, coloring_icon
import os

the_color = UI_COLORS.get("processing_color")


class TabGeometryUI(QtWidgets.QMainWindow, QtWidgets.QWidget):
    """
    Страница QTabWidget раздела Геометрия разметки
    color_active, icon_inactive цвета иконок активные и неактивные соответственно
    Example: tab_page = TabGeometryUI(QtCore.Qt.GlobalColor.red, QtCore.Qt.GlobalColor.white, self)
    """
    signal_message = QtCore.pyqtSignal(str)  # сигнал для вывода сообщения

    def __init__(self, color_active=None, color_inactive=None, parent=None):
        super(TabGeometryUI, self).__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.name = "Geometry"
        self.tool_tip_title ="Geometry of labeling"
        if color_active:
            self.icon_active = coloring_icon("glyph_geometry", color_active)
        if color_inactive:
            self.icon_inactive = coloring_icon("glyph_geometry", color_inactive)
        self.setCentralWidget(QtWidgets.QPushButton("text"))

    @QtCore.pyqtSlot(str)
    def default_dir_changed(self, path):
        # заглушка на смену каталога для выходных данных по умолчанию
        pass

    def tr(self, text):
        return QtCore.QCoreApplication.translate("TabMergeUI", text)

    def translate_ui(self):  # переводим текущие тексты и добавленные/вложенные вкладки
        # Processing - Merge
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = TabGeometryUI()
    w.show()
    app.exec()
