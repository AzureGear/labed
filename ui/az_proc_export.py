import datetime

from PyQt5 import QtWidgets, QtGui, QtCore
from utils import UI_COLORS, config, AppSettings
from utils.sama_project_handler import DatasetSAMAHandler
from ui import new_button, new_cbx, new_text, AzButtonLineEdit
from datetime import datetime
from rasterio import features
from shapely import Polygon
import numpy as np
from PIL import Image
import shutil
import cv2
import os

the_color = UI_COLORS.get("processing_color")


# TODO: доделать интерфейс

# ----------------------------------------------------------------------------------------------------------------------
class AzExportDialog(QtWidgets.QDialog):
    """
    Диалоговое окно для экспорта данных. Использованы реализации экспорта Романа Хабарова
    sama_data - объект класса DatasetSAMAHandler файла проекта SAMA
    data - отсортированные данные по выборкам, например:
        {'train': ['02_GBR_2015.jpg', '03_DEU_2022.jpg'],
        'val': ['03_DEU_2023.jpg', '03_DEU_2020.jpg', '03_DEU_2022.jpg'],
        'test': []}
    """

    def __init__(self, sama_data, split_data, window_title="Export dataset", parent=None):
        super().__init__(parent)
        self.settings = AppSettings()  # настройки программы
        self.setWindowTitle(window_title)
        self.setFixedSize(600, 150)  # фиксированные размеры для размещения кастомных виджетов
        self.setWindowFlag(QtCore.Qt.WindowType.Tool)
        self.sama_data = sama_data  # исходный проект SAMA
        self.split_data = split_data  # отсортированные данные
        self.export_complete = False
        self.setup_ui()

        # Поток для экспорта
        self.export_worker = Exporter(self.sama_data, export_dir=self.output_dir.text(), split_data=self.split_data,
                                      format=self.format_cbx.currentText(), dataset_name="dataset")

        # Сигналы
        self.export_worker.signal_percent_conn.connect(self.worker_percent_change)
        self.export_worker.started.connect(lambda: self.switch_buttons(False))
        self.export_worker.finished.connect(self.finish)

    def setup_ui(self):
        """Настройка интерфейса"""
        # Создаем кнопки
        self.button_cancel = new_button(self, "pb", self.tr("Close"), slot=self.reject)
        self.button_ok = new_button(self, "pb", self.tr("Export"), slot=self.exec_export)

        self.format_cbx = new_cbx(self, config.UI_AZ_EXPORT_TYPES)  # формат выходных данных
        self.format_label = new_text(self, self.tr("Output format:"))

        self.output_dir_label = new_text(self, self.tr("Output dir:"))
        self.output_dir = AzButtonLineEdit("glyph_folder", the_color, self.tr("Select dir"), True, dir_only=True,
                                           save_dialog=True, parent=self)
        self.output_dir.setText(self.settings.read_default_output_dir())  # по умолчанию выходной каталог из настроек

        self.split_info_label = new_text(self, self.tr("Split settings:"))
        self.split_info = new_text(self, "TADA!")

        self.button_cancel.setMinimumWidth(100)
        self.button_ok.setMinimumWidth(100)
        button_layout = QtWidgets.QHBoxLayout()  # компоновщик для кнопок
        button_layout.addStretch(1)
        button_layout.addWidget(self.button_ok)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.button_cancel)

        self.layout = QtWidgets.QFormLayout()  # основной компоновщик вида QFormLayout
        self.layout.addRow(self.output_dir_label, self.output_dir)
        self.layout.addRow(self.format_label, self.format_cbx)
        self.layout.addRow(self.split_info_label, self.split_info)
        self.layout.addItem(button_layout)
        self.setLayout(self.layout)

    @QtCore.pyqtSlot(int)
    def worker_percent_change(self, val):
        # заглушка под индикатор прогресса
        if val == 100:
            self.export_complete = True

    def switch_buttons(self, flag):
        self.button_ok.setEnabled(flag)
        self.button_cancel.setEnabled(flag)

    def finish(self):
        self.switch_buttons(True)
        self.accept()

    def exec_export(self):
        """Выполнение сортировки"""
        self.export_worker.export_dir = self.output_dir.text()
        self.export_worker.format = self.format_cbx.currentText()
        if not self.export_worker.isRunning():
            self.export_worker.start()

    def tr(self, text):
        return QtCore.QCoreApplication.translate("AzExportDialog", text)

    def translate_ui(self):  # переводим диалог
        # Processing - Attributes - Export Dialog
        self.format_label.setText(self.tr("Output format:"))
        self.output_dir_label.setText(self.tr("Output dir:"))
        self.split_info_label.setText(self.tr("Split settings:"))
        self.button_cancel.setText(self.tr("Close"))
        self.button_ok.setText(self.tr("Export"))


