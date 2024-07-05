from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS
import os.path as osp
import os

# Если есть проблема с сигналами, то возможно следует удалить декоратор @QtCore.pyqtSlot()

here = osp.dirname(osp.abspath(__file__))
default_color = UI_COLORS.get("default_color")


# ----------------------------------------------------------------------------------------------------------------------
class AzButtonLineEdit(QtWidgets.QLineEdit):
    """
    Упрощённая QLineEdit с кнопкой внутри: color - цвет, caption - заголовок,
    read_only - возможность изменения строки вручную, dir_only - возвращает только каталог,
    save_dialog - возвращает только файл для сохранения, filter - фильтр типа файлов, initial_filter - то же,
    save_dir - запоминание каталога, в который заходим, on_button_clicked_callback - слот.
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
        self.setContentsMargins(0, 0, 31, 0)
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

class AzInputDialog(QtWidgets.QDialog):
    def __init__(self, parent, num_rows, labels, window_title, has_ok=True, has_cancel=True, ok_text="OK",
                 cancel_text="Cancel"):
        """Кастомизация диалогового окна. В качестве параметров передаются:
           число строк (num_rows), заголовки строк (labels), заголовок окна и допустимые кнопки. Также возможно
           указание кастомных заголовков кнопок "ОК" и "Cancel".
           dialog = AzInputDialog(2, ["age", "stage"], "Your status")
        """
        super().__init__(parent)

        # перечень QLineEdit для ввода
        self.line_edits = []
        self.setMinimumSize(300,100)

        # форма для размещения
        form_layout = QtWidgets.QFormLayout()
        for i in range(num_rows):
            label = QtWidgets.QLabel(labels[i])  # название/метка
            line_edit = QtWidgets.QLineEdit()
            form_layout.addRow(label, line_edit)
            self.line_edits.append(line_edit)  # добавляем всё в перечень

        # настройка кнопок...
        # button_box = QtWidgets.QDialogButtonBox()
        # if has_ok:
        #     ok_button = button_box.addButton(ok_text, QtWidgets.QDialogButtonBox.AcceptRole)
        # if has_cancel:
        #     cancel_button = button_box.addButton(cancel_text, QtWidgets.QDialogButtonBox.RejectRole)
        self.ok_button = QtWidgets.QPushButton(ok_text, self)
        self.cancel_button = QtWidgets.QPushButton(cancel_text, self)

        # ...и компоновка
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addStretch(1)
        if has_ok:
            h_layout.addWidget(self.ok_button)
        if has_cancel:
            h_layout.addWidget(self.cancel_button)
        # layout.addWidget(button_box)
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        # заголовок окна
        self.setWindowTitle(window_title)

        # если кнопки "OK", то идет слот принятия
        # if has_ok:
        #     ok_button.clicked.connect(self.finish)
        #
        # # иначе с отказом
        # if has_cancel:
        #     cancel_button.clicked.connect(self.reject)
        if has_ok:
            self.ok_button.clicked.connect(self.finish)
        if has_cancel:
            self.cancel_button.clicked.connect(self.finish)

    def exec_(self):  # переопределяем запуск диалога
        result = super().exec_()
        data = [line_edit.text() for line_edit in self.line_edits]
        return result, data  # возвращаем нажатую кнопку и данные

    def finish(self):  # переопределяем запуск диалога
        result = super().exec_()
        data = [line_edit.text() for line_edit in self.line_edits]
        return result, data  # возвращаем нажатую кнопку и данные
        self.close


class OkCancelDialog(QtWidgets.QWidget):
    def __init__(self, parent, title, text, on_ok=None, on_cancel=None,
                 ok_text=None, cancel_text=None):

        super().__init__(parent)
        self.settings = AppSettings()
        self.lang = self.settings.read_lang()

        self.setWindowFlag(QtCore.Qt.Tool)

        self.setWindowTitle(title)

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel(text)

        buttons_layout = QtWidgets.QHBoxLayout()

        # Reset text
        if not ok_text:
            ok_text = 'Ок' if self.lang == 'RU' else "OK"
        if not cancel_text:
            cancel_text = 'Отменить' if self.lang == 'RU' else "Cancel"

        self.ok_button = QtWidgets.QPushButton(ok_text, self)
        self.cancel_button = QtWidgets.QPushButton(cancel_text, self)

        if not on_ok:
            self.ok_button.clicked.connect(self.on_ok_clicked)
        else:
            self.ok_button.clicked.connect(on_ok)

        if not on_cancel:
            self.cancel_button.clicked.connect(self.cancel_button_clicked)
        else:
            self.cancel_button.clicked.connect(on_cancel)

        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addWidget(self.label)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.show()

    def on_ok_clicked(self):
        self.close()

    def cancel_button_clicked(self):
        self.close()


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

    def tog1(self):
        if self.isChecked():
            self.setIcon(self.icon_activate)
        else:
            self.setIcon(self.icon_default)


# ----------------------------------------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------------------------------
class AzTableModel(QtCore.QAbstractTableModel):
    """
    Модель для отображения табличных данных, принимает лист листов [[x1, y1], [x2, y2]... ]
    Все методы "перегруженные" для минимального функционала.
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
            self.dataChanged.emit(index, index, [role])
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
            flag |= QtCore.Qt.ItemFlag.ItemIsEditable
            # | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled #
        return flag  # type: ignore

    # def flags(self, index: QtCore.QModelIndex):
    #     flag = super().flags(index)
    #     if self._flags:
    #         for i, _flag in enumerate(self._flags()):
    #             if index.column() == i:
    #                 flag |= _flag
    #     return flag


