from qdarktheme.qtpy.QtCore import Qt
from qdarktheme.qtpy.QtWidgets import QDockWidget, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QToolBox, QTabWidget, \
    QLabel
from qdarktheme.qtpy.QtGui import QColor

from utils.settings_handler import AppSettings


class ProcessingUI(QWidget):
    """
    Класс обработки датасетов
    """

    def __init__(self, parent):
        super().__init__()
        ##  if we do not provide a color style for the whole tab widget text color this works, but as soon as we provide
        # that color, then set tabcolor stops working with qdarkstyle.

        self.settings = AppSettings()  # настройки программы
        layout = QVBoxLayout(self)  # вертикальный класс с расположением элементов интерфейса
        tabwidget = QTabWidget()
        colors = ('red', 'green', 'black', 'blue')
        for i, color in enumerate(colors):
            tabwidget.addTab(QWidget(), 'Tab #{}'.format(i + 1))
            tabwidget.tabBar().setTabTextColor(i, QColor(color))
        layout.addWidget(tabwidget)
        self.toolbox = QToolBox(self)
        self.toolbox.addItem(QLabel("Test"), "Объединить датасеты в формат SAMA")
        self.toolbox.addItem(QLabel("Test"), "Нарезать снимки заданного размера")
        # self.toolbox.addItem("Удалить из датасета")
        # self.toolbox.addItem("Поиск снимков по атрибутам разметки")
        # self.toolbox.addItem(Изменение геометрии разметки
        layout.addWidget(self.toolbox)  # ему добавляем виджет
