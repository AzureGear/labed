from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QColor
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLineEdit
from utils import AppSettings
from ui import newPixmap
import os
import re


class AzImageViewer(QtWidgets.QGraphicsView):  # Реализация Романа Хабарова
    """
    Виджет для отображения изображений *.jpg, *.png и т.д.
    """

    def __init__(self, parent=None, active_color=None, fat_point_color=None, on_rubber_band_mode=None):
        super().__init__(parent)
        scene = QtWidgets.QGraphicsScene(self)
        self.setScene(scene)

        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self._pixmap_item)

    @property
    def pixmap_item(self):
        return self._pixmap_item

    def set_pixmap(self, pixmap):
        """
        Задать новую картинку
        """
        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self.scene().addItem(self._pixmap_item)
        self.pixmap_item.setPixmap(pixmap)


# ======================================================================================================================

def natural_order(val):  # естественная сортировка
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', val)]


# ======================================================================================================================

# @staticmethod
def AzFileDialog(self, caption=None, last_dir=None, dir_only=False, filter=None, initial_filter=None,
                 save_dir=True, parent=None):
    """ Базовые варианты диалоговых окон """
    settings = AppSettings()  # чтение настроек
    save_dir = settings.read_last_dir()  # вспоминаем прошлый открытый каталог
    if dir_only:
        select_dir = QFileDialog.getExistingDirectory(self, caption, last_dir)
        if select_dir:
            if save_dir:
                settings.write_last_dir(select_dir)
            return select_dir
    else:
        arr = QFileDialog.getOpenFileNames(self, caption, last_dir, filter, initial_filter)
        select_files = arr[0]
        if len(arr[0]) > 0:
            if save_dir:
                settings.write_last_dir(os.path.dirname(select_files[0]))
            return select_files


# ======================================================================================================================


class AzButtonLineEdit(QLineEdit):
    """
    Упрощённая QLineEdit с кнопкой внутри
    """

    def __init__(self, icon_name, color="Black", caption=None, read_only=True, dir_only=False, save_dialog=False,
                 filter=None, save_dir=True, initial_filter=None, on_button_clicked_callback=None, parent=None):
        super(AzButtonLineEdit, self).__init__(parent)
        self.settings = AppSettings()  # чтение настроек
        self.button = QtWidgets.QToolButton(self)  # создаём кнопку
        self.button.setIcon(coloring_icon(icon_name, color))  # устанавливаем иконку
        # принимаем и устанавливаем атрибуты:
        self.on_button_clicked_callback = on_button_clicked_callback
        self.last_dir = self.settings.read_last_dir()  # вспоминаем прошлый открытый каталог
        self.dir_only = dir_only
        self.save_dialog = save_dialog
        self.save_dir = save_dir
        self.caption = caption
        self.filter = filter
        self.initial_filter = initial_filter
        self.setReadOnly(read_only)
        self.button.clicked.connect(self.on_button_clicked)  # соединяем сигнал щелчка
        # self.button.setStyleSheet('border: 0px; padding: 0px;')  # убираем границу и отступы
        self.button.setCursor(QtCore.Qt.PointingHandCursor)  # курсор при наведении на иконку

    def resizeEvent(self, event):
        # для перемещения кнопки в правый угол
        button_size = self.button.sizeHint()
        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frame_width - button_size.width(),
                         (self.rect().bottom() - button_size.height() + 1) / 2)
        super(AzButtonLineEdit, self).resizeEvent(event)

    def on_button_clicked(self):
        self.last_dir = self.settings.read_last_dir()  # обновляем, т.к. могли выполняться действия
        if self.dir_only:  # выбрано "только каталог"
            select_dir = QFileDialog.getExistingDirectory(self, self.caption, self.last_dir)
            if select_dir:
                if self.save_dir:
                    self.settings.write_last_dir(select_dir)
                self.setText(select_dir)
                if self.on_button_clicked_callback:
                    self.on_button_clicked_callback()
        else:
            if self.save_dialog:  # выбрано диалог сохранения файла
                filename, _ = QFileDialog.getSaveFileName(self, self.caption, self.last_dir, self.filter,
                                                          self.initial_filter)
                if self.save_dir:
                    self.settings.write_last_dir(os.path.dirname(filename))
            else:  # значит классический вариант выбора файлов (dir_only=False, save_dialog=False)
                filename, _ = QFileDialog.getOpenFileName(self, self.caption, self.last_dir, self.filter,
                                                          self.initial_filter)
            if len(filename) > 0:  # проверяем в обоих случаях возвращаемый файл
                if self.save_dir:  # сохраняем последний используемый каталог
                    self.settings.write_last_dir(os.path.dirname(filename))
                self.setText(filename)
            if self.on_button_clicked_callback:
                self.on_button_clicked_callback()


# ======================================================================================================================

def coloring_icon(path, color):  # здесь следует учесть, что метод работает с иконками с заливкой черным цветом
    """
    Перекрашивает иконку в заданный цвет, возвращает QIcon
    return: QIcon;
    Работа с svg не проверена
    """
    pixmap = newPixmap(path)  # иконка, которую будем перекрашивать
    mask = pixmap.createMaskFromColor(QColor('black'), QtCore.Qt.MaskOutColor)  # по умолчанию цвет иконок черный
    pixmap.fill(QColor(color))  # меняем цвет иконки...
    pixmap.setMask(mask)  # ...по маске
    return QIcon(pixmap)


# ======================================================================================================================

class AzAction(QtWidgets.QAction):
    """
    Кастомизация QAction, в виде зажимаемой кнопки с переменой цвета иконки, когда она активна
    return: QAction
    """

    def __init__(self, text, path, color_active, color_base="black", parent=None):
        self.icon_default = coloring_icon(path, color_base)
        self.icon_activate = coloring_icon(path, color_active)
        super().__init__(self.icon_default, text, parent)
        self.setCheckable(True)
        self.toggled.connect(self.tog1)

    def toggle(self):
        pass

    def tog1(self):
        if self.isChecked():
            self.setIcon(self.icon_activate)
        else:
            self.setIcon(self.icon_default)
