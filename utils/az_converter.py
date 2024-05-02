from random import randint
import ujson  # поскольку он показывает большую производительность по сравнению с json
import os


# ----------------------------------------------------------------------------------------------------------------------
# Структура *.json файла SAMA (Романа Хабарова)
#
# "path_to_images": "F:\\data_sets\\test_oil_ref\\"
# data["path_to_images"] = "only_one_path"
#  ├- data["images"] = {"one.jpg":[ ], "two.jpg":[ ], ... , "n.jpg":[ ]}
#  |                               └- {shapes: [ ] }
#  |                                            └- "cls_num":, "id":, "points":[ ]
#  |                                                                            └- [ [x1, y1], [x2, y2], ... [xn, yn] ]
#  ├- data["labels"] = ["name_one", "name_two", ... , "name_n"]
#  └- data["labels_color"] = {"name_one", "name_two", ... , "name_n": [ ] }
#                                                                      └- label [r, g, b]
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
# ----------------------------------------------------------------------------------------------------------------------

# TODO: сделать функцию считывания ЛРМ изо всех файлов *.MAP, ее усреднения и записи в файл SAMA

def convert_to_sama(input_files, output_file):
    """
    Конвертация файлов проекта LabelMe в проект SAMA
    """
    data = dict()
    data["path_to_images"] = os.path.dirname(input_files[0])  # такой же, как у первого файла
    images = {}  # изображения
    class_numbers = {}  # {имя класса:номера класса} считая с 0; создаётся динамически
    labels_colors = {}  # цвета меток
    labels_set = set()  # метки: перечень уникальных меток
    id_count = -1  # начинаем с -1, т.к. на первой итерации +1 и будет id:0.

    for item in input_files:  # начинаем обход перечня полученных файлов
        list_shapes = []
        label_me_data = load(item)
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

    for label in labels_set:  # для всех меток...
        labels_colors[label] = random_color()  # ...формируем случайные цвета
    data["images"] = images
    data["labels"] = list(class_numbers.keys())  # ключи class_numbers содержат список меток по порядку
    data["labels_color"] = labels_colors
    save(output_file, data, 'w+')
    return True


def random_color():  # генерируем случайные цвета
    rand_col = [randint(0, 255), randint(0, 255), randint(0, 255), 120]  # оттенок alfa по умолчанию оставляем 120
    return rand_col


def load(json_path):
    with open(json_path, 'r', encoding='utf8') as f:
        data = ujson.load(f)
        return data


def save(json_path, data, mode='w'):
    with open(json_path, 'w+') as f:
        ujson.dump(data, f)


if __name__ == '__main__':
    pass
    # convert_labelme_to_sama(test_list, "F:/data_sets/output_dir/test_for_merge2/small_test/_temp.json")
