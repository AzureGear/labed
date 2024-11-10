from PyQt5 import QtWidgets, QtGui, QtCore
from utils.sama_project_handler import DatasetSAMAHandler
from utils import helper
import numpy as np
import cv2
import os


class AzCalcStdMean(QtWidgets.QDialog):
    """
    Диалоговое окно раcчета средних значений и СКО яркости по 3 каналам изображений в датасете. Принимает либо путь
    Рассчитывать для всех изображений в каталоге
    """

    def __init__(self, prj_file):
        super().__init__()
        self.prj_file = prj_file
        self.flag_all_from_dir = False  # флага
        self.std_dataset = None  # выходное СКО яркости датасета для каждого канала
        # выходное среднее значение яркости датасета для каждого канала
        self.mean_dataset = None

        self.setWindowTitle(
            self.tr("Calculate mean and Std for channels of dataset images"))
        # фиксированные размеры для размещения кастомных виджетов
        self.setFixedSize(350, 150)
        self.setWindowFlag(QtCore.Qt.WindowType.Tool)

        self.setup_ui()

        self.sama_data = DatasetSAMAHandler()
        self.sama_data.load(self.prj_file)

        if not self.sama_data.is_correct_file:
            self.pb_recalc.setEnabled(False)
            self.pb_save.setEnabled(False)
            self.images_label.setText(
                self.tr("Current project file is not correct."))
            self.images_count.setText("")
        else:
            self.images_count.setText("0/" + str(self.sama_data.get_images_num()))
            self.calc_mean_std_dataset_channels(self.get_images_list_for_calc()) # расчет значений

        self.rb_images_from_dir.clicked.connect(self.change_calc_source)
        self.pb_recalc.clicked.connect(self.recalc)

    def get_images_list_for_calc(self):
        if self.flag_all_from_dir: # использовать все изображения из каталога
            path_dir = self.sama_data.get_image_path()
            images = [image for image in os.listdir(path_dir) if helper.check_ext(image)]
        
        else:
            images = self.sama_data.get_images_list()  # использовать только изображения из проекта
            
        return images            

    @staticmethod
    def calc_mean_std_dataset_channels(images_list):
        print(images_list)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.rb_images_prj_only = QtWidgets.QRadioButton(
            self.tr("Images from project only"))
        self.rb_images_from_dir = QtWidgets.QRadioButton(
            self.tr("All images in the project 'image path' variable"))
        self.rb_images_prj_only.setChecked(True)

        # Создаем метку для отображения выбранного переключателя
        self.images_label = QtWidgets.QLabel(self.tr("Images: "))
        self.images_count = QtWidgets.QLabel("0/0")
        h_lay_images = QtWidgets.QHBoxLayout()
        h_lay_images.addWidget(self.images_label)
        h_lay_images.addWidget(self.images_count)
        h_lay_images.addStretch(1)

        # Создаем кнопку для подтверждения выбора
        self.pb_recalc = QtWidgets.QPushButton(self.tr("Recalculate"))
        self.pb_save = QtWidgets.QPushButton(
            self.tr("Write results to project"))
        h_lay_buttons = QtWidgets.QHBoxLayout()
        h_lay_buttons.addStretch(1)
        h_lay_buttons.addWidget(self.pb_recalc)
        h_lay_buttons.addWidget(self.pb_save)

        self.result = QtWidgets.QLineEdit()
        self.result.setReadOnly(True)

        layout.addWidget(self.rb_images_prj_only)
        layout.addWidget(self.rb_images_from_dir)
        layout.addLayout(h_lay_images)
        layout.addWidget(self.result)
        layout.addLayout(h_lay_buttons)

    def change_calc_source(self):
        if self.rb_images_from_dir.isChecked:
            self.flag_all_from_dir = False
        elif self.rb_images_prj_only.isChecked:
            self.flag_all_from_dir = True

    def recalc(self):
        img_names = [image for image in os.listdir(
            path_dir) if helper.check_ext(image)]
        mean = np.zeros(3)  # mean in (0,1,2) channels
        std = np.zeros(3)

        for i in range(len(img_names)):
            im_name = img_names[i]
            im = cv2.imread(os.path.join(path_dir, im_name))
            m, s = cv2.meanStdDev(im)
            for channel in range(3):
                mean[channel] = mean[channel] * \
                    (1.0 - (1.0 / (i + 1))) + m[channel] / (i + 1)
                std[channel] = std[channel] * \
                    (1.0 - (1.0 / (i + 1))) + s[channel] / (i + 1)

    def translate_ui(self):
        # Processing - Attributes - Calc Mean Std for Dataset Dialog
        self.setWindowTitle(
            self.tr("Calculate mean and Std for channels of dataset images"))
        self.rb_images_prj_only.setText(self.tr("Images from project only"))
        self.rb_images_from_dir.setText(
            self.tr("All images in the project 'image path' variable"))
        self.pb_recalc.setText(self.tr("Recalculate"))
        self.pb_save.setText(self.tr("Write results to project"))
        self.images_label.setText(self.tr("Images:"))

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzCalcStdMean", text)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = AzCalcStdMean(
        "D:/data_sets/uranium enrichment/anno_json_r1024/anno_sama_r1024.json")
    window.show()
    sys.exit(app.exec_())