# ----------------------------------------------------------------------------------------------------------------------

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


# ----------------------------------------------------------------------------------------------------------------------
def coloring_icon(path, color):
    """
    Перекрашивает иконку в заданный цвет, возвращает QIcon
    return: QIcon;
    Работа с svg не проверена, также следует учесть, что метод работает с иконками с заливкой черным цветом
    """
    pixmap = new_pixmap(path)  # иконка, которую будем перекрашивать
    mask = pixmap.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)  # по умолчанию цвет иконок черный
    pixmap.fill(QtGui.QColor(color))  # меняем цвет иконки...
    pixmap.setMask(mask)  # ...по маске
    return QtGui.QIcon(pixmap)


# ----------------------------------------------------------------------------------------------------------------------
def new_icon(icon):
    """Создает и возвращает иконку по её наименованию"""
    icons_dir = osp.join(here, "../icons")
    return QtGui.QIcon(osp.join(":/", icons_dir, "%s.png" % icon))


# ----------------------------------------------------------------------------------------------------------------------
def new_act(parent, text, icon=None, color=None, slot=None, checkable=False, checked=False, enabled=True, shortcut=None,
            tip=None):
    """Create a new action and assign callbacks, shortcuts, etc. Implement LabelME"""
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
def new_pixmap(path):
    """Возвращает иконку из каталога icons по передаваемому имени, расширение 'png' дописывает сама.
    Implement LabelME"""
    icons_dir = osp.join(here, "../icons")
    return QtGui.QPixmap(osp.join(":/", icons_dir, "%s.png" % path))


# ----------------------------------------------------------------------------------------------------------------------
def new_text(parent, text: str = None, text_color: str = None, alignment="l", bald=False):
    """Объект QLabel. Добавление центрированного (alignment = "l", "r", "c") текста (text) с заданным
    цветом (text_color)"""
    label = QtWidgets.QLabel(parent)
    if text is not None:
        label.setText(text)
        if bald:
            label.setText("<b>" + label.text() + "</b>")

    # label.setFrameShape(QtWidgets.QFrame.Box)
    qt_alignment = None  # центрирование текста
    if alignment == "r":
        qt_alignment = QtCore.Qt.AlignmentFlag.AlignRight
    elif alignment == "c":
        qt_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
    else:  # во всех остальных случаях
        qt_alignment = QtCore.Qt.AlignmentFlag.AlignLeft
    label.setAlignment(qt_alignment)
    if text_color is not None:
        label.setStyleSheet("color: " + text_color)
    return label


# ----------------------------------------------------------------------------------------------------------------------
def new_button(parent, obj="pb", text=None, icon=None, color=None, slot=None, checkable=False, checked=False,
               icon_size=None, tooltip=None):
    """
    Создание и настройка кнопки PyQt5 (основа реализована из LabelMe)
    obj (тип кнопки): pb (QPushButton), tb (QToolButton);
    text - надпись; icon - имя иконки из каталога "icons" без расширения; color - цвет; icon_size - размер иконок
    checkable - возможность активации/деактивации; checked - активна/неактивная, если выбрано "checkable"
    tooltip - выплывающая подсказка
    """
    b = None
    if obj == "tb":
        b = QtWidgets.QToolButton(parent)
        if checkable:
            b.setCheckable(checkable)
            b.setChecked(checked)
    elif obj == "pb":
        b = QtWidgets.QPushButton(parent)
    else:
        return None
    if text is not None:
        b.setText(text)
    if icon is not None:
        if color is None:
            color = default_color
        b.setIcon(coloring_icon(icon, color))
    if slot is not None:
        b.clicked.connect(slot)
    if icon_size is not None:
        b.setIconSize(QtCore.QSize(icon_size, icon_size))
    if tooltip is not None:
        b.setToolTip(tooltip)
    return b


