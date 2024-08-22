from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, config
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
    last_dir - открытие с указанного места, по умолчанию открытый прошлый каталог "settings.read_last_dir()"
    """

    def __init__(self, icon_name, color="Black", caption=None, read_only=True, dir_only=False, save_dialog=False,
                 filter=None, save_dir=True, initial_filter=None, slot=None, parent=None):
        super(AzButtonLineEdit, self).__init__(parent)
        self.settings = AppSettings()  # чтение настроек
        self.button = QtWidgets.QToolButton(self)  # создаём кнопку
        self.button.setIcon(coloring_icon(icon_name, color))  # устанавливаем иконку
        # принимаем и устанавливаем атрибуты:
        self.slot = slot
        self.last_dir = self.settings.read_last_dir()  # вспоминаем прошлый открытый каталог
        self.dir_only = dir_only
        self.save_dialog = save_dialog
        self.save_dir = save_dir
        self.caption = caption
        self.filter = filter
        self.initial_filter = initial_filter
        self.setReadOnly(read_only)
        self.setContentsMargins(0, 0, 31, 0)  # отступ справа на величину иконки
        self.slot = slot

        # Signals
        self.button.clicked.connect(self.on_button_clicked)  # соединяем сигнал щелчка
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
                if self.slot:
                    self.slot()
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
            if self.slot:
                self.slot()


# ----------------------------------------------------------------------------------------------------------------------


class AzInputDialog(QtWidgets.QDialog):
    def __init__(self, parent, num_rows, labels, window_title, has_ok=True, has_cancel=True, ok_text="OK",
                 cancel_text="Cancel", input_type=[0], combo_inputs=None):
        """
        Кастомизация диалогового окна. В качестве параметров передаются:
        число строк (num_rows), заголовки строк (labels), заголовок окна и допустимые кнопки. Также возможно
        указание кастомных заголовков кнопок "ОК" и "Cancel".
        Тип данных (input_type): 0 - QLineEdit, 1 - QComboBox, и во втором случае данные из (combo_inputs) закладываются
        в combobox. combo_inputs должен передавать лист листов [["mom","dad","grandpa"]["like","like","smells"]]
        dialog = AzInputDialog(self, 2, ["age", "stage"], "Your status")
        """
        super().__init__(parent)
        # заголовок окна
        self.setWindowTitle(window_title)
        self.setWindowFlag(QtCore.Qt.Tool)

        self.inputs = []  # перечень QLineEdit для ввода

        # форма для размещения
        layout = QtWidgets.QVBoxLayout(self)
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addStretch(1)
        form_layout = QtWidgets.QFormLayout()

        for i in range(num_rows):
            label = QtWidgets.QLabel(labels[i])  # название/метка
            if input_type[i] == 1:  # тип QComboBox()
                input_field = QtWidgets.QComboBox()
                if combo_inputs is not None:
                    input_field.addItems(combo_inputs[i])
            else:  # во всех остальных случаях
                input_field = QtWidgets.QLineEdit()  # тип QLineEdit()
            form_layout.addRow(label, input_field)
            self.inputs.append(input_field)  # добавляем всё в перечень

        # настройка кнопок и их сигналов
        if has_ok:
            ok_button = QtWidgets.QPushButton(ok_text)
            ok_button.setMinimumSize(100, config.BUTTON_H)
            ok_button.clicked.connect(self.check_inputs)
            h_layout.addWidget(ok_button)

        if has_cancel:
            cancel_button = QtWidgets.QPushButton(cancel_text)
            cancel_button.setMinimumSize(100, config.BUTTON_H)
            cancel_button.clicked.connect(self.reject)
            h_layout.addWidget(cancel_button)
        layout.addLayout(form_layout)
        layout.addLayout(h_layout)
        self.adjustSize()  # располагаем все виджеты
        self.setFixedSize(self.size())  # закрепляем

    def get_inputs(self):  # возвращаем перечень объектов
        result = []
        for input_field in self.inputs:
            if isinstance(input_field, QtWidgets.QComboBox):
                result.append(input_field.currentText())
            elif isinstance(input_field, QtWidgets.QLineEdit):
                result.append(input_field.text())
        return result

    def check_inputs(self):
        checked = True
        for input_field in self.inputs:
            if isinstance(input_field, QtWidgets.QLineEdit):
                if len(input_field.text()) < 1:
                    checked = False
        if checked:
            self.accept()


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
def new_label_icon(icon_path, the_color, size, ):
    """Возвращает QLabel с объектом иконкой заданного цвета (the_color) и размера (size)"""
    label_icon = QtWidgets.QLabel()
    icon = coloring_icon(icon_path, the_color)
    pixmap = QtGui.QPixmap.fromImage(icon.pixmap(size, size).toImage())
    label_icon.setPixmap(pixmap)
    label_icon.setSizePolicy(size, size)
    return label_icon


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
        qt_alignment = (QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignVCenter)
    elif alignment == "c":
        qt_alignment = (QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignVCenter)
    else:  # во всех остальных случаях
        qt_alignment = (QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignVCenter)
    label.setAlignment(qt_alignment)
    if text_color is not None:
        label.setStyleSheet("color: " + text_color)
    return label


# ----------------------------------------------------------------------------------------------------------------------
def new_button(parent, obj="pb", text=None, icon=None, color=None, slot=None, checkable=False, checked=False,
               icon_size=None, tooltip=None):
    """
    Создание и настройка кнопки PyQt5 (основа реализована из LabelMe)
    obj (тип кнопки): pb (QPushButton), tb (QToolButton); lb (QPushButton) но выглядящая как label
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
    elif obj == "lb":
        b = QtWidgets.QPushButton(parent)
        b.setStyleSheet('''
            QPushButton {
                border: none;
            }
            QPushButton:hover {
                background-color: transparent;
            }
            ''')
    else:
        return None
    if text is not None:
        b.setText(text)
    if icon is not None:
        if color is None:
            b.setIcon(new_icon(icon))
        else:
            b.setIcon(coloring_icon(icon, color))
    if slot is not None:
        b.clicked.connect(slot)
    if icon_size is not None:
        b.setIconSize(QtCore.QSize(icon_size, icon_size))
    if tooltip is not None:
        b.setToolTip(tooltip)
    return b


