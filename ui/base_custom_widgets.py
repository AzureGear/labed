from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLineEdit
from utils.settings_handler import AppSettings


class EditWithButton(QWidget):  ## Реализация Романа Хабарова
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
            self.setWindowFlag(Qt.Tool)

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

class ButtonLineEdit(QtWidgets.QLineEdit):  # упрощённая QLineEdit с кнопкой внутри

    def __init__(self, icon_file, caption=None, editable=True, parent=None, dir_only=False,
                 on_button_clicked_callback=None):
        super(ButtonLineEdit, self).__init__(parent)
        self.settings = AppSettings()  # чтение настроек
        self.last_dir = self.settings.read_last_dir()  # вспоминаем прошлый открытый каталог
        self.button = QtWidgets.QToolButton(self)  # создаём кнопку
        self.button.setIcon(QtGui.QIcon(icon_file))  # устанавливаем иконку
        # принимаем и устанавливаем атрибуты:
        self.on_button_clicked_callback = on_button_clicked_callback
        self.dir_only = dir_only
        self.caption = caption
        self.setReadOnly(editable)
        self.button.clicked.connect(self.on_button_clicked)  # соединяем сигнал щелчка
        # self.button.setStyleSheet('border: 0px; padding: 0px;')  # убираем границу и отступы
        self.button.setCursor(QtCore.Qt.PointingHandCursor)  # курсор при наведении на иконку

    def resizeEvent(self, event):
        # для перемещения кнопки в правый угол
        button_size = self.button.sizeHint()
        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frame_width - button_size.width(),
                         (self.rect().bottom() - button_size.height() + 1) / 2)
        super(ButtonLineEdit, self).resizeEvent(event)

    def on_button_clicked(self):
        if self.dir_only:
            select_dir = QFileDialog.getExistingDirectory(self, self.caption, self.last_dir)
            if select_dir:
                self.settings.write_last_dir(select_dir)
                self.setText(select_dir)
                if self.on_button_clicked_callback:
                    self.on_button_clicked_callback()