# ----------------------------------------------------------------------------------------------------------------------
class Exporter(QtCore.QThread):
    """Экспортер данных. Реализация Романа Хабарова
        Az+: splits не используется, т.к. передаются уже отсортированные выборки train, val, test (split_data)"""

    signal_percent_conn = QtCore.pyqtSignal(int)

    def __init__(self, project_data, export_dir, format='yolo_seg', export_map=None, dataset_name='dataset',
                 variant_idx=0, splits=None, split_method='names', sim='random',
                 is_filter_null=False, new_image_size=None, split_data=None):
        """
        0 - Train/Val/Test
        1 - Train/Val
        2 - Only Train
        3 - Only Val
        4 - Only Test

        format - формат экспорта. Варианты: "yolo_seg", "yolo_box", "coco", "mm_seg"
                        0 - "YOLO Seg", 1 - "YOLO Box", 2 - 'COCO', 3 - 'MM Segmentation'

        """
        super(Exporter, self).__init__()

        # SIGNALS
        self.export_percent_conn = self.signal_percent_conn
        # self.info_conn = InfoConnection()
        # self.err_conn = ErrorConnection()

        self.export_dir = export_dir
        self.format = format
        self.export_map = export_map
        self.dataset_name = dataset_name

        self.variant_idx = variant_idx
        self.splits = splits
        self.split_method = split_method
        self.sim = sim
        self.is_filter_null = is_filter_null

        self.new_image_size = new_image_size  # None - no resize
        # Изменение разметки YOLO не требуется - она в относительных координатах
        # COCO - требуется.
        # Также требуется resize изображений

        self.data = project_data
        self.split_data = split_data

    def run(self):
        if self.format == "YOLO Seg":
            self.exportToYOLO(type="seg")
        elif self.format == "YOLO Box":
            self.exportToYOLO(type="box")
        elif self.format == "MMSegmentation":
            self.exportMMSeg()
        elif self.format == "SAMA (split and copy according to selected tran/test/val)":
            self.export_sama()  # Az+: копирование части датасета в исходном формате SAMA
        # else:
        #     self.exportToCOCO()

    def export_sama(self):
        """Копирование в отдельные каталоги train, val, test файлов проекта в
        соответствии с параметрами сортировки"""
        export_dir = self.export_dir
        if not os.path.isdir(export_dir):
            return

        # создаем каталоги train/val/test
        train_val_test_dirs = self.create_images_labels_subdirs(export_dir)

        # Собираем только существующие изображения
        self.clear_not_existing_images()
        split_names = self.split_data
        sum_images = sum(len(images) for images in self.split_data.values())
        im_num = 0  # счетчик
        timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

        # {"train": ["img01.jpg, "img02.jpg", ...], ... }
        for split_folder, image_names in split_names.items():
            if image_names:
                # создаем новый проект SAMA
                new_sama_file = DatasetSAMAHandler()

                # каталог для файла проекта и соответствующих изображений
                dest_dir = train_val_test_dirs[split_folder]
                new_sama_file.data["path_to_images"] = dest_dir
                new_sama_file.data["labels"] = self.data["labels"]
                new_sama_file.data["labels_color"] = self.data["labels_color"]
                new_sama_file.data["description"] = "Export to " + train_val_test_dirs[split_folder] + "\n" + \
                                                    str(timestamp) + "\n" + self.data["description"]

                new_sama_images = []
                for filename, image in self.data["images"].items():
                    if filename not in image_names:
                        continue

                    if not len(image["shapes"]) and self.is_filter_null:  # чтобы не создавать пустых файлов
                        continue

                    src = os.path.join(self.data["path_to_images"], filename)
                    if not os.path.exists(src):
                        continue

                    dest = os.path.join(dest_dir, filename)
                    if src != dest:
                        shutil.copy(src, dest)

                    new_sama_images.append({filename: image})
                    im_num += 1
                    self.export_percent_conn.emit(int(100 * im_num / sum_images))

                new_sama_file.data["images"] = new_sama_images
                new_sama_file.save(os.path.join(dest_dir, f"export_{split_folder}.json"))

    def get_labels(self):
        return self.data["labels"]

    def get_export_map(self, export_label_names):
        label_names = self.get_labels()
        export_map = {}
        export_cls_num = 0
        for i, name in enumerate(label_names):
            if name in export_label_names:
                export_map[name] = export_cls_num
                export_cls_num += 1
            else:
                export_map[name] = 'del'

        return export_map

    def is_blurred_classes(self, export_map):
        for label in export_map:
            if export_map[label] == 'blur':
                return True

        return False

    def create_images_labels_subdirs(self, export_dir, is_labels_need=True):

        if self.format == "MMSegmentation":

            images_dir = os.path.join(export_dir, 'img_dir')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            for folder in ["train", "val", "test"]:
                folder_name = os.path.join(images_dir, folder)
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

            labels_dir = os.path.join(export_dir, 'ann_dir')
            if not os.path.exists(labels_dir):
                os.makedirs(labels_dir)

            for folder in ["train", "val", "test"]:
                folder_name = os.path.join(labels_dir, folder)
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

            return images_dir, labels_dir

        elif (self.format == "YOLO Seg") or (self.format == "YOLO Box"):
            # Формат экспорт YOLO или COCO
            images_dir = os.path.join(export_dir, 'images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)

            for folder in ["train", "val", "test"]:
                folder_name = os.path.join(images_dir, folder)
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

            if is_labels_need:
                labels_dir = os.path.join(export_dir, 'labels')
                if not os.path.exists(labels_dir):
                    os.makedirs(labels_dir)

                for folder in ["train", "val", "test"]:
                    folder_name = os.path.join(labels_dir, folder)
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)

                return images_dir, labels_dir

            return images_dir

        else:
            # формат SAMA
            if not self.split_data:
                return None

            if not self.split_data:
                return None

            dirs = {"train": None, "val": None, "test": None}

            for key in dirs.keys():
                # Проверяем наличие ключа и его значение в self.split_data
                if key in self.split_data and self.split_data[key]:
                    new_dir = os.path.join(export_dir, key)
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                    dirs[key] = new_dir

            return dirs

    def create_blur_dir(self, export_dir):
        blur_dir = os.path.join(export_dir, 'blur')
        if not os.path.exists(blur_dir):
            os.makedirs(blur_dir)
        return blur_dir

    def write_yolo_seg_line(self, shape, im_shape, f, cls_num):
        """
        Пишет одну запись в txt YOLO
        shape - [ [x1, y1], ... ] в абс координатах
        """
        points = shape["points"]
        line = f"{cls_num}"
        for point in points:
            line += f" {point[0] / im_shape[1]} {point[1] / im_shape[0]}"

        f.write(f"{line}\n")

    def write_yolo_box_line(self, shape, im_shape, f, cls_num):
        points = shape["points"]
        xs = []
        ys = []
        for point in points:
            xs.append(point[0])
            ys.append(point[1])
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        w = abs(max_x - min_x)
        h = abs(max_y - min_y)

        x_center = min_x + w / 2
        y_center = min_y + h / 2

        f.write(
            f"{cls_num} {x_center / im_shape[1]} {y_center / im_shape[0]} {w / im_shape[1]} {h / im_shape[0]}\n")

    def create_mmseg_readme(self, yaml_short_name, save_folder, label_names, dataset_name='Dataset', palette=None):
        label_names = {k: v + 1 for v, k in enumerate(label_names)}
        label_names['background'] = 0
        yaml_full_name = os.path.join(save_folder, yaml_short_name)
        with open(yaml_full_name, 'w') as f:
            f.write(f"# {dataset_name}\n")
            # Paths:
            path_str = f"path: {save_folder}\n"
            path_str += "annotations: ann_dir \n"
            path_str += "images: img_dir\n"
            f.write(path_str)
            # Classes:
            f.write("#Classes\n")
            f.write(f"nc: {len(label_names)} # number of classes\n")
            f.write(f"names: {label_names}\n")
            if not palette:
                palette = {}
                for name, cls_num in label_names:
                    if cls_num > len(config.COLORS) - 1:
                        color_num = len(config.COLORS) % (cls_num + 1) - 1
                        color = config.COLORS[color_num][:-1]
                    else:
                        color = config.COLORS[cls_num][:-1]
                    palette[name] = color
            f.write(f"palette: {palette}\n")

    def exportMMSeg(self):
        """
        Экспорт датасета в формат MM Segmentation

        Номер класса для фона - 0
        Нумерация остальных классов начинается с 1

        my_dataset
        |-- img_dir
        |   |-- train
        |   |   |-- xxx{img_suffix}
        |   |   |-- yyy{img_suffix}
        |   |   |-- zzz{img_suffix}
        |   |-- val
        |-- ann_dir
        |   |-- train
        |   |   |-- xxx{seg_map_suffix}
        |   |   |-- yyy{seg_map_suffix}
        |   |   |-- zzz{seg_map_suffix}
        |   |-- val
        """

        export_dir = self.export_dir
        export_map = self.export_map

        if not os.path.isdir(export_dir):
            return

        images_dir, labels_dir = self.create_images_labels_subdirs(export_dir)

        self.clear_not_existing_images()
        labels_names = self.get_labels()

        if not export_map:
            export_map = self.get_export_map(labels_names)

        is_blur = self.is_blurred_classes(export_map)

        if is_blur:
            blur_dir = self.create_blur_dir(export_dir)

        split_names = self.split_data
        im_num = 0

        export_label_names = {}
        unique_values = []
        for k, v in export_map.items():
            if v != 'del' and v != 'blur' and v not in unique_values:
                export_label_names[k] = v
                unique_values.append(v)

        labels_color = self.data['labels_color']  # dict {name:rgba}
        palette = {k: v[:-1] for k, v in labels_color.items()}

        self.create_mmseg_readme(f"{self.dataset_name}.yaml", export_dir, list(export_label_names.keys()),
                                 dataset_name=self.dataset_name, palette=palette)

        for split_folder, image_names in split_names.items():

            for filename, image in self.data["images"].items():

                if filename not in image_names:
                    continue

                if not len(image["shapes"]) and self.is_filter_null:  # чтобы не создавать пустых файлов
                    continue

                fullname = os.path.join(self.data["path_to_images"], filename)

                if not os.path.exists(fullname):
                    continue

                width, height = Image.open(fullname).size
                im_shape = [height, width]

                # Final_mask - маска. На нее по очереди наносятся маски полигонов
                if self.new_image_size:
                    final_mask = np.zeros((self.new_image_size[1], self.new_image_size[0]))
                else:
                    final_mask = np.zeros((height, width))

                final_mask[:, :] = 0  # сперва вся маска заполнена фоном

                if is_blur:
                    txt_yolo_name = convert_image_name_to_txt_name(filename)
                    blur_txt_name = os.path.join(blur_dir, txt_yolo_name)
                    blur_f = open(blur_txt_name, 'w')

                # Desc - порядок. По умолчанию - по убыванию площади
                #     Нужно для нанесения сегментов на маску. Сперва большие сегменты, затем маленькие.
                #     Возвращает сортированный список shapes по площади
                sorted_by_area_shapes = sort_shapes_by_area(image['shapes'], True)

                for shape in sorted_by_area_shapes:
                    cls_num = shape["cls_num"]

                    points = shape["points"]

                    if self.new_image_size:
                        # масштабируем полигон
                        new_points = []
                        for point in points:
                            x_scale = 1.0 * self.new_image_size[0] / width
                            y_scale = 1.0 * self.new_image_size[1] / height
                            x = int(point[0] * x_scale)
                            y = int(point[1] * y_scale)
                            new_points.append([x, y])
                        points = new_points

                    if cls_num == -1 or cls_num > len(labels_names) - 1:
                        continue

                    label_name = labels_names[cls_num]
                    export_cls_num = export_map[label_name]

                    if export_cls_num == 'del':
                        continue

                    elif export_cls_num == 'blur':
                        self.write_yolo_seg_line(shape, im_shape, blur_f, 0)

                    else:
                        # Наносим полигон в виде маски на image_name.png
                        # нумерация классов начинается с 1. 0 - фон
                        paint_shape_to_mask(final_mask, points, export_cls_num + 1)

                # Сохраняем маску {png_ann_name} в директорию ann_dir/{split_folder}/
                png_ann_name = convert_image_name_to_png_name(filename)
                png_fullpath = os.path.join(labels_dir, split_folder, png_ann_name)
                cv2.imwrite(png_fullpath, final_mask)

                if is_blur:
                    blur_f.close()
                    # mask = get_mask_from_yolo_txt(fullname, blur_txt_name, [0])
                    # blurred_image_cv2 = blur_image_by_mask(fullname, mask)
                    # if self.new_image_size:
                    #     blurred_image_cv2 = cv2.resize(blurred_image_cv2, self.new_image_size)

                    # cv2.imwrite(os.path.join(images_dir, split_folder, filename), blurred_image_cv2)
                else:

                    if self.new_image_size:
                        img = cv2.imread(fullname)
                        new_img = cv2.resize(img, self.new_image_size)
                        cv2.imwrite(os.path.join(images_dir, split_folder, filename), new_img)
                    else:
                        shutil.copy(fullname, os.path.join(images_dir, split_folder, filename))

                im_num += 1
                self.export_percent_conn.emit(int(100 * im_num / (len(self.data['images']))))

    def exportToYOLO(self, type):
        """
        type "seg" / "box"
        export_map - {label_name: cls_num или 'del' или 'blur' , ... } Экспортируемых меток может быть меньше
        """
        export_dir = self.export_dir
        export_map = self.export_map

        if not os.path.isdir(export_dir):
            return

        self.clear_not_existing_images()
        labels_names = self.get_labels()

        if not export_map:
            export_map = self.get_export_map(labels_names)

        images_dir, labels_dir = self.create_images_labels_subdirs(export_dir)
        is_blur = self.is_blurred_classes(export_map)

        if is_blur:
            blur_dir = self.create_blur_dir(export_dir)

        export_label_names = {}
        unique_values = []
        for k, v in export_map.items():
            if v != 'del' and v != 'blur' and v not in unique_values:
                export_label_names[k] = v
                unique_values.append(v)

        use_test = True if self.variant_idx == 0 else False
        create_yaml(f"{self.dataset_name}.yaml", export_dir, list(export_label_names.keys()),
                    dataset_name=self.dataset_name, use_test=use_test)

        split_names = self.split_data  # Az+
        im_num = 0

        for split_folder, image_names in split_names.items():

            for filename, image in self.data["images"].items():

                if filename not in image_names:
                    continue

                if not len(image["shapes"]) and self.is_filter_null:  # чтобы не создавать пустых файлов
                    continue

                fullname = os.path.join(self.data["path_to_images"], filename)

                if not os.path.exists(fullname):
                    continue

                txt_yolo_name = convert_image_name_to_txt_name(filename)

                width, height = Image.open(fullname).size
                im_shape = [height, width]

                if is_blur:
                    blur_txt_name = os.path.join(blur_dir, txt_yolo_name)
                    blur_f = open(blur_txt_name, 'w')

                with open(os.path.join(labels_dir, split_folder, txt_yolo_name), 'w') as f:
                    for shape in image["shapes"]:
                        cls_num = shape["cls_num"]  # Shape - в абсолютных координатах

                        if cls_num == -1 or cls_num > len(labels_names) - 1:
                            continue

                        label_name = labels_names[cls_num]
                        export_cls_num = export_map[label_name]

                        if export_cls_num == 'del':
                            continue

                        elif export_cls_num == 'blur':
                            if type == "seg":
                                self.write_yolo_seg_line(shape, im_shape, blur_f, 0)
                            elif type == "box":
                                self.write_yolo_box_line(shape, im_shape, blur_f, 0)

                        else:
                            if type == "seg":
                                self.write_yolo_seg_line(shape, im_shape, f, export_cls_num)
                            elif type == "box":
                                self.write_yolo_box_line(shape, im_shape, f, export_cls_num)

                if is_blur:
                    blur_f.close()
                #     mask = get_mask_from_yolo_txt(fullname, blur_txt_name, [0])
                #     blurred_image_cv2 = blur_image_by_mask(fullname, mask)
                #     if self.new_image_size:
                #         blurred_image_cv2 = cv2.resize(blurred_image_cv2, self.new_image_size)
                #
                #     cv2.imwrite(os.path.join(images_dir, split_folder, filename), blurred_image_cv2)
                else:
                    if self.new_image_size:
                        pass
                        # img = cv2.imread(fullname)
                        # new_img = cv2.resize(img, self.new_image_size)
                        # cv2.imwrite(os.path.join(images_dir, split_folder, filename), new_img)
                    else:
                        src = fullname
                        dest = os.path.join(images_dir, split_folder, filename)
                        if src != dest:
                            shutil.copy(src, dest)

                im_num += 1
                self.export_percent_conn.emit(int(100 * im_num / (len(self.data['images']))))

    # def exportToCOCO(self):
    #
    #     export_dir = self.export_dir
    #     export_map = self.export_map
    #
    #     self.clear_not_existing_images()
    #     labels_names = self.get_labels()
    #
    #     if not export_map:
    #         export_map = self.get_export_map(labels_names)
    #
    #     images_dir = self.create_images_labels_subdirs(export_dir, is_labels_need=False)
    #     is_blur = self.is_blurred_classes(export_map)
    #
    #     if is_blur:
    #         blur_dir = self.create_blur_dir(export_dir)
    #
    #     split_names = self.get_split_image_names()
    #
    #     for split_folder, image_names in split_names.items():
    #
    #         # split folder - one of [train, val, test]
    #
    #         export_json = {}
    #         export_json["info"] = {"year": datetime.date.today().year, "version": "1.0",
    #                                "description": "exported to COCO format using AI Annotator", "contributor": "",
    #                                "url": "", "date_created": datetime.date.today().strftime("%c")}
    #
    #         export_json["images"] = []
    #
    #         id_tek = 1
    #         id_map = {}
    #
    #         for filename, image in self.data["images"].items():
    #
    #             if filename not in image_names:
    #                 continue
    #
    #             if not len(image["shapes"]) and self.is_filter_null:  # чтобы не создавать пустых файлов
    #                 continue
    #
    #             id_map[filename] = id_tek
    #             im_full_path = os.path.join(self.data["path_to_images"], filename)
    #             im_save_path = os.path.join(images_dir, split_folder, filename)
    #
    #             if not os.path.exists(im_full_path):
    #                 continue
    #
    #             width, height = Image.open(im_full_path).size
    #             im_shape = [height, width]
    #
    #             width = im_shape[1]
    #             height = im_shape[0]
    #             im_dict = {"id": id_tek, "width": width, "height": height, "file_name": filename, "license": 0,
    #                        "flickr_url": im_save_path, "coco_url": im_save_path, "date_captured": ""}
    #             export_json["images"].append(im_dict)
    #
    #             id_tek += 1
    #
    #         export_json["annotations"] = []
    #
    #         seg_id = 1
    #         im_num = 0
    #         for filename, image in self.data["images"].items():
    #
    #             if filename not in image_names:
    #                 continue
    #
    #             if not len(image["shapes"]) and self.is_filter_null:  # чтобы не создавать пустых файлов
    #                 continue
    #
    #             fullname = os.path.join(self.data["path_to_images"], filename)
    #
    #             txt_yolo_name = hf.convert_image_name_to_txt_name(filename)
    #             if not os.path.exists(fullname):
    #                 continue
    #
    #             width, height = Image.open(fullname).size
    #             im_shape = [height, width]
    #
    #             if is_blur:
    #                 blur_txt_name = os.path.join(blur_dir, txt_yolo_name)
    #                 blur_f = open(blur_txt_name, 'w')
    #
    #             for shape in image["shapes"]:
    #
    #                 cls_num = shape["cls_num"]
    #
    #                 if cls_num == -1 or cls_num > len(labels_names) - 1:
    #                     continue
    #
    #                 label_name = labels_names[cls_num]
    #                 export_cls_num = export_map[label_name]
    #
    #                 if export_cls_num == 'del':
    #                     continue
    #
    #                 elif export_cls_num == 'blur':
    #                     self.write_yolo_seg_line(shape, im_shape, blur_f, 0)
    #
    #                 else:
    #                     points = shape["points"]
    #                     xs = []
    #                     ys = []
    #                     all_points = [[]]
    #
    #                     for point in points:
    #                         if self.new_image_size:
    #                             x_scale = 1.0 * self.new_image_size[0] / width
    #                             y_scale = 1.0 * self.new_image_size[1] / height
    #                             x = int(point[0] * x_scale)
    #                             y = int(point[1] * y_scale)
    #                             xs.append(x)
    #                             ys.append(y)
    #                             all_points[0].append(x)
    #                             all_points[0].append(y)
    #                         else:
    #                             xs.append(point[0])
    #                             ys.append(point[1])
    #                             all_points[0].append(int(point[0]))
    #                             all_points[0].append(int(point[1]))
    #
    #                     seg = np.array(all_points[0])
    #
    #                     poly = np.reshape(seg, (seg.size // 2, 2))
    #                     poly = Polygon(poly)
    #                     area = poly.area
    #
    #                     min_x = min(xs)
    #                     max_x = max(xs)
    #                     min_y = min(ys)
    #                     max_y = max(ys)
    #                     w = abs(max_x - min_x)
    #                     h = abs(max_y - min_y)
    #
    #                     x_center = min_x + w / 2
    #                     y_center = min_y + h / 2
    #
    #                     bbox = [int(x_center), int(y_center), int(width), int(height)]
    #
    #                     seg = {"segmentation": all_points, "area": int(area), "bbox": bbox, "iscrowd": 0, "id": seg_id,
    #                            "image_id": id_map[filename], "category_id": export_cls_num + 1}
    #                     export_json["annotations"].append(seg)
    #                     seg_id += 1
    #
    #             if is_blur:
    #                 blur_f.close()
    #                 mask = get_mask_from_yolo_txt(fullname, blur_txt_name, [0])
    #                 blurred_image_cv2 = blur_image_by_mask(fullname, mask)
    #                 if self.new_image_size:
    #                     blurred_image_cv2 = cv2.resize(blurred_image_cv2, self.new_image_size)
    #
    #                 cv2.imwrite(os.path.join(images_dir, split_folder, filename), blurred_image_cv2)
    #             else:
    #
    #                 if self.new_image_size:
    #                     img = cv2.imread(fullname)
    #                     new_img = cv2.resize(img, self.new_image_size)
    #                     cv2.imwrite(os.path.join(images_dir, split_folder, filename), new_img)
    #                 else:
    #                     shutil.copy(fullname, os.path.join(images_dir, split_folder, filename))
    #
    #             im_num += 1
    #             self.export_percent_conn.percent.emit(int(100 * im_num / (len(self.data['images']))))
    #
    #         export_json["licenses"] = [{"id": 0, "name": "Unknown License", "url": ""}]
    #         export_json["categories"] = []
    #
    #         for label in export_map:
    #             if export_map[label] != 'del' and export_map[label] != 'blur':
    #                 category = {"supercategory": "type", "id": export_map[label] + 1, "name": label}
    #                 export_json["categories"].append(category)
    #
    #         with open(os.path.join(images_dir, split_folder, f"{split_folder}.json"), 'w') as f:
    #             ujson.dump(export_json, f)

    def get_image_path(self):
        return self.data["path_to_images"]

    def clear_not_existing_images(self):
        images = {}
        im_path = self.get_image_path()
        for filename, im in self.data['images'].items():
            if os.path.exists(os.path.join(im_path, filename)):
                images[filename] = im
            else:
                print(f"Checking files: image {filename} doesn't exist")

        self.data['images'] = images


