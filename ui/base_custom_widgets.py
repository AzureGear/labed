from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QColor
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLineEdit
from utils import AppSettings
from ui import newPixmap
import os


class AzImageViewer(QtWidgets.QGraphicsView):  # Реализация Романа Хабарова
    """
    Виджет для отображения изображений *.jpg, *.png и т.д.
    """

    def __init__(self, parent=None, active_color=None, fat_point_color=None, on_rubber_band_mode=None):
        """
        active_color - цвет активного полигона, по умолчанию config.ACTIVE_COLOR
        fat_point_color - цвет узлов активного полигона, по умолчанию config.FAT_POINT_COLOR
        """

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
        # scene = QtWidgets.QGraphicsScene(self)
        # self.setScene(scene)
        # self.scene().clear()

        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self.scene().addItem(self._pixmap_item)
        self.pixmap_item.setPixmap(pixmap)
        #
        # self.init_objects_and_params()
        #
        # self.set_fat_width()
        # self.set_pens()
        # self.remove_fat_point_from_scene()
        # self.clear_ai_points()
        #
        # self.active_group = ActiveHandler([])
        # self.active_group.set_brush_pen_line_width(self.active_brush, self.active_pen, self.line_width)
        #
        # # Ruler items clear:
        # self.on_ruler_mode_off()
        #
        # if self.view_state == ViewState.rubber_band:
        #     self.on_rb_mode_change(False)


# ======================================================================================================================
class EditWithButton(QWidget):  # Реализация Романа Хабарова
    def __init__(self, parent, in_separate_window=False, on_button_clicked_callback=None,
                 is_dir=False, file_type='txt',
                 dialog_text='Открытие файла', placeholder=None, title=None,
                 is_existing_file_only=True):
        """
        Поле Edit с кнопкой
        """
        super().__init__(parent)
        self.settings = AppSettings()
        last_dir = self.settings.read_last_dir()

        if in_separate_window:
            self.setWindowFlag(QtCore.Qt.Tool)

        if title:
            self.setWindowTitle(title)

        self.is_dir = is_dir
        self.file_type = file_type
        self.on_button_clicked_callback = on_button_clicked_callback
        self.dialog_text = dialog_text
        self.start_folder = last_dir
        self.is_existing_file_only = is_existing_file_only

        layout = QHBoxLayout()

        self.edit = QLineEdit()
        if placeholder:
            self.edit.setPlaceholderText(placeholder)
        self.button = QPushButton()

        self.icon_folder = os.path.join(os.path.dirname(__file__), "..", "icons", "glyph_folder.png")

        self.button.setIcon(QIcon(self.icon_folder))

        self.button.clicked.connect(self.on_button_clicked)

        layout.addWidget(self.edit)
        self.edit_height = self.edit.height() - 12
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setPlaceholderText(self, placeholder):
        self.edit.setPlaceholderText(placeholder)

    def getEditText(self):
        return self.edit.text()

    def showEvent(self, event):
        self.button.setMaximumHeight(max(self.edit_height, self.edit.height()))

    def on_button_clicked(self):

        if self.is_dir:
            dir_ = QFileDialog.getExistingDirectory(self,
                                                    self.dialog_text)
            if dir_:
                # self.settings.write_last_opened_path(dir_)
                self.edit.setText(dir_)
                if self.on_button_clicked_callback:
                    self.on_button_clicked_callback()

        else:

            if self.is_existing_file_only:
                file_name, _ = QFileDialog.getOpenFileName(self,
                                                           self.dialog_text,
                                                           self.start_folder,
                                                           f'{self.file_type} File (*.{self.file_type})')

            else:
                file_name, _ = QFileDialog.getSaveFileName(self,
                                                           self.dialog_text,
                                                           self.start_folder,
                                                           f'{self.file_type} File (*.{self.file_type})')
            if file_name:
                # self.settings.write_last_opened_path(os.path.dirname(file_name))
                self.edit.setText(file_name)
                if self.on_button_clicked_callback:
                    self.on_button_clicked_callback()


# ======================================================================================================================

# @staticmethod
def AzFileDialog(self, caption=None, last_dir=None, dir_only=False, parent=None):
    if dir_only:
        select_dir = QFileDialog.getExistingDirectory(self, caption, last_dir)
        if select_dir:
            return select_dir


class AzButtonLineEdit(QLineEdit):
    """
    Упрощённая QLineEdit с кнопкой внутри
    """

    def __init__(self, icon_name, color="Black", caption=None, read_only=True, parent=None, dir_only=False,
                 on_button_clicked_callback=None):
        super(AzButtonLineEdit, self).__init__(parent)
        self.settings = AppSettings()  # чтение настроек
        self.last_dir = self.settings.read_last_dir()  # вспоминаем прошлый открытый каталог
        self.button = QtWidgets.QToolButton(self)  # создаём кнопку
        self.button.setIcon(coloring_icon(icon_name, color))  # устанавливаем иконку
        # принимаем и устанавливаем атрибуты:
        self.on_button_clicked_callback = on_button_clicked_callback
        self.dir_only = dir_only
        self.caption = caption
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
        if self.dir_only:
            select_dir = QFileDialog.getExistingDirectory(self, self.caption, self.last_dir)
            if select_dir:
                self.settings.write_last_dir(select_dir)
                self.setText(select_dir)
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