# ----------------------------------------------------------------------------------------------------------------------
def labelValidator():
    return QtGui.QRegExpValidator(QtCore.QRegExp(r"^[^ \t].+"), None)
    # regexp = QtCore.QRegExp(r'^[[:ascii:]]+$')  # проверка имени файла на символы
    # validator = QtGui.QRegExpValidator(regexp, self.slice_output_file_path)  # создаём валидатор
    # self.slice_output_file_path.setValidator(validator)  # применяем его к нашей строке


# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
def az_custom_dialog(caption, message, yes=False, no=False, back=False, custom_button=False, custom_text="",
                     parent=None):
    """
    Кастомизация диалоговых окон (вопросы, диалоги)
    Возвращает int: 1 - Да, 2 - Нет, 3 - Назад, 4 - <пользовательский вариант>
    """
    dlg = QtWidgets.QMessageBox(parent)
    dlg.setWindowTitle(caption)
    dlg.setInformativeText(message)
    if yes:
        dlg.addButton("Да", QtWidgets.QMessageBox.ButtonRole.YesRole)
    if no:
        dlg.addButton("Нет", QtWidgets.QMessageBox.ButtonRole.NoRole)
    if back:
        dlg.addButton("Назад", QtWidgets.QMessageBox.ButtonRole.ResetRole)
    if custom_button:
        dlg.addButton(custom_text, QtWidgets.QMessageBox.ButtonRole.ActionRole)
    dlg.exec()
    m = dlg.buttonRole(dlg.clickedButton())
    if m == QtWidgets.QMessageBox.ButtonRole.YesRole:
        return 1
    elif m == QtWidgets.QMessageBox.ButtonRole.NoRole:
        return 2
    elif m == QtWidgets.QMessageBox.ButtonRole.ResetRole:
        return 3
    elif m == QtWidgets.QMessageBox.ButtonRole.ActionRole:
        return 4
    else:
        return -1


# ----------------------------------------------------------------------------------------------------------------------
def az_file_dialog(parent=None, caption=None, last_dir=None, dir_only=False, filter=None, initial_filter=None,
                   remember_dir=True, file_to_save=False):
    """ Базовые варианты диалоговых окон (открыть, сохранить, указать путь и т.п.)"""
    settings = AppSettings()  # чтение настроек
    if not last_dir:  # если исходный каталог не настроен
        last_dir = settings.read_last_dir()  # вспоминаем прошлый открытый каталог
    if dir_only:  # выбрать только каталог
        select_dir = QtWidgets.QFileDialog.getExistingDirectory(parent, caption, last_dir)
        if select_dir:
            if remember_dir:
                settings.write_last_dir(select_dir)
            return select_dir
    else:

        if file_to_save:
            # сохранение файла
            arr = QtWidgets.QFileDialog.getSaveFileName(parent, caption, last_dir, filter, initial_filter)
        else:
            # открытие файла
            arr = QtWidgets.QFileDialog.getOpenFileNames(parent, caption, last_dir, filter, initial_filter)
        select_files = arr[0]
        if len(arr[0]) > 0:
            if remember_dir:
                settings.write_last_dir(os.path.dirname(select_files[0]))
            return select_files


# ----------------------------------------------------------------------------------------------------------------------
def save_via_qtextstream(table_data, path, exclude_columns: list = None):
    """Экспорт и сохранение табличных данных (table_data) в файл (path),
    исключая перечень столбцов указанный в exclude_columns"""

    # Добавить ловлю ошибок при экспорте
    file = QtCore.QFile(path)
    result = False
    if file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text):
        stream = QtCore.QTextStream(file)
        stream.setCodec("UTF-8")

        if exclude_columns is not None:
            for row in range(table_data.rowCount()):
                for col in range(table_data.columnCount()):
                    if col not in exclude_columns:  # пропускаем столбцы из списка исключений
                        item = table_data.item(row, col)
                        if item is not None:
                            stream << item.text() << "\t"
                stream << "\n"
        else:  # если "левых" столбцов нет, то сохраняем таблицу целиком
            for row in range(table_data.rowCount()):
                for col in range(table_data.columnCount()):
                    item = table_data.item(row, col)
                    if item is not None:
                        stream << item.text() << "\t"
                stream << "\n"

        file.close()
        result = True
    return result

# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