# ----------------------------------------------------------------------------------------------------------------------
def create_yaml(yaml_short_name, save_folder, label_names, dataset_name='dataset', use_test=None):
    """Создание файла yaml для датасета"""
    yaml_full_name = os.path.join(save_folder, yaml_short_name)
    with open(yaml_full_name, 'w') as f:
        f.write(f"# {dataset_name}\n")

        # Paths:
        path_str = f"path: {save_folder}\n"
        path_str += "train: images/train  # train images (relative to 'path') \n"
        path_str += "val: images/val  # val images (relative to 'path')\n"
        if not use_test:
            path_str += "test:  # test images (optional)\n"
        else:
            path_str += "test:  images/test # test images\n"
        f.write(path_str)

        # Classes:
        f.write("#Classes\n")
        f.write(f"nc: {len(label_names)} # number of classes\n")
        f.write(f"names: {label_names}\n")


def convert_image_name_to_txt_name(image_name):
    splitted_name = image_name.split('.')
    txt_name = ""
    for i in range(len(splitted_name) - 1):
        txt_name += splitted_name[i]

    return txt_name + ".txt"


def sort_shapes_by_area(shapes, desc=True):
    """
    shapes - List({'points': List([x1,y1], [x2,y2], ...), 'cls_num' : Int, 'id': Int})
    desc - порядок. По умолчанию - по убыванию площади
    Нужно для нанесения сегментов на маску. Сперва большие сегменты, затем маленькие.
    Возвращает сортированный список shapes по площади
    """
    if desc:
        areas = [-Polygon(shape["points"]).area for shape in shapes]
    else:
        areas = [Polygon(shape["points"]).area for shape in shapes]
    idx = np.argsort(areas)
    return [shapes[i] for i in idx]


