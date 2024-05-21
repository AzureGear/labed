from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from utils import AppSettings
from ui import newPixmap
import os
import re


# ======================================================================================================================
class _TableModel(QtCore.QAbstractTableModel):  # Реализация qdarktheme
    def __init__(self) -> None:
        super().__init__()
        self._data = [[i * 10 + j for j in range(4)] for i in range(5)]

    def data(self, index: QtCore.QModelIndex, role: int):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == QtCore.Qt.ItemDataRole.CheckStateRole and index.column() == 1:
            return QtCore.Qt.CheckState.Checked if index.row() % 2 == 0 else QtCore.Qt.CheckState.Unchecked
        if role == QtCore.Qt.ItemDataRole.EditRole and index.column() == 2:
            return self._data[index.row()][index.column()]  # pragma: no cover
        return None

    def rowCount(self, index) -> int:  # noqa: N802
        return len(self._data)

    def columnCount(self, index) -> int:  # noqa: N802
        return len(self._data[0])

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        flag = super().flags(index)
        if index.column() == 1:
            flag |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
        elif index.column() in (2, 3):
            flag |= QtCore.Qt.ItemFlag.ItemIsEditable
        return flag  # type: ignore

    def headerData(  # noqa: N802
            self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return ["Normal", "Checkbox", "Spinbox", "LineEdit"][section]
        return section * 100


# ======================================================================================================================

class AzTableModel(QtCore.QAbstractTableModel):
    """
    Модель для отображения табличных данных, принимает лист листов [[x1, y1], [x2, y2]... ]
    """

    def __init__(self, data=None, header_data=None, edit_column=None, parent=None):
        super(AzTableModel, self).__init__()
        self._data = data
        self._header_data = header_data
        if edit_column:
            self.edit_col = edit_column
        if self._data is None:
            self._header_data = [["no data available"]]

    def data(self, index, role):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                return self._data[index.row()][index.column()]
        # if role == QtCore.Qt.ItemDataRole.DisplayRole:
        #     return self._data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if value > 95:
                value = 95
            elif value < 0:
                value = 0
            self._data[index.row()][index.column()] = value
            return True
        return False

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return self._header_data[section]
        return section + 1

    def rowCount(self, index):
        # Количество строк = всего элементов списка списков [[x1, y1], [x2, y2] ... >>[xN, yN]<< ]
        if self._data:
            return len(self._data)
        else:
            return 0

    def columnCount(self, index):
        # Количество столбцов = элементов внутреннего списка [[x1, >>y1<<], [x2, y2] ... [xN, yN]]
        if self._data:
            return len(self._data[0])
        else:
            return 0

    def flags(self, index: QtCore.QModelIndex):
        flag = super().flags(index)
        if index.column() == int(self.edit_col):
            flag |= QtCore.Qt.ItemFlag.ItemIsEditable  # | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        return flag  # type: ignore

    # def flags(self, index: QtCore.QModelIndex):
    #     flag = super().flags(index)
    #     if self._flags:
    #         for i, _flag in enumerate(self._flags()):
    #             if index.column() == i:
    #                 flag |= _flag
    #     return flag


# ======================================================================================================================

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
        select_dir = QtWidgets.QFileDialog.getExistingDirectory(self, caption, last_dir)
        if select_dir:
            if save_dir:
                settings.write_last_dir(select_dir)
            return select_dir
    else:
        arr = QtWidgets.QFileDialog.getOpenFileNames(self, caption, last_dir, filter, initial_filter)
        select_files = arr[0]
        if len(arr[0]) > 0:
            if save_dir:
                settings.write_last_dir(os.path.dirname(select_files[0]))
            return select_files


# ======================================================================================================================

class AzSpinBox(QtWidgets.QSpinBox):
    """
    Упрощённая реализация числового виджета
    """

    def __init__(self, min_val=1, max_val=1280, step=8, max_start_val=True, start_val=1, min_wide=40, prefix=None,
                 suffix=None, parent=None):
        super(AzSpinBox, self).__init__(parent)
        self.setMinimum(min_val)
        self.setMaximum(max_val)
        self.setSingleStep(step)
        self.setAccelerated(True)
        if max_start_val:
            self.setValue(self.maximum())
        else:
            self.setValue(start_val)
        self.setMinimumWidth(min_wide)
        if suffix is not None:
            self.setSuffix(suffix)
        if prefix is not None:
            self.setPrefix(prefix)


# ======================================================================================================================

class AzButtonLineEdit(QtWidgets.QLineEdit):
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
            select_dir = QtWidgets.QFileDialog.getExistingDirectory(self, self.caption, self.last_dir)
            if select_dir:
                if self.save_dir:
                    self.settings.write_last_dir(select_dir)
                self.setText(select_dir)
                if self.on_button_clicked_callback:
                    self.on_button_clicked_callback()
        else:
            if self.save_dialog:  # выбрано диалог сохранения файла
                filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.caption, self.last_dir, self.filter,
                                                                    self.initial_filter)
                if self.save_dir:
                    self.settings.write_last_dir(os.path.dirname(filename))
            else:  # значит классический вариант выбора файлов (dir_only=False, save_dialog=False)
                filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.caption, self.last_dir, self.filter,
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
    mask = pixmap.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)  # по умолчанию цвет иконок черный
    pixmap.fill(QtGui.QColor(color))  # меняем цвет иконки...
    pixmap.setMask(mask)  # ...по маске
    return QtGui.QIcon(pixmap)


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