# ----------------------------------------------------------------------------------------------------------------------
def new_cbx(parent, items=None, edit=False, valid=None):
    """Упрощенная настройка QComboBox: items - список объектов; edit - возможность редактировать, valid - валидатор"""
    cbx = QtWidgets.QComboBox(parent)
    cbx.setEditable(edit)
    if items:
        cbx.addItems(items)
    if valid:
        cbx.setValidator(valid)
    return cbx


# ----------------------------------------------------------------------------------------------------------------------
def labelValidator():
    return QtGui.QRegExpValidator(QtCore.QRegExp(r"^[^ \t].+"), None)
    # regexp = QtCore.QRegExp(r'^[[:ascii:]]+$')  # проверка имени файла на символы
    # validator = QtGui.QRegExpValidator(regexp, self.slice_output_file_path)  # создаём валидатор
    # self.slice_output_file_path.setValidator(validator)  # применяем его к нашей строке


# ----------------------------------------------------------------------------------------------------------------------
def setup_dock_widgets(parent, docks, settings):
    """
    Настройка интерфейса Widget'ов с поддержкой DockWidgets со структурой DockWidget
    Принимает аргументы:
    parent - родитель
    settings - словарь параметров из config.py "widget_name": [ bool, bool, ... ]
        0 - show, 1 - closable, 2 - movable, 3 - floatable, 4 - no_caption, 5 - no_actions
    docks -перечень DockWidgets
    """
    features = QtWidgets.QDockWidget.DockWidgetFeatures()  # features для док-виджетов
    for dock in docks:
        dock_settings = settings.get(dock)  # храним их описание в config.py
        if not dock_settings[0]:  # 0 - show
            getattr(parent, dock).setVisible(False)  # устанавливаем атрибуты напрямую
        if dock_settings[1]:  # 1 - closable
            features = features | QtWidgets.QDockWidget.DockWidgetClosable
        if dock_settings[2]:  # 2 - movable
            features = features | QtWidgets.QDockWidget.DockWidgetMovable
        if dock_settings[3]:  # 3 - floatable
            features = features | QtWidgets.QDockWidget.DockWidgetFloatable
        if dock_settings[4]:  # 4 - no_caption
            getattr(parent, dock).setTitleBarWidget(QtWidgets.QWidget())
        if dock_settings[5]:  # 5 - no_actions - "close"
            getattr(parent, dock).toggleViewAction().setVisible(False)
        getattr(parent, dock).setFeatures(features)  # применяем настроенные атрибуты [1-3]


