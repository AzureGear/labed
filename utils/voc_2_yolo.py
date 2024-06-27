import os
import numpy as np
from pathlib import Path
from xml.dom.minidom import parse
from shutil import copyfile

FILE_ROOT = "D:/data_sets/BloodCells/BCCD_Dataset-master_orig/"  # каталог конвертируемого датасета

IMAGE_SET_ROOT = FILE_ROOT + "BCCD/ImageSets/Main"
IMAGE_PATH = FILE_ROOT + "BCCD/JPEGImages"  # каталог изображений
ANNOTATIONS_PATH = FILE_ROOT + "BCCD/Annotations"  # каталог аннотаций

DATA_ROOT = "D:/data_sets/BloodCells/results/"  # выходной каталог
LABELS_ROOT = DATA_ROOT + "BCCD/Labels"  # выходной каталог меток

DEST_IMAGES_PATH = "images"
DEST_LABELS_PATH = "labels"

classes = ['Platelets', 'RBC', 'WBC']

files = os.listdir(ANNOTATIONS_PATH)


def cord_converter(size, box):
    """
    convert xml annotation to darknet format coordinates
    :param size： [w,h]
    :param box: anchor box coordinates [upper-left x,uppler-left y,lower-right x, lower-right y]
    :return: converted [x,y,w,h]
    """
    x1 = int(box[0])
    y1 = int(box[1])
    x2 = int(box[2])
    y2 = int(box[3])

    dw = np.float32(1. / int(size[0]))
    dh = np.float32(1. / int(size[1]))

    w = x2 - x1
    h = y2 - y1
    x = x1 + (w / 2)
    y = y1 + (h / 2)

    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return [x, y, w, h]


def save_file(img_jpg_file_name, size, img_box):  # разметка: исходные xml -> txt
    save_file_name = LABELS_ROOT + '/' + img_jpg_file_name + '.txt'
    print(save_file_name)
    file_path = open(save_file_name, "a+")
    for box in img_box:
        cls_num = classes.index(box[0])  # поиск по class_id

        new_box = cord_converter(size, box[1:])  # Конвертация координат ограничительной рамки в формат YOLO x, y, w, h

        file_path.write(f"{cls_num} {new_box[0]} {new_box[1]} {new_box[2]} {new_box[3]}\n")

    file_path.flush()
    file_path.close()


def get_xml_data(file_path, img_xml_file):
    img_path = file_path + '/' + img_xml_file + '.xml'
    print(img_path)

    dom = parse(img_path)
    root = dom.documentElement
    img_name = root.getElementsByTagName("filename")[0].childNodes[0].data
    img_size = root.getElementsByTagName("size")[0]
    objects = root.getElementsByTagName("object")
    img_w = img_size.getElementsByTagName("width")[0].childNodes[0].data
    img_h = img_size.getElementsByTagName("height")[0].childNodes[0].data
    img_c = img_size.getElementsByTagName("depth")[0].childNodes[0].data
    # print("img_name:", img_name)
    # print("image_info:(w,h,c)", img_w, img_h, img_c)
    img_box = []
    for box in objects:
        cls_name = box.getElementsByTagName("name")[0].childNodes[0].data
        x1 = int(box.getElementsByTagName("xmin")[0].childNodes[0].data)
        y1 = int(box.getElementsByTagName("ymin")[0].childNodes[0].data)
        x2 = int(box.getElementsByTagName("xmax")[0].childNodes[0].data)
        y2 = int(box.getElementsByTagName("ymax")[0].childNodes[0].data)
        # print("box:(c,xmin,ymin,xmax,ymax)", cls_name, x1, y1, x2, y2)
        img_jpg_file_name = img_xml_file + '.jpg'
        img_box.append([cls_name, x1, y1, x2, y2])
    # print(img_box)

    # test_dataset_box_feature(img_jpg_file_name, img_box)
    save_file(img_xml_file, [img_w, img_h], img_box)


def copy_data(img_set_source, img_labels_root, imgs_source, type):
    file_name = img_set_source + '/' + type + ".txt"
    file = open(file_name)

    root_file = Path(DATA_ROOT + DEST_IMAGES_PATH + '/' + type)
    if not root_file.exists():
        print(f"Path {root_file} is not exit")
        os.makedirs(root_file)

    root_file = Path(DATA_ROOT + DEST_LABELS_PATH + '/' + type)
    if not root_file.exists():
        print(f"Path {root_file} is not exit")
        os.makedirs(root_file)

    for line in file.readlines():
        print(line)
        img_name = line.strip('\n')
        img_sor_file = imgs_source + '/' + img_name + '.jpg'
        label_sor_file = img_labels_root + '/' + img_name + '.txt'

        # Копирование изображений
        DICT_DIR = DATA_ROOT + DEST_IMAGES_PATH + '/' + type
        img_dict_file = DICT_DIR + '/' + img_name + '.jpg'

        copyfile(img_sor_file, img_dict_file)

        # Копирование меток
        DICT_DIR = DATA_ROOT + DEST_LABELS_PATH + '/' + type
        img_dict_file = DICT_DIR + '/' + img_name + '.txt'
        copyfile(label_sor_file, img_dict_file)


if __name__ == '__main__':  # вызов конвертации
    for file in files:
        print("file name: ", file)
        file_xml = file.split(".")
        get_xml_data(ANNOTATIONS_PATH, file_xml[0])
    copy_data(IMAGE_SET_ROOT, LABELS_ROOT, IMAGE_PATH, "train")
    copy_data(IMAGE_SET_ROOT, LABELS_ROOT, IMAGE_PATH, "val")
    copy_data(IMAGE_SET_ROOT, LABELS_ROOT, IMAGE_PATH, "test")
