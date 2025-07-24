from shapely.validation import make_valid
from shapely.geometry import Polygon
from utils.helper import load_json, save_json, random_color
from random import randint
import shutil
import numpy as np
import os


# ----------------------------------------------------------------------------------------------------------------------
"""
Структура *.json файла SAMA (Романа Хабарова)

"path_to_images": "F:\\data_sets\\test_oil_ref\\"
data["path_to_images"] = "only_one_path"
 ├- data["images"] = {"one.jpg":{ }, "two.jpg":{ }, ... , "n.jpg":{ } }
 |                               └- {shapes: [ { } ] }
 |                                              └- "cls_num":, "id":, "points":[ ]
 |                                                                              └- [[x1, y1], [x2, y2], ... [xn, yn]]
 ├- data["labels"] = ["name_one", "name_two", ... , "name_n"]
 └- data["labels_color"] = {"name_one", "name_two", ... , "name_n": [ ] }
                                                                     └- label [r, g, b]
"""
# ----------------------------------------------------------------------------------------------------------------------
""" Структура *.json  файла LabelMe (Michael Pitidis, Hussein Abdulwahid, Kentaro Wada)

"version": "",
"flags": {},
"shapes": [{ }, { } ... { } ]
            ├- "label" : "name",
            ├- "points" : [ ],
            |              └- [ [x1, y1], [x2, y2], ... [xn, yn] ]
            ├- "group_id" : null,
            ├- "description" : "descr",
            ├- "shape_type" : "polygon",
            ├- "flags" : { },
            └- "mask" : null
"imagePath": "some_name.jpg",
"imageData": "...<data>..."
"""
# ----------------------------------------------------------------------------------------------------------------------
"""
# Структура файла хранения проекта точек Визуального ручного кадрирования (AzManualSlice):

"filename" = "D:/data_sets/uranium enrichment/test_cut/crude_uranium_enrichment.json"  # 
"scan_size" = 1280  # размер окна кадрирования
"images" = { "125n_FRA_2019-09.jpg" : [ ], ... }
	                                   └-  "points" : { [x1, y1], [x2, y2], ... , [xN, yN] }
"""


# ----------------------------------------------------------------------------------------------------------------------

def convert_labelme_to_sama(input_files, output_file):
    """
    Конвертация файлов проекта LabelMe в проект SAMA
    """
    data = dict()
    result = {"no_label_me_data": [], "dublicated_data": []}
    error_no_data = []  # список ошибок отсутствия данных labelme
    error_duplicate_images = []  # список ошибок дублирования изображений
    data["path_to_images"] = os.path.dirname(
        input_files[0])  # такой же, как у первого файла
    images = {}  # изображения
    base_names_set = set()  # базовые имена, т.к. SAMA не терпят одинаковых
    error_numbers = 0  # количество ошибок при конвертации
    class_numbers = {}  # {имя класса:номера класса} считая с 0; создаётся динамически
    labels_colors = {}  # цвета меток
    labels_set = set()  # метки: перечень уникальных меток
    id_count = -1  # начинаем с -1, т.к. на первой итерации +1 и будет id:0.

    for item in input_files:  # начинаем обход перечня полученных файлов
        list_shapes = []
        label_me_data = load_json(item)

        if not label_me_data:
            error_numbers += 1
            error_no_data.append(item)
            continue

        # формируем имя файла (можно и через os.path.basename(image))
        img_name = label_me_data["imagePath"]
        # список формата labelMe, где [ { "label", "points []", ... }, { ... } ]
        lm_shapes = label_me_data["shapes"]

        for lm_shp_dict in lm_shapes:  # просматриваем список "shapes" LabelMe
            shapes = {}  # каждое новое изображение обновляем
            # перечень меток должен быть уникальным без повтора
            labels_set.add(lm_shp_dict["label"])

            for lab in labels_set:  # проверяем есть ли у нас такой ключ в сете
                if lab not in class_numbers:
                    # счетчик классов в формате Ромы начинается с 0
                    class_numbers[lab] = len(labels_set) - 1
            id_count = id_count + 1  # увеличиваем счётчик объектов
            # номер класса (имя метки)
            shapes["cls_num"] = class_numbers[lm_shp_dict["label"]]
            shapes["id"] = id_count  # счетчик объектов
            shapes["points"] = lm_shp_dict["points"]  # полигоны
            list_shapes.append(shapes)
        images[img_name] = {"shapes": list_shapes,
                            "lrm": None,
                            'status': 'empty'}
        base_name = os.path.basename(item)
        if base_name not in base_names_set:
            base_names_set.add(base_name)
        else:
            error_duplicate_images.append(item)

    result["no_label_me_data"] = error_no_data
    result["dublicated_data"] = error_duplicate_images
    if error_numbers == len(input_files):  # всё завершилось ошибками

        return False, result

    for label in labels_set:  # для всех меток...
        labels_colors[label] = random_color()  # ...формируем случайные цвета
    data["images"] = images
    # ключи class_numbers содержат список меток по порядку
    data["labels"] = list(class_numbers.keys())
    data["labels_color"] = labels_colors
    save_json(output_file, data, 'w+')
    return True, result


# ----------------------------------------------------------------------------------------------------------------------
def merge_sama_to_sama(input_files, output_file, copy_files=False):
    """
    Слияние файлов проектов формата SAMA с копированием файлов
    """
    result = {"success": [], "error_no_data": [], "error_duplicate": []}

    error_no_data = []  # список ошибок отсутствия данных
    success_data = []
    error_duplicate_images = []  # список ошибок дублирования изображений
    data = dict()  # выходные данные
    data["path_to_images"] = os.path.dirname(
        output_file)  # путь каталога выходного файла
    images = dict()  # словарь всех изображений
    id_count = 0
    # объединенные метки для всех-всех файлов (супер список)
    combined_labels = []
    combined_colors = dict()
    combined_descr = ""  # объединенное описание проекта

    # проходим цикл, чтобы сформировать общий набор классов (имён меток)
    for input_file in input_files:
        input_data = load_json(input_file)
        if not input_data:
            error_no_data.append(input_file)

        else:
            # список имен меток { "label1", "label2", ... }
            input_labels = input_data["labels"]

            for label in input_labels:
                if label not in combined_labels:  # если метки в нашем объединённом словаре нет...
                    combined_labels.append(label)  # ...то мы её добавляем
                    # заодно формируем цвета
                    combined_colors[label] = input_data["labels_color"][label]
            if "description" in input_data.keys():
                combined_descr += input_data["description"] + "\n"

    data["labels"] = combined_labels
    data["labels_color"] = combined_colors

    result["error_no_data"] = error_no_data  # ошибки отсутствия данных

    # print(combined_labels)
    if len(input_files) == len(error_no_data):
        return result  # возвращаем словарь ошибок: чтение файлов неудачно, объединить ничего не выйдет

    for input_file in input_files:  # снова проходим все файлы
        input_data = load_json(input_file)
        if not input_data:
            continue
        input_dir = input_data["path_to_images"]
        input_labels = input_data["labels"]
        # сопоставляем номера классов объединённому классификатору
        labels_match_dict = {i: combined_labels.index(label) for i, label in enumerate(input_labels) if
                             label in combined_labels}

        # анализируем словарь изображений
        for image, image_dict in input_data["images"].items():
            if image not in images.keys():  # такого изображения нет, значит будем добавлять его в словарь
                image_dict.setdefault("last_user", None)
                image_dict.setdefault("lrm", None)
                image_dict.setdefault("status", None)

                new_image_dict = {"shapes": [],  # новый словарь для image: { shapes, lrm, status, last_user }
                                  "lrm": image_dict["lrm"],
                                  "status": image_dict["status"],
                                  "last_user": image_dict["last_user"]}

                # shape = { "cls_num":, "id":, "points":[ ] }
                for shape in image_dict["shapes"]:
                    new_one_shape = {"cls_num": labels_match_dict[shape["cls_num"]], "id": id_count,
                                     "points": shape["points"]}
                    id_count += 1
                    new_image_dict["shapes"].append(new_one_shape)

                # копируем изображение из исходного в выходной каталог, если оно в наличии
                if copy_files and os.path.exists(os.path.join(input_dir, image)):
                    shutil.copyfile(os.path.join(input_dir, image), os.path.join(
                        os.path.dirname(output_file), image))

                images[image] = new_image_dict
                success_data.append(image)

            else:
                # Объединяем разметку (с проверкой на дубликаты)
                exist_image_dict = images[image]
                exist_shapes = exist_image_dict["shapes"]
                
                # Создаем словарь для быстрого доступа
                exist_shapes_by_cls = {}
                for shape in exist_shapes:
                    cls_num = shape["cls_num"]
                    exist_shapes_by_cls.setdefault(cls_num, []).append(shape)
                
                # Обработка новых контуров
                for shape in image_dict["shapes"]:
                    new_cls = labels_match_dict[shape["cls_num"]]
                    new_shape = {
                        "cls_num": new_cls,
                        "id": id_count,
                        "points": shape["points"]
                    }
                    id_count += 1
                    
                    # Проверка дубликатов только для текущего класса
                    is_duplicate = False
                    if new_cls in exist_shapes_by_cls:
                        for exist_shape in exist_shapes_by_cls[new_cls]:
                            if is_duplicate_poly(exist_shape, new_shape):
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        exist_shapes.append(new_shape)
                
                # Обновляем словарь
                keys_check = ["last_user", "lrm", "status"]
                for key in keys_check:
                    if exist_image_dict.get(key):
                        image_dict[key] = exist_image_dict[key]
                
                images[image] = {
                    "shapes": exist_shapes,
                    "lrm": image_dict["lrm"],
                    "status": image_dict["status"],
                    "last_user": image_dict["last_user"]
                }
                success_data.append(image)

    data["images"] = images
    data["description"] = combined_descr
    save_json(output_file, data, 'w+')  # записываем результат

    # ошибки отсутствия данных
    result["error_duplicate_images"] = error_duplicate_images
    result["success"] = success_data
    return result


