from PyQt5 import QtWidgets, QtGui, QtCore
from utils.sama_project_handler import DatasetSAMAHandler
from utils import helper
from enum import Enum
import numpy as np
import cv2
import os


class SourceCalcState(Enum):
    """
    Источник для расчета значений
    """
    user_dir = 0  # изображения из пользовательского каталога
    image_path = 1  # изображения из каталога "image path"
    project_only = 2  # изображения из проекта


class AzCalcStdMean(QtWidgets.QDialog):
    """
    Диалоговое окно раcчета средних значений и СКО яркости по 3 каналам изображений в датасете. Принимает либо путь
    Рассчитывать для всех изображений в каталоге
    """

    def __init__(self, prj_file, input_type=1, user_dir_or_file=None):
        super().__init__()
        self.prj_file = prj_file
        self.user_path = user_dir_or_file  # пользовательский файл, либо каталог
        self.input_type = input_type  # с поддержкой файла проекта
        self.std_dataset = None  # выходное СКО яркости датасета для каждого канала
        # выходное среднее значение яркости датасета для каждого канала
        self.mean_dataset = None
        self.current_calc_source = None  # текущий источник изображений
        self.current_image_list = None

        # фиксированные размеры для размещения кастомных виджетов
        self.setFixedSize(350, 150)
        self.setWindowFlag(QtCore.Qt.WindowType.Tool)

        self.setup_ui()

        if self.input_type == 1:  # интерфейс с поддержкой sama_data
            self.setWindowTitle(self.tr("Calculate mean and Std for channels of dataset images"))
            self.sama_data = DatasetSAMAHandler()
            self.sama_data.load(self.prj_file)
            self.check_sama_data()

        else:  # интерфейс для выбора пользовательского каталога
            self.setWindowTitle(self.tr("Calculate mean and Std for channels of user path"))
            self.current_calc_source = SourceCalcState.user_dir

        self.get_image_list(self.current_calc_source)

        # Signals
        self.pb_calc.clicked.connect(self.recalc)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        if self.input_type == 1:
            self.rb_images_prj_only = QtWidgets.QRadioButton(
                self.tr("Images from project only"))
            self.rb_images_from_dir = QtWidgets.QRadioButton(
                self.tr("All images in the project 'image path' variable"))
            self.rb_images_prj_only.setChecked(True)
            self.current_calc_source = SourceCalcState.project_only

        # Создаем метку для отображения выбранного переключателя
        self.images_label = QtWidgets.QLabel(self.tr("Images: "))
        self.images_count = QtWidgets.QLabel("0/0")
        h_lay_images = QtWidgets.QHBoxLayout()
        h_lay_images.addWidget(self.images_label)
        h_lay_images.addWidget(self.images_count)
        h_lay_images.addStretch(1)

        # Создаем кнопку для подтверждения выбора
        self.pb_calc = QtWidgets.QPushButton(self.tr("Calculate"))
        self.pb_save = QtWidgets.QPushButton(
            self.tr("Write results to project"))
        h_lay_buttons = QtWidgets.QHBoxLayout()
        h_lay_buttons.addStretch(1)
        h_lay_buttons.addWidget(self.pb_calc)
        h_lay_buttons.addWidget(self.pb_save)

        self.result = QtWidgets.QLineEdit()
        self.result.setReadOnly(True)

        if self.input_type == 1:
            layout.addWidget(self.rb_images_prj_only)
            layout.addWidget(self.rb_images_from_dir)
            # смена на каталог
            self.rb_images_from_dir.clicked.connect(lambda: self.change_calc_source(SourceCalcState.image_path))
            # смена на проект
            self.rb_images_prj_only.clicked.connect(lambda: self.change_calc_source(SourceCalcState.project_only))
        layout.addLayout(h_lay_images)
        layout.addWidget(self.result)
        layout.addLayout(h_lay_buttons)

    def check_sama_data(self):
        if not self.sama_data.is_correct_file:
            self.pb_calc.setEnabled(False)
            self.pb_save.setEnabled(False)
            self.images_label.setText(
                self.tr("Current project file is not correct."))
            self.images_count.setText("")

    def get_image_list(self, calc_source):
        self.current_image_list = None
        # Тип источника для расчета - только изображения проекта
        if calc_source == SourceCalcState.project_only:
            self.check_sama_data()
            self.images_count.setText("0/" + str(self.sama_data.get_images_num()))
            img_path = self.sama_data.get_image_path()
            img_names = [os.path.join(img_path, image) for image in self.sama_data.get_images_list()]

        # Тип источника для расчета - все изображения из 'image_path' проекта
        elif calc_source == SourceCalcState.image_path:
            self.check_sama_data()
            img_path = self.sama_data.get_image_path()
            img_names = [os.path.join(img_path, image) for image in os.listdir(img_path) if helper.check_ext(image)]
            self.images_count.setText("0/" + str(len(img_names)))

        # Тип источника для расчета - пользовательский путь
        elif calc_source == SourceCalcState.user_dir:
            if not helper.check_file(self.user_path):
                self.images_label.setText(self.tr("User path is not correct."))
                self.images_count.setText("")
                return

            # либо это путь к файлу изображения
            if helper.check_ext(self.user_path):
                self.images_count.setText("0/1")  # одно изображение
                img_names = [self.user_path]

            # либо это путь к каталогу
            else:
                img_names = [os.path.join(self.user_path, image) for image in os.listdir(self.user_path) if
                             helper.check_ext(image)]
                self.images_count.setText("0/" + str(len(img_names)))

        self.current_image_list = img_names

    def change_calc_source(self, source_signal):
        if self.current_calc_source == source_signal:
            return
        else:
            self.current_calc_source = source_signal
        self.clear_calc()
        self.get_image_list(self.current_calc_source)

    @staticmethod
    def calc_mean_std_dataset_channels(images_list):
        """image_list - входной перечень изображений для которых рассчитывается mean, std"""
        mean = np.zeros(3)  # mean in (0,1,2) channels
        std = np.zeros(3)

        for i, image in enumerate(images_list):
            # im_name = img_names[i]
            im = cv2.imread(image)
            m, s = cv2.meanStdDev(im)
            for channel in range(3):
                mean[channel] = mean[channel] * (1.0 - (1.0 / (i + 1))) + m[channel] / (i + 1)
                std[channel] = std[channel] * (1.0 - (1.0 / (i + 1))) + s[channel] / (i + 1)

        return mean, std


    def clear_calc(self):
        self.result.clear()

    def recalc(self):
        # расчет значений
        mean, std = self.calc_mean_std_dataset_channels(self.current_image_list)
        self.mean_dataset = np.round(mean, 3)
        self.std_dataset = np.round(std, 3)
        self.result.setText(f"mean: {self.mean_dataset}, std: {self.std_dataset}")

    def translate_ui(self):
        # Processing - Attributes - Calc Mean Std for Dataset Dialog
        self.setWindowTitle(
            self.tr("Calculate mean and Std for channels of dataset images"))
        self.rb_images_prj_only.setText(self.tr("Images from project only"))
        self.rb_images_from_dir.setText(
            self.tr("All images in the project 'image path' variable"))
        self.pb_calc.setText(self.tr("Recalculate"))
        self.pb_save.setText(self.tr("Write results to project"))
        self.images_label.setText(self.tr("Images:"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzCalcStdMean", text)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AzCalcStdMean(
        "D:/data_sets/uranium enrichment/data/anno_json_r1024/anno_sama_r1024.json")
    window.show()
    sys.exit(app.exec_())