# ----------------------------------------------------------------------------------------------------------------------
def az_custom_dialog(caption, message, yes=True, no=True, back=False, custom_button=False, custom_text="",
                     parent=None):
    """
    Кастомизация диалоговых окон (вопросы, диалоги)
    Возвращает int: 1 - Да, 2 - Нет, 3 - Назад, 4 - <пользовательский вариант>
    """
    dlg = QtWidgets.QMessageBox(parent)
    dlg.setWindowTitle(caption)
    dlg.setInformativeText(message)
    if yes:
        yes_button = dlg.addButton("Yes", QtWidgets.QMessageBox.ButtonRole.YesRole)
        yes_button.setFixedSize(80, config.BUTTON_H)
    if no:
        no_button = dlg.addButton("No", QtWidgets.QMessageBox.ButtonRole.NoRole)
        no_button.setFixedSize(80, config.BUTTON_H)
    if back:
        back_button = dlg.addButton("Back", QtWidgets.QMessageBox.ButtonRole.ResetRole)
        back_button.setFixedSize(80, config.BUTTON_H)
    if custom_button:
        back_button = dlg.addButton("Back", QtWidgets.QMessageBox.ButtonRole.ResetRole)
        back_button.setFixedSize(80, config.BUTTON_H)
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
            file, _ = QtWidgets.QFileDialog.getSaveFileName(parent, caption, last_dir, filter, initial_filter)
            if len(file) > 1:
                if remember_dir:
                    settings.write_last_dir(os.path.dirname(file))
                return file

        else:
            # открытие файла
            file, _ = QtWidgets.QFileDialog.getOpenFileNames(parent, caption, last_dir, filter, initial_filter)
            if len(file) > 0:
                if remember_dir:
                    settings.write_last_dir(os.path.dirname(file))
                return file


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
def set_margins_recursive(widget, left, top, right, bottom, spacing):
    # устанавливаем значения setContentsMargins для текущего объекта...
    if isinstance(widget, (QtWidgets.QLayout, QtWidgets.QVBoxLayout, QtWidgets.QHBoxLayout, QtWidgets.QGridLayout)):
        widget.setContentsMargins(left, top, right, bottom)
        if hasattr(widget, 'setSpacing'):
            widget.setSpacing(spacing)
        for i in range(widget.layout().count()):  # ...и запускаем рекурсию
            child = widget.itemAt(i).widget()
            if child is not None:
                set_margins_recursive(child, left, top, right, bottom, spacing)

    elif isinstance(widget, (QtWidgets.QWidget, QtWidgets.QGroupBox)):
        widget.setContentsMargins(left, top, right, bottom)
        if hasattr(widget, 'setSpacing'):
            widget.setSpacing(spacing)
        layout = widget.layout()
        if layout:
            layout.setContentsMargins(left, top, right, bottom)
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item is not None:
                    set_margins_recursive(item, left, top, right, bottom, spacing)


# ----------------------------------------------------------------------------------------------------------------------
def set_widgets_and_layouts_margins2(widget, left, top, right, bottom):
    """Установка всем виджетам и компоновщикам отступов. Работает рекурсивно"""
    if isinstance(widget, QtWidgets.QWidget):  # наш тип виджет
        layout = widget.layout()
        if layout is not None:
            layout.setContentsMargins(left, top, right, bottom)
            for i in range(widget.layout().count()):
                # запускаем рекурсию
                set_widgets_and_layouts_margins2(widget.layout().itemAt(i).widget(), left, top, right, bottom)
    elif isinstance(widget, QtWidgets.QLayout):  # наш тип Layout
        for i in range(widget.count()):
            set_widgets_and_layouts_margins2(widget.itemAt(i).widget(), left, top, right, bottom)  # запускаем рекурсию
    elif isinstance(widget, QtWidgets.QSplitter):  # наш тип разделитель
        for i in range(widget.count()):
            set_widgets_and_layouts_margins2(widget.itemAt(i).widget(), left, top, right, bottom)  # запускаем рекурсию


# ----------------------------------------------------------------------------------------------------------------------
def set_widgets_visible(layout, flag):
    """Отключение всех виджетов и компоновщиков. Работает рекурсивно"""
    # TODO: не работает, разобраться

    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget is not None:
            widget.setVisible(flag)
            if isinstance(widget, QtWidgets.QGroupBox) or isinstance(widget, QtWidgets.QWidget):
                set_widgets_visible(widget.layout(), flag)
        elif isinstance(item, QtWidgets.QLayout):
            set_widgets_visible(item, flag)

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
