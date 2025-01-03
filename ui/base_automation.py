from PyQt5 import QtCore, QtWidgets, QtGui
from utils import AppSettings, UI_COLORS, helper
from utils import helper
from ui import az_file_dialog
import cv2
import random
import os
from PIL import Image


current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/
the_color = UI_COLORS.get("automation_color")


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
        self.button04 = QtWidgets.QPushButton("Create txt files in dir")

        main_win = QtWidgets.QMainWindow()
        main_win.setCentralWidget(self.log)

        g_layout = QtWidgets.QGridLayout()
        g_layout.addWidget(self.button01, 0, 0)
        g_layout.addWidget(self.button02, 1, 0)
        g_layout.addWidget(self.button03, 2, 0)
        g_layout.addWidget(self.button04, 3, 0)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addLayout(g_layout)
        h_layout.addWidget(main_win)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # уменьшаем границу
        layout.addLayout(h_layout)

        self.button01.clicked.connect(self.palette_get)
        self.button02.clicked.connect(self.palette_apply)
        self.button03.clicked.connect(self.split_images_in_dir)
        self.button04.clicked.connect(self.create_text_files_in_dir)

    def create_text_files_in_dir(self):
        """Создание для изображения пустых текстовых файлов (как дополнительные данные в валидацию при обучении)"""
        sel_dir = az_file_dialog(self, self.tr("Каталог с изображениями, для которых создаются txt"),
                                 self.settings.read_last_dir(), dir_only=True)
        if not os.path.exists(sel_dir):
            return
        # используем только поддерживаемые QImageReader расширения
        types = [".%s" % fmt.data().decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()]
        text_files = []  # перечень возвращаемых изображений
        for root, dirs, files in os.walk(sel_dir):
            for file in files:
                if file.lower().endswith(tuple(types)):
                    relative_path = os.path.normpath(os.path.join(root, os.path.splitext(os.path.basename(file))[0] + ".txt"))
                    text_files.append(relative_path)
            break
        [helper.save_txt(txt, "") for txt in text_files]  # создаем пустышки


    def palette_get(self):
        pass # перемещено в Attrs

    def palette_apply(self):
        """Применить палитру к файлу проекта SAMA"""
        # загружаем файл с палитрой
        sel_file = az_file_dialog(self, self.tr("Выберете палитру *.palette"), self.settings.read_last_dir(),
                                  dir_only=False, filter="Palette (*.palette)", initial_filter="palette (*.palette)")
        if not helper.check_files(sel_file):
            return
        self.log.append(f"\nВыбрана палитра: &{sel_file[0]}")
        palette = helper.load(sel_file[0])
        colors = palette["labels_color"]  # выгружаем цвета палитры

        # загружаем файл проекта SAMA
        input_file = az_file_dialog(self, self.tr("Применить палитру к проекту SAMA *.json"),
                                    self.settings.read_last_dir(),
                                    dir_only=False, filter="SAMA project (*.json)", initial_filter="json (*.json)")
        if not helper.check_files(input_file):
            return
        json = helper.load(input_file[0])
        input_colors = json["labels_color"]

        # обходим ключи
        for color in input_colors:
            if color in colors:  # такой цвет есть в нашей палитре
                input_colors[color] = colors[color]
        json["labels_color"] = input_colors
        helper.save(input_file[0], json)
        self.log.append(f"\nПалитра применена, файл сохранён: &{input_file[0]}")

    def split_images_in_dir(self):
        """Выбор каталог для разрезания случайного количества изображений"""
        sel_dir = az_file_dialog(self, self.tr("Каталог с изображениями"), self.settings.read_last_dir(), dir_only=True)
        if not os.path.exists(sel_dir):
            return

        save_dir = self.settings.read_default_output_dir()
        files_count, ok = QtWidgets.QInputDialog.getText(None, "Количество снимков в каталоге", "Укажите количество:")
        
        if not ok:
            return
        size, ok = QtWidgets.QInputDialog.getText(None, "Размер кадрирования", "Введите размер стороны:")
        
        if not ok:
            return
        # получаем случайные снимки...
        # TODO: не сохранять остатки от нарезки
        random_filenames = self.get_random_files(sel_dir, int(files_count))
        if random_filenames:  # ...и режем их на заданные размеры
            for file in random_filenames:
                self.split_image(file, int(size), int(size), save_dir, False)

    def none(self):
        pass

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AutomationUI", text)

    def translate_ui(self):
        pass
        # self.tab_widget.setTabText(0, self.tr(self.tab_mnist.name))

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
    def split_image(image_path, split_width, split_height, save_path, save_not_full=True):
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

        # флаг сохранять и обрезанные границы
        if save_not_full: # если обрезка имеет остаток - добавляем до заданного размера область черного цвета
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
# ----------------------------------------------------------------------------------------------------------------------

def repear_png_palette(input_path, output_path):
    """Исправляет проблему палитры для файлов иконок PNG"""
    pngs = helper.get_files(input_path, ("png"))
    # path = r"D:\data_prj\labed\labed\icons"
    # out_dir = r"D:\data_prj\labed\labed\new_icons"
    for item in pngs:
        name = os.path.basename(item) # базовое имя с расширением
        
        with Image.open(input_path) as img:
            img.info.pop('icc_profile', None)
            img.save(os.path.join(output_path, name), 'png')

# ----------------------------------------------------------------------------------------------------------------------


import random

# Assume bags is a list of lists, where each sublist contains the counts of each number on the dice in a bag
def balance_dice(bags):
    # Initialize the white and black boxes
    white_box = []
    black_box = []

    # Step 1: Initial Sorting
    for bag in bags:
        if random.random() < 0.5:
            white_box.append(bag)
        else:
            black_box.append(bag)

    def calculate_imbalance(white_box, black_box):
        # Step 2: Calculate Imbalance
        counts_white = [sum(bag.count(i) for bag in white_box) for i in range(1, 7)]
        counts_black = [sum(bag.count(i) for bag in black_box) for i in range(1, 7)]
        imbalance = sum(abs(counts_white[i] - 2/3 * counts_black[i]) for i in range(6))
        return imbalance

    def try_swaps(white_box, black_box):
        # Step 3: Swap Bags
        for i, bag_w in enumerate(white_box):
            for j, bag_b in enumerate(black_box):
                # Try swapping the bags
                white_box_new = white_box[:i] + white_box[i+1:] + [bag_b]
                black_box_new = black_box[:j] + black_box[j+1:] + [bag_w]

                # Step 4: Repeat
                imbalance_new = calculate_imbalance(white_box_new, black_box_new)
                if imbalance_new < imbalance:
                    # If the swap reduces the imbalance, keep it
                    imbalance = imbalance_new
                    white_box = white_box_new
                    black_box = black_box_new

        return white_box, black_box

    # Main loop
    imbalance = calculate_imbalance(white_box, black_box)
    while imbalance > 0:
        white_box, black_box = try_swaps(white_box, black_box)
        imbalance = calculate_imbalance(white_box, black_box)

    return white_box, black_box