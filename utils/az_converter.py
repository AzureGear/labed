from random import randint
from utils.helper import load_json, save_json, random_color
import shutil
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
    data["path_to_images"] = os.path.dirname(input_files[0])  # такой же, как у первого файла
    images = {}  # изображения
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
            continue

        if not "imagePath" in label_me_data:
            error_numbers += 1
            continue

        img_name = label_me_data["imagePath"]  # формируем имя файла (можно и через os.path.basename(image))
        lm_shapes = label_me_data["shapes"]  # список формата labelMe, где [ { "label", "points []", ... }, { ... } ]

        for lm_shp_dict in lm_shapes:  # просматриваем список "shapes" LabelMe
            shapes = {}  # каждое новое изображение обновляем
            labels_set.add(lm_shp_dict["label"])  # перечень меток должен быть уникальным без повтора

            for lab in labels_set:  # проверяем есть ли у нас такой ключ в сете
                if lab not in class_numbers:
                    class_numbers[lab] = len(labels_set) - 1  # счетчик классов в формате Ромы начинается с 0
            id_count = id_count + 1  # увеличиваем счётчик объектов
            shapes["cls_num"] = class_numbers[lm_shp_dict["label"]]  # номер класса (имя метки)
            shapes["id"] = id_count  # счетчик объектов
            shapes["points"] = lm_shp_dict["points"]  # полигоны
            list_shapes.append(shapes)
        images[img_name] = {"shapes": list_shapes,
                            "lrm": None,
                            'status': 'empty'}

    if error_numbers == len(input_files):  # всё завершилось ошибками
        return False

    for label in labels_set:  # для всех меток...
        labels_colors[label] = random_color()  # ...формируем случайные цвета
    data["images"] = images
    data["labels"] = list(class_numbers.keys())  # ключи class_numbers содержат список меток по порядку
    data["labels_color"] = labels_colors
    save_json(output_file, data, 'w+')
    return True


# ----------------------------------------------------------------------------------------------------------------------
def merge_sama_to_sama(input_files, output_file, copy_files=False):
    """
    Слияние файлов проектов формата SAMA с копированием файлов
    """
    result = {"error_no_data": [], "error_duplicate": []}

    error_no_data = []  # список ошибок отсутствия данных
    error_duplicate_images = []  # список ошибок дублирования изображений
    data = dict()  # выходные данные
    data["path_to_images"] = os.path.dirname(output_file)  # путь каталога выходного файла
    images = dict()  # словарь всех изображений
    id_count = 0
    combined_labels = []  # объединенные метки для всех-всех файлов (супер список)
    combined_colors = dict()
    combined_descr = ""  # объединенное описание проекта

    for input_file in input_files:  # проходим цикл, чтобы сформировать общий набор классов (имён меток)
        input_data = load_json(input_file)
        if not input_data:
            error_no_data.append(input_file)

        else:
            input_labels = input_data["labels"]  # список имен меток { "label1", "label2", ... }

            for label in input_labels:
                if label not in combined_labels:  # если метки в нашем объединённом словаре нет...
                    combined_labels.append(label)  # ...то мы её добавляем
                    combined_colors[label] = input_data["labels_color"][label]  # заодно формируем цвета
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

        for image, image_dict in input_data["images"].items():  # анализируем словарь изображений
            if image not in images.keys():  # такого изображения нет, значит будем добавлять его в словарь
                image_dict.setdefault("last_user", None)
                image_dict.setdefault("lrm", None)
                image_dict.setdefault("status", None)

                new_image_dict = {"shapes": [],  # новый словарь для image: { shapes, lrm, status, last_user }
                                  "lrm": image_dict["lrm"],
                                  "status": image_dict["status"],
                                  "last_user": image_dict["last_user"]}

                for shape in image_dict["shapes"]:  # shape = { "cls_num":, "id":, "points":[ ] }
                    new_one_shape = {"cls_num": labels_match_dict[shape["cls_num"]], "id": id_count,
                                     "points": shape["points"]}
                    id_count += 1
                    new_image_dict["shapes"].append(new_one_shape)

                # копируем изображение из исходного в выходной каталог, если оно в наличии
                if copy_files and os.path.exists(os.path.join(input_dir, image)):
                    shutil.copyfile(os.path.join(input_dir, image), os.path.join(os.path.dirname(output_file), image))

                images[image] = new_image_dict
            else:
                # имеется такое же точно изображение; сперва попробуем объединить разметку
                exist_image_dict = images[image]  # анализируем имеющуюся разметку
                exist_cls = set(shape["cls_num"] for shape in exist_image_dict["shapes"])  # список классов правильный
                new_cls = set(labels_match_dict[shape["cls_num"]] for shape in image_dict["shapes"])
                common_cls = exist_cls & new_cls

                if len(common_cls) > 0:  # для изображения есть разметка, которая может конфликтовать
                    error_duplicate_images.append(image)  # не стоит объединять, добавляем в ошибку

                else:  # иначе объединяем разметку для снимка
                    exist_shape = exist_image_dict["shapes"]
                    for shape in image_dict["shapes"]:  # сама разметка
                        new_one_shape = {"cls_num": labels_match_dict[shape["cls_num"]], "id": id_count,
                                         "points": shape["points"]}
                        exist_shape.append(new_one_shape)
                        id_count += 1

                    keys_check = ["last_user", "lrm", "status"]  # перечень ключей, которые следует проверить
                    for key in keys_check:
                        if exist_image_dict.get(key):  # если они не пустые...
                            image_dict[key] = exist_image_dict[key]  # ...то они заменяться реальными значениями

                    new_image_dict = {"shapes": exist_shape,  # объединенный словарь для image
                                      "lrm": image_dict["lrm"],
                                      "status": image_dict["status"],
                                      "last_user": image_dict["last_user"]}
                    images[image] = new_image_dict

    data["images"] = images
    data["description"] = combined_descr
    save_json(output_file, data, 'w+')  # записываем результат

    result["error_duplicate_images"] = error_duplicate_images  # ошибки отсутствия данных
    return result

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':  # заглушка для отладки
    merge_sama_to_sama(["d:/data_sets/oil_refinery/tests/test_for_sama_merge/proj1/proj_one.json",
                        "d:/data_sets/oil_refinery/tests/test_for_sama_merge/proj2/proj_two.json"],
                       "d:/data_sets/output_data/_merge.json")
    # convert_labelme_to_sama(my_list, "D:/data_sets/output data/_merge.json")
