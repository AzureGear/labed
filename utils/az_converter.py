from random import randint
from utils.helper import load, save
import shutil
import os


# ----------------------------------------------------------------------------------------------------------------------
# Структура *.json файла SAMA (Романа Хабарова)
#
# "path_to_images": "F:\\data_sets\\test_oil_ref\\"
# data["path_to_images"] = "only_one_path"
#  ├- data["images"] = {"one.jpg":{ }, "two.jpg":{ }, ... , "n.jpg":{ } }
#  |                               └- {shapes: [ { } ] }
#  |                                              └- "cls_num":, "id":, "points":[ ]
#  |                                                                              └- [[x1, y1], [x2, y2], ... [xn, yn]]
#  ├- data["labels"] = ["name_one", "name_two", ... , "name_n"]
#  └- data["labels_color"] = {"name_one", "name_two", ... , "name_n": [ ] }
#                                                                      └- label [r, g, b]
#
# ----------------------------------------------------------------------------------------------------------------------
# Структура *.json  файла LabelMe (Michael Pitidis, Hussein Abdulwahid, Kentaro Wada)
#
# "version": "",
# "flags": {},
# "shapes": [{ }, { } ... { } ]
#             ├- "label" : "name",
#             ├- "points" : [ ],
#             |              └- [ [x1, y1], [x2, y2], ... [xn, yn] ]
#             ├- "group_id" : null,
#             ├- "description" : "descr",
#             ├- "shape_type" : "polygon",
#             ├- "flags" : { },
#             └- "mask" : null
# "imagePath": "some_name.jpg",
# "imageData": "...<data>..."
#
# ----------------------------------------------------------------------------------------------------------------------
# Структура файла хранения проекта точек Визуального ручного кадрирования (AzManualSlice):
# "filename" = "D:/data_sets/uranium enrichment/test_cut/crude_uranium_enrichment.json"
# "scan_size" = 1280
#  "images" = { "125n_FRA_2019-09.jpg" : [ ], ... }
# 		                                  └-  "points" : { [x1, y1], [x2, y2], ... , [xN, yN] }
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
        label_me_data = load(item)

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
    save(output_file, data, 'w+')
    return True


# ----------------------------------------------------------------------------------------------------------------------
def merge_sama_to_sama(input_files, output_file, copy_files=False):
    """
    Слияние файлов проектов формата SAMA с копированием файлов
    """
    error_main_count = 0  # счетчик серьезных ошибок
    error_duplicate_images = 0  # счетчик ошибок дублирования изображений
    data = dict()  # выходные данные
    data["path_to_images"] = os.path.dirname(output_file)  # путь каталога выходного файла
    images = dict()  # словарь всех изображений
    id_count = 0
    combined_labels = []  # объединенные метки для всех-всех файлов (супер список)
    combined_colors = dict()

    for input_file in input_files:  # проходим цикл, чтобы сформировать общий набор классов (имён меток)
        input_data = load(input_file)
        if not input_data:
            error_main_count += 1  # увеличиваем счетчик важных ошибок
        else:
            input_labels = input_data["labels"]  # список имен меток { "label1", "label2", ... }

            for label in input_labels:
                if label not in combined_labels:  # если метки в нашем объединённом словаре нет...
                    combined_labels.append(label)  # ...то мы её добавляем
                    combined_colors[label] = input_data["labels_color"][label]  # заодно формируем цвета

    data["labels"] = combined_labels
    data["labels_color"] = combined_colors

    # print(combined_labels)
    if len(input_files) == error_main_count:
        return 2  # возвращаем код ошибки: чтение файлов неудачно, объединить ничего не выйдет

    for input_file in input_files:  # снова проходим все файлы
        input_data = load(input_file)
        if not input_data:
            continue
        input_dir = input_data["path_to_images"]
        input_labels = input_data["labels"]
        # сопоставляем номера классов объединённому классификатору
        labels_match_dict = {i: combined_labels.index(label) for i, label in enumerate(input_labels) if
                             label in combined_labels}

        for image, image_dict in input_data["images"].items():  # анализируем словарь изображений
            if image not in images.keys():  # такого изображения нет, значит будем добавлять его в словарь
                new_image_dict = {"shapes": [],  # новый словарь для image: { shapes, lrm, status, last_user }
                                  "lrm": image_dict["lrm"], "status": image_dict["status"], "last_user": None}

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
                error_duplicate_images += 1
    data["images"] = images
    save(output_file, data, 'w+')  # записываем результат
    if error_main_count != 0 or error_duplicate_images != 0:  # сигнализируем об ошибках
        return error_main_count + error_duplicate_images
    else:
        return 0


# ----------------------------------------------------------------------------------------------------------------------
def random_color():  # генерируем случайные цвета
    rand_col = [randint(0, 255), randint(0, 255), randint(0, 255), 120]  # оттенок alfa по умолчанию оставляем 120
    return rand_col


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':  # заглушка для отладки
    merge_sama_to_sama(["d:/labed/labed/test/test_merge_lableme_data_01.json",
                        "d:/data_sets/uranium enrichment/anno_json_r1024_mc/sliced_2024-06-13--09-04-27_mc.json",
                        "d:/data_sets/oil_refinery/cutter_prj/cut_prj.json"],
                       "d:/data_sets/output_data/_merge.json")
    # convert_labelme_to_sama(my_list, "F:/data_sets/uranium enrichment/_merge.json")

