from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, save, load
from ui import new_button, coloring_icon, az_file_dialog
import numpy as np
import os

current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/
the_color = UI_COLORS.get("automation_color")
# TODO: добавить код удаления выбранных записей по разметке и самих изображений к ним относящимся

class AutomationUI(QtWidgets.QWidget):
    """
    Класс виджета автоматизации
    """

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        txt = 'Hello, world!\n'
        self.log = QtWidgets.QTextEdit()
        self.log.setText(txt)

        self.button01 = QtWidgets.QPushButton("Get palette")
        self.button02 = QtWidgets.QPushButton("Apply palette")
        main_win = QtWidgets.QMainWindow()
        main_win.setCentralWidget(self.log)

        g_layout = QtWidgets.QGridLayout()
        g_layout.addWidget(self.button01, 0, 0)
        g_layout.addWidget(self.button02, 0, 1)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addLayout(g_layout)
        h_layout.addWidget(main_win)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        layout.addLayout(h_layout)

        self.button01.clicked.connect(self.palette_get)
        self.button02.clicked.connect(self.palette_apply)

    def palette_get(self):  # извлечь и сохранить палитру из проекта SAMA
        papa = self.settings.read_last_dir()
        print("init: " + papa)
        sel_file = az_file_dialog(self, self.tr("Выбрать палитру из файла проекта SAMA *.json"),
                                  self.settings.read_last_dir(), dir_only=False,
                                  filter="SAMA project (*.json)", initial_filter="json (*.json)")

        # if sel_file is None:  # проверки на существование и открытие
        #     return
        # if not os.path.exists(sel_file[0]):
        #     return
        if not self.check_file(sel_file):
            return
        json = load(sel_file[0])
        self.log.append(f"\nВыбран файл: &{sel_file[0]}")
        colors = json["labels_color"]
        data = dict()
        data["labels_color"] = colors
        dict_images = dict()

        file = az_file_dialog(self, self.tr("Сохранение палитры проекта SAMA *.json"), self.settings.read_last_dir(),
                              dir_only=False, file_to_save=True, filter="Palette (*.palette)",
                              initial_filter="palette (*.palette)")
        if len(file[0]) > 0:
            save(file, data, 'w+')  # сохраняем файл как палитру
        self.log.append(f"\nПалитра сохранена: &{file[0]}")

    def palette_apply(self):  # применить палитру к файлу проекта SAMA
        # загружаем файл с палитрой
        sel_file = az_file_dialog(self, self.tr("Выберете палитру *.palette"), self.settings.read_last_dir(),
                                  dir_only=False, filter="Palette (*.palette)", initial_filter="palette (*.palette)")
        if not self.check_file(sel_file):
            return
        self.log.append(f"\nВыбрана палитра: &{sel_file[0]}")
        palette = load(sel_file[0])
        colors = palette["labels_color"]  # выгружаем цвета палитры

        # загружаем файл проекта SAMA
        input_file = az_file_dialog(self, self.tr("Применить палитру к проекту SAMA *.json"),
                                    self.settings.read_last_dir(),
                                    dir_only=False, filter="SAMA project (*.json)", initial_filter="json (*.json)")
        if not self.check_file(input_file):
            return
        json = load(input_file[0])
        input_colors = json["labels_color"]

        # обходим ключи
        for color in input_colors:
            if color in colors:  # такой цвет есть в нашей палитре
                input_colors[color] = colors[color]
        json["labels_color"] = input_colors
        save(input_file[0], json)
        self.log.append(f"\nПалитра применена, файл сохранён: &{input_file[0]}")

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AutomationUI", text)

    def translate_ui(self):
        pass
        # self.tab_widget.setTabText(0, self.tr(self.tab_mnist.name))

    @staticmethod
    def check_file(args):  # двойная проверка на наличие файлов
        if args is None:  # проверка на существование...
            return False
        if not os.path.exists(args[0]):  # ...и открытие
            return False
        return True