# ----------------------------------------------------------------------------------------------------------------------
def is_duplicate_poly(shape1, shape2, iou_threshold=0.95, distance_threshold=5.0):
    """Определяет, являются ли два контура дубликатами с помощью геометрических метрик"""
    # Создаем полигоны из точек
    poly1 = Polygon(shape1['points'])
    poly2 = Polygon(shape2['points'])
    
    # Исправляем невалидные геометрии (если есть самопересечения)
    if not poly1.is_valid:
        poly1 = make_valid(poly1)
    if not poly2.is_valid:
        poly2 = make_valid(poly2)
    
    # Считаем IoU
    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    iou = intersection / union if union > 0 else 0
    
    # Считам расстояние между центрами
    centroid1 = np.array(poly1.centroid.coords[0])
    centroid2 = np.array(poly2.centroid.coords[0])
    centroid_distance = np.linalg.norm(centroid1 - centroid2)
    
    # Проверяем критерии схожести
    if iou >= iou_threshold: 
        return True # провал по IoU
    if centroid_distance <= distance_threshold and abs(poly1.area - poly2.area) / min(poly1.area, poly2.area) < 0.1:
        return True # провалились по центроидам с площадями полигонов
    
    return False

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':  # заглушка для отладки
    here = os.path.dirname(os.path.abspath(__file__))

    common_dir = os.path.abspath(os.path.join(
        os.path.dirname(here), "tests/data"))
    files_labelme1 = ["001.json", "002.json",
                      "003.json", "004.json", "005.json"]
    files_labelme2 = ["002.json", "004.json", "006.json"]
    for files, subdir in [(files_labelme1, "imgs1"), (files_labelme2, "imgs2")]:
        files[:] = [os.path.join(common_dir, subdir, f) for f in files]
    files_sum = files_labelme1 + files_labelme2
    test_merge = True
    if not test_merge:
        flag, info = convert_labelme_to_sama(
            files_sum, os.path.join(common_dir, "test_output", "my.json"))
        print(flag, info)
    else:
        result = merge_sama_to_sama([os.path.join(common_dir, "proj_one.json"),
                            os.path.join(common_dir, "proj_two.json")],
                            os.path.join(common_dir, "test_output", "merge_sama.json"))
        print(result)
