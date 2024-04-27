# import json
import ujson  # поскольку он показывает большую производительность по сравнению с json
import os
import sys
import re

# ----------------------------------------------------------------------------------------------------------------------
# Структура файла SAMA (Романа Хабарова)
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
# Структура файла LabelMe (Michael Pitidis, Hussein Abdulwahid, Kentaro Wada)
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
#
# TODO: динамически добавлять объектов в список; сделать списки данных
# TODO: сделать функцию считывания ЛРМ из файла *.MAP и записи её в файл SAMA

test_list = ['D:/data_sets/oil_refinery/test_for_merge2/487_USA_2015-11.json',
             'D:/data_sets/oil_refinery/test_for_merge2/487_USA_2022-01.json',
             'D:/data_sets/oil_refinery/test_for_merge2/487_USA_2015-12.json',
             'D:/data_sets/oil_refinery/test_for_merge2/487_USA_2018-03.json',
             'D:/data_sets/oil_refinery/test_for_merge2/487_USA_2017-01.json',
             'D:/data_sets/oil_refinery/test_for_merge2/487_USA_2012-10.json',
             'D:/data_sets/oil_refinery/test_for_merge2/487_USA_2011-11.json']


# labels_nums = {}
#        for im in self.data['images'].values():
#            for shape in im['shapes']:
#                cls_num = shape['cls_num']
#                label_name = labels[cls_num]
#                if label_name not in labels_nums:
#                    labels_nums[label_name] = 1
#                else:
#                    labels_nums[label_name] += 1
#        return labels_nums


def convert_labelme_to_sama(input_files, output_file):
    """ Реальный пример файла
    "path_to_images":"F:\\data_sets\\test_oil_ref\\",
    	"images": {
    			"154s.jpg": {
    					  "shapes": [
    							    {"cls_num": 0,
    							 	"id":0,
    							 	"points": [
    									    [708.9772254617831,803.994791760785],
    									    [725.0571212969988,829.3328094405188],
    									    [653.4284943946743,875.6234186631094],
    									    [636.3740594179304,851.2599401249038]
    									      ]
    							    },
    								{"cls_num":1, "id":0, "points": [[12.291923, 11.3992912], ... ] }
    							   ],
    					  "lrm":0.20257005180040008,
    					  "status":"empty",
    					  "last_user": null
    					   }
    		     },
    	"labels": ["building"],
    	"labels_color":{ "building": [170,0,0,120] }
    """
    data = dict()
    data["path_to_images"] = os.path.dirname(input_files[0])  # такой же, как у первого файла
    images = {}  # изображения
    # начинаем обход перечня полученных файлов
    labels_colors = {}  # цвета меток
    labels = []  # метки
    labels_set = set()  # перечень уникальных меток
    for item in input_files:
        shapes = {}  # каждый новый файл обновляем
        label_me_data = load(item)
        img_name = label_me_data["imagePath"]  # формируем имя файла (можно и через os.path.basename(image))
        lm_shapes = label_me_data["shapes"]  # список формата labelMe, где список [ "label", "points" ... ]
        for lm_shp_dict in lm_shapes:
            # print(type(lm_shapes[0]))
            # return
            labels_set.add(lm_shp_dict["label"])
        images[img_name] = create_blank_image()  # создаём пустую заготовку для "images"
    data["images"] = images
    data["labels"] = list(labels_set)
    data["labels_color"] = labels_colors
    save(output_file, data, 'w+')
    return True


def get_all_images_info():
    res = {}
    for image_name, im_data in data["images"].items():
        status = im_data.get("status", "empty")
        last_user = im_data.get("last_user", "unknown")

        res[image_name] = {"status": status, "last_user": last_user}
    return res


def add_shapes_to_images(self, dicts_with_shapes):
    """
    Добавить данные по полигонам. Не затираются предыдущие полигоны, а добавляются поверх имеющихся
    dicts_with_shapes - { image_name1: {'shapes':[...]}, image_name2: {'shapes':[...]}, ...}
    """
    for im_name, im_data in dicts_with_shapes.items():
        if im_name in self.data['images']:
            for shape in im_data['shapes']:  # im_data в формате {"shapes": [...]}
                self.data["images"][im_name]['shapes'].append(shape)
        else:
            im_blank = create_blank_image()
            for shape in im_data['shapes']:  # im_data в формате {"shapes": [...]}
                im_blank['shapes'].append(shape)
            self.data["images"][im_name] = im_blank


def create_blank_image():
    return {"shapes": [], "lrm": None, 'status': 'empty'}


def load(json_path):
    with open(json_path, 'r', encoding='utf8') as f:
        data = ujson.load(f)
        return data


def save(json_path, data, mode='w'):
    with open(json_path, 'w+') as f:
        ujson.dump(data, f)


if __name__ == '__main__':
    convert_labelme_to_sama(test_list, "d:/data_sets/oil_refinery/test_for_merge2/_temp.json")