def paint_shape_to_mask(mask, points, cls_num):
    """
    Добавляет на mask - np.zeros((img_height, img_width))
    points:[ [x1,y1], ...] - точки граней маски
    cls_num - номер класса
    """
    img_height, img_width = mask.shape

    pol = Polygon(points)

    mask_image = features.rasterize([pol], out_shape=(img_height, img_width),
                                    fill=0,
                                    default_value=cls_num)

    mask[mask_image == cls_num] = cls_num


def convert_image_name_to_png_name(image_name):
    splitted_name = image_name.split('.')
    txt_name = ""
    for i in range(len(splitted_name) - 1):
        txt_name += splitted_name[i]

    return txt_name + ".png"


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    from utils.sama_project_handler import DatasetSAMAHandler

    app = QtWidgets.QApplication(sys.argv)
    sama_data = DatasetSAMAHandler()
    sama_data.load("D:/data_sets/uranium enrichment/data/anno_json_r800/anno_sama_r800.json")
    split = {'train': ['01_bra_resende_2023-08_02_000.jpg', '01_bra_resende_bing_03_000.jpg'],
             'val': ['02_gbr_capenhurst_2018-03_000.jpg', '02_gbr_capenhurst_2018-03_001.jpg', '03_DEU_2022.jpg'],
             'test': []}
    w = AzExportDialog(sama_data, split_data=split)
    w.show()
    app.exec()
