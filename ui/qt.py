import os.path as osp
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from utils import AppSettings
import os

here = osp.dirname(osp.abspath(__file__))


# ----------------------------------------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------------------------------
def coloring_icon(path, color):
    """
    Перекрашивает иконку в заданный цвет, возвращает QIcon
    return: QIcon;
    Работа с svg не проверена, также следует учесть, что метод работает с иконками с заливкой черным цветом
    """
    pixmap = newPixmap(path)  # иконка, которую будем перекрашивать
    mask = pixmap.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)  # по умолчанию цвет иконок черный
    pixmap.fill(QtGui.QColor(color))  # меняем цвет иконки...
    pixmap.setMask(mask)  # ...по маске
    return QtGui.QIcon(pixmap)


# ----------------------------------------------------------------------------------------------------------------------

def new_icon(icon):
    icons_dir = osp.join(here, "../icons")
    return QtGui.QIcon(osp.join(":/", icons_dir, "%s.png" % icon))


# ----------------------------------------------------------------------------------------------------------------------
def new_act(parent, text, slot=None, shortcut=None, icon=None, color=None, tip=None, checkable=False, enabled=True,
            checked=False):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QtWidgets.QAction(text, parent)
    if icon is not None:
        a.setIconText(text.replace(" ", "\n"))
        a.setIcon(coloring_icon(icon, color))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    a.setChecked(checked)
    return a


# ----------------------------------------------------------------------------------------------------------------------

def newPixmap(path):
    icons_dir = osp.join(here, "../icons")
    return QtGui.QPixmap(osp.join(":/", icons_dir, "%s.png" % path))


# ----------------------------------------------------------------------------------------------------------------------

def new_button(object="pushbutton", text=None, icon=None, color=None, slot=None):
    b = QtWidgets.QPushButton(text)
    if icon is not None:
        b.setIcon(new_icon(icon))
    if slot is not None:
        b.clicked.connect(slot)
    return b


# ----------------------------------------------------------------------------------------------------------------------
def labelValidator():
    return QtGui.QRegExpValidator(QtCore.QRegExp(r"^[^ \t].+"), None)
    # regexp = QtCore.QRegExp(r'^[[:ascii:]]+$')  # проверка имени файла на символы
    # validator = QtGui.QRegExpValidator(regexp, self.slice_output_file_path)  # создаём валидатор
    # self.slice_output_file_path.setValidator(validator)  # применяем его к нашей строке
