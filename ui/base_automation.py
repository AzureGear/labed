from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, save, load
from ui import new_button, coloring_icon, az_file_dialog
import cv2
import random
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
        self.button03 = QtWidgets.QPushButton("Cut images in dir")
        self.button04 = QtWidgets.QPushButton("--- NONE ----")

        main_win = QtWidgets.QMainWindow()
        main_win.setCentralWidget(self.log)

        g_layout = QtWidgets.QGridLayout()
        g_layout.addWidget(self.button01, 0, 0)
        g_layout.addWidget(self.button02, 0, 1)
        g_layout.addWidget(self.button03, 1, 0)
        g_layout.addWidget(self.button04, 1, 1)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addLayout(g_layout)
        h_layout.addWidget(main_win)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        layout.addLayout(h_layout)

        self.button01.clicked.connect(self.palette_get)
        self.button02.clicked.connect(self.palette_apply)
        self.button03.clicked.connect(self.split_images_in_dir)
        self.button04.clicked.connect(self.none)

    def palette_get(self):
        """Извлечь и сохранить палитру из проекта SAMA"""
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
        if len(file) > 0:
            save(file, data, 'w+')  # сохраняем файл как палитру
        self.log.append(f"\nПалитра сохранена: &{file}")

    def palette_apply(self):
        """Применить палитру к файлу проекта SAMA"""
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

    def split_images_in_dir(self):
        """Выбор каталог для разрезания случайного количества изображений"""
        sel_dir = az_file_dialog(self, self.tr("Каталог с изображениями"), self.settings.read_last_dir(), dir_only=True)
        if not os.path.exists(sel_dir):
            return
        # dir = "d:/data_sets/nuclear_power_stations/"
        save = self.settings.read_default_output_dir()
        files_count, ok = QtWidgets.QInputDialog.getText(None, "Количество снимков в каталоге", "Укажите количество:")
        if not ok:
            return
        size, ok = QtWidgets.QInputDialog.getText(None, "Размер кадрирования", "Введите размер стороны:")
        if not ok:
            return
        # получаем случайные снимки...
        random_filenames = self.get_random_files(sel_dir, int(files_count))
        if random_filenames:  # ...и режем их на заданные размеры
            for file in random_filenames:
                self.split_image(file, int(size), int(size), save)

    def none(self):
        pass

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

    @staticmethod
    def get_random_files(dir, count: int, images=True, files_exts=None):
        """
        Возвращает указанное (count) количество случайных файлов, взятых из каталога (directory).
        Дополнительно можно указать разрешение files_exts[], либо флаг images, который указывает расширения изображений.
        """
        if not os.path.exists(dir):
            # переданного каталога не существует
            return None
        image_filenames = []
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
        if images:
            files_exts = image_extensions

        # перечень всех изображений в каталоге
        for filename in os.listdir(dir):
            ext = os.path.splitext(filename)[-1].lower()
            if ext in files_exts:
                image_filenames.append(os.path.join(dir, filename))

        # Возвращаем count случайных имён файлов
        return random.sample(image_filenames, count)

    @staticmethod
    def split_image(image_path, split_width, split_height, save_path):
        """
        Разбивка изображения (image_path) заданного размера w x h (width, height) в каталог (save_path).
        split_image("d:/data_sets/test.jpg", 200, 200 "d:/output")
        """
        img = cv2.imread(image_path)  # читаем изображение
        width, height, _ = img.shape
        tile_width = split_width
        tile_height = split_height
        count = 0  # счётчик
        filename = os.path.splitext(os.path.basename(image_path))[0]
        # если обрезка имеет остаток - добавляем до заданного размера область черного цвета
        pad_width = tile_width - (width % tile_width) if width % tile_width else 0
        pad_height = tile_height - (height % tile_height) if height % tile_height else 0

        img = cv2.copyMakeBorder(img, 0, pad_height, 0, pad_width, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        width, height, _ = img.shape

        for i in range(0, width, tile_width):
            for j in range(0, height, tile_height):
                tile = img[j:j + tile_height, i:i + tile_width]

                # Сохраняем фрагмент изображения
                if tile.size > 0:
                    name = filename + "_{:0>4}.jpg".format(count)
                    tile_path = os.path.join(save_path, name)
                    cv2.imwrite(tile_path, tile)
                    count += 1
