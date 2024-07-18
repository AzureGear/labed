import numpy as np
import os
import ujson
import re


def create_blank_image(self):
    return {"shapes": [], "lrm": None, 'status': 'empty'}


class DatasetSAMAHandler:
    """
    Реализация Романа Хабарова. Класс для работы с данными проекта. Осуществляет хранение данных разметки словарем.
    """

    def __init__(self, filename=None):
        # Инициализация
        self.data = dict()
        self.data["path_to_images"] = ""
        self.data["images"] = {}
        self.data["labels"] = []
        self.data["labels_color"] = {}
        self.data["description"] = ""  # Az+: описание проекта
        self.filename = None
        self.is_loaded = False
        self.is_correct_file = False

        # проверка реальности
        if filename is None:
            return
        if not os.path.exists(filename):
            return

        # загрузка и простая проверка данных
        self.load(filename)

    def load(self, json_path):  # загрузка проекта через ujson
        self.is_correct_file = False
        self.is_loaded = False
        try:
            with open(json_path, 'r') as f:
                self.data = ujson.load(f)
                if self.check_json(self.data):
                    self.is_correct_file = True
                    self.filename = json_path
                    self.update_ids()
                self.is_loaded = True

        except ujson.JSONDecodeError:
            print(f"Файл {json_path} пустой, либо содержит некорректные данные.")
            return None

    @staticmethod
    def check_json(json_project_data):
        for field in ["path_to_images", "images", "labels", "labels_color"]:
            if field not in json_project_data:
                return False
        return True

    def calc_dataset_balance(self):
        labels = self.get_labels()
        labels_nums = {}
        for im in self.data['images'].values():
            for shape in im['shapes']:
                cls_num = shape['cls_num']
                label_name = labels[cls_num]
                if label_name not in labels_nums:
                    labels_nums[label_name] = 1
                else:
                    labels_nums[label_name] += 1
        return labels_nums


    def save(self, json_path):
        with open(json_path, 'w', encoding='utf8') as f:
            ujson.dump(self.data, f)

    def update_ids(self):
        if not self.data["images"]:
            return
        id_num = 0
        for im in self.data['images'].values():
            for shape in im['shapes']:
                shape['id'] = id_num
                id_num += 1

    def set_data(self, data):
        self.data = data
        self.is_loaded = True

    def set_image_lrm(self, image_name, lrm):
        im = self.get_image_data(image_name)  # im = {shapes:[], lrm:float, status:str}
        if im:
            im["lrm"] = round(lrm, 6)
        else:
            im = create_blank_image()
            im['lrm'] = round(lrm, 6)
            self.data["images"][image_name] = im

    def get_image_status(self, image_name):
        im = self.get_image_data(image_name)  # im = {shapes:[], lrm:float, status:str}
        if im:
            status = im.get("status", None)
            if status:
                return status
            self.set_image_status(image_name, 'empty')
            return 'empty'

    def get_all_images_info(self):
        res = {}
        for image_name, im_data in self.data["images"].items():
            status = im_data.get("status", "empty")
            last_user = im_data.get("last_user", "unknown")

            res[image_name] = {"status": status, "last_user": last_user}
        return res

    def set_image_status(self, image_name, status):
        if status not in ['empty', 'in_work', 'approve']:
            return
        im = self.get_image_data(image_name)  # im = {shapes:[], lrm:float, status:str}
        if im:
            im["status"] = status
            self.data["images"][image_name] = im
        else:
            im = create_blank_image()
            im["status"] = status
            self.data["images"][image_name] = im

    def get_image_last_user(self, image_name):
        im = self.get_image_data(image_name)
        if im:
            return im.get("last_user", None)

    def set_image_last_user(self, image_name, last_user):
        im = self.get_image_data(image_name)
        if im:
            im["last_user"] = last_user
            self.data["images"][image_name] = im
        else:
            im = create_blank_image()
            im["last_user"] = last_user
            self.data["images"][image_name] = im

    def set_lrm_for_all_images(self, lrms_data, no_image_then_continue=False):
        """Az: установка ЛРМ для изображений функция Романа, с дополнением"""
        set_names = []
        unset_names = []
        im_names_in_folder = os.listdir(self.get_image_path())
        for image_name in lrms_data:  # 1. Цикл по объектам в lrms_data
            if image_name not in im_names_in_folder:
                unset_names.append(image_name)
            else:

                lrm = lrms_data[image_name]  # Az: lrms_data = {"image_name" : lrm: float }
                im = self.get_image_data(image_name)  # im = {shapes:[], lrm:float, status:str}
                if im:
                    im["lrm"] = round(lrm, 6)
                    self.data["images"][image_name] = im
                else:
                    if no_image_then_continue:
                        continue  # Az+: если есть изображения, о которых нет записей в датасете
                    im = create_blank_image()
                    im['lrm'] = round(lrm, 6)
                    self.data["images"][image_name] = im

                set_names.append(image_name)

        return set_names, unset_names

    def set_labels(self, labels):
        self.data["labels"] = labels

    def set_path_to_images(self, path):
        self.data["path_to_images"] = path

    def set_blank_data_for_images_names(self, images_names):
        im_names_in_folder = os.listdir(self.get_image_path())
        for im_name in images_names:
            if im_name in im_names_in_folder:
                im = self.get_image_data(im_name)
                if not im:
                    im = create_blank_image()
                    self.data["images"][im_name] = im

    def set_label_color(self, cls_name, color=None, alpha=None):
        """Замена цвета. Az+ Переписана для своих задач"""
        new_alpha = alpha
        if not alpha:
            old_color = self.data["labels_color"][cls_name]
            new_alpha = old_color[3]
        color = [color[0], color[1], color[2], new_alpha]
        self.data["labels_color"][cls_name] = color

    def set_labels_colors(self, labels_names, rewrite=False):
        if rewrite:
            self.data["labels_color"] = {}

        for label_name in labels_names:
            if label_name not in self.data["labels_color"]:
                self.set_label_color(label_name)

    def set_labels_names(self, labels):
        self.data["labels"] = labels

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

    def set_image_data(self, image_name, image_data):
        self.data["images"][image_name] = image_data

    def get_data(self):
        return self.data

    def get_label_color(self, cls_name):
        return self.data["labels_color"].get(cls_name, None)

    def get_label_num(self, label_name):
        for i, label in enumerate(self.data["labels"]):
            if label == label_name:
                return i
        return -1

    def get_images_num(self):
        return len(self.data["images"])

    def get_colors(self):
        return [tuple(self.data["labels_color"][key]) for key in
                self.data["labels_color"]]

    def get_image_data(self, image_name):
        return self.data["images"].get(image_name, None)

    def get_labels(self):
        return self.data["labels"]

    def get_labels_count(self):  # Az+: общее количество меток
        count = 0
        for image_data in self.data["images"].values():
            for shape in image_data["shapes"]:
                count += 1
        return count

    def get_label_name(self, cls_num):
        if cls_num < len(self.data["labels"]):
            return self.data["labels"][cls_num]

    def get_image_lrm(self, image_name):
        im = self.get_image_data(image_name)  # im = {shapes:[], lrm:float, status:str}
        if im:
            return im.get("lrm", None)

    def get_image_path(self):
        return self.data["path_to_images"]

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

    def change_cls_num_by_ids(self, image_name, lbl_ids, new_cls_num):
        im = self.get_image_data(image_name)  # im = {shapes:[], lrm:float, status:str}
        new_shapes = []

        for shape in im['shapes']:
            if shape['id'] in lbl_ids:
                new_shape = shape
                new_shape["cls_num"] = new_cls_num
                new_shapes.append(new_shape)
            else:
                new_shapes.append(shape)
        im['shapes'] = new_shapes
        self.data["images"][image_name] = im

    def rename_color(self, old_name, new_name):
        if old_name in self.data["labels_color"]:
            color = self.data["labels_color"][old_name]
            self.data["labels_color"][new_name] = color
            del self.data["labels_color"][old_name]

    def change_name(self, old_name, new_name):
        self.rename_color(old_name, new_name)
        labels = []
        for i, label in enumerate(self.data["labels"]):
            if label == old_name:
                labels.append(new_name)
            else:
                labels.append(label)
        self.data["labels"] = labels

    def delete_label_color(self, label_name):
        if label_name in self.data["labels_color"]:
            del self.data["labels_color"][label_name]

    def delete_label(self, label_name):
        labels = []
        for label in self.data['labels']:
            if label != label_name:
                labels.append(label)
        self.set_labels(labels)

    def delete_image(self, image_name):
        if image_name in self.data["images"]:
            del self.data["images"][image_name]

    def delete_data_by_class_name(self, cls_name):
        name_to_name_map = {}  # Конвертер старого имени в новое
        old_name_to_num = {}
        new_labels = []

        for i, label in enumerate(self.data["labels"]):

            if label != cls_name:
                name_to_name_map[label] = label
                new_labels.append(label)
            else:
                name_to_name_map[label] = None

            old_name_to_num[label] = i

        new_name_to_num = {}
        for i, label in enumerate(new_labels):
            new_name_to_num[label] = i

        num_to_num = {}
        for label, old_num in old_name_to_num.items():
            new_name = name_to_name_map[label]
            if new_name:
                new_num = new_name_to_num[new_name]
                num_to_num[old_num] = new_num
            else:
                num_to_num[old_num] = -1

        for im_name, image in self.data["images"].items():  # image = {shapes:[], lrm:float, status:str}
            new_shapes = []
            for shape in image["shapes"]:

                new_num = num_to_num[shape["cls_num"]]
                if new_num != -1:
                    shape_new = {}
                    shape_new["cls_num"] = new_num
                    shape_new["points"] = shape["points"]
                    shape_new["id"] = shape["id"]
                    new_shapes.append(shape_new)

            image["shapes"] = new_shapes
            self.data["images"][im_name] = image

        self.set_labels(new_labels)

        self.delete_label_color(cls_name)

    def delete_data_by_class_number(self, cls_num):

        for im_name, image in self.data["images"].items():  # image = {shapes:[], lrm:float, status:str}
            new_shapes = []
            for shape in image["shapes"]:
                if shape["cls_num"] < cls_num:
                    new_shapes.append(shape)
                elif shape["cls_num"] > cls_num:
                    shape_new = {}
                    shape_new["cls_num"] = shape["cls_num"] - 1
                    shape_new["points"] = shape["points"]
                    shape_new["id"] = shape["id"]
                    new_shapes.append(shape_new)

            image["shapes"] = new_shapes
            self.data["images"][im_name] = image

    def change_data_class_from_to(self, from_cls_name, to_cls_name):  # Az: слияние одного класса в другой

        name_to_name_map = {}  # Конвертер старого имени в новое
        old_name_to_num = {}
        new_labels = []

        for i, label in enumerate(self.data["labels"]):

            if label != from_cls_name:
                name_to_name_map[label] = label
                new_labels.append(label)
            else:
                name_to_name_map[label] = to_cls_name

            old_name_to_num[label] = i

        new_name_to_num = {}
        for i, label in enumerate(new_labels):
            new_name_to_num[label] = i

        num_to_num = {}
        for label, old_num in old_name_to_num.items():
            new_name = name_to_name_map[label]
            new_num = new_name_to_num[new_name]
            num_to_num[old_num] = new_num

        for im_name, image in self.data["images"].items():  # image = {shapes:[], lrm:float, status:str}
            new_shapes = []
            for shape in image["shapes"]:
                shape_new = {}
                shape_new["cls_num"] = num_to_num[shape["cls_num"]]
                shape_new["points"] = shape["points"]
                shape_new["id"] = shape["id"]
                new_shapes.append(shape_new)

            image["shapes"] = new_shapes
            self.data["images"][im_name] = image

        self.set_labels(new_labels)

        self.delete_label_color(from_cls_name)

    def create_images_labels_subdirs(self, export_dir):
        images_dir = os.path.join(export_dir, 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        labels_dir = os.path.join(export_dir, 'labels')
        if not os.path.exists(labels_dir):
            os.makedirs(labels_dir)

        return images_dir, labels_dir

    def clear_not_existing_images(self):
        images = {}
        im_path = self.get_image_path()
        for filename, im in self.data['images'].items():
            if os.path.exists(os.path.join(im_path, filename)):
                images[filename] = im
            else:
                print(f"Checking files: image {filename} doesn't exist")
        self.data['images'] = images

    def calc_stat(self):  # Реализация Романа Хабарова + кое-что из моего
        labels = self.data['labels']
        stats = {lbl: {'count': 0, 'percent': 0, 'frequency': 0, 'size': {'mean': 0, 'second': 0, 'std': 0}} for lbl in
                 labels}
        frequency = {label: 0 for label in labels}  # Az+: создаем словарь "имя метки: число появлений метки"
        total_label_count = 0
        size_mass = {lbl: [] for lbl in labels}  # Az: создаем словарь "имя метки: []"
        for im in self.data['images'].values():
            appears = {label: 0 for label in labels}  # Az+: строим вектор флагов. Никаких меток еще не встречали.
            for shape in im['shapes']:
                cls_num = shape['cls_num']  # Az: номер метки (класс)
                if cls_num > len(labels) - 1:  # Az?Question: зачем здесь "-1"?
                    continue
                label_name = labels[cls_num]  # Az: имя метки (название)
                if label_name in appears:
                    appears[label_name] = 1  # Az+: меняем флаг появления
                xs = [x for x, y in shape['points']]  # Az: массив точек x
                ys = [y for x, y in shape['points']]  # Az: массив точек y
                width = max(xs) - min(xs)  # Az: находим ширину...
                height = max(ys) - min(ys)  # Az: ...и высоту
                size = max(width, height)  # находим габариты

                size_mass[label_name].append(size)

                stats[label_name]['count'] += 1
                total_label_count += 1

            # Az+: Суммируем прошлые результаты встречаемости с текущими
            for key in appears:
                if key in frequency:
                    frequency[key] += appears[key]

        number_of_images = len(self.data['images'])
        for label_name in labels:
            if total_label_count == 0:
                stats[label_name]['percent'] = 0
            else:
                stats[label_name]['percent'] = float(stats[label_name]['count']) / total_label_count * 100
            mass = np.array(size_mass[label_name])

            if len(mass) > 0:
                stats[label_name]['size']['mean'] = mass.mean()
                stats[label_name]['size']['std'] = mass.std()

            stats[label_name]['frequency'] = float(frequency[label_name] / number_of_images * 100)

        return stats

    def get_sort_data(self):
        """
        Az+: Извлечение данных для класса сортировщика.
        {"image_name":str, [label1_counts:int, label2_counts:int, ... ] }
        """
        data = {}
        label_n = len(self.get_labels())
        for im_name, image in self.data["images"].items():  # смотрим каждое изображение
            label_counts = [0] * label_n  # делаем лист по количеству классов/меток
            for shape in image["shapes"]:  # по каждому объекту
                label_counts[shape["cls_num"]] += 1  # добавляем в столбец, в соответствии с классом/меткой
            data[im_name] = label_counts
        return data
        values = list(data.values())
        # преобразуем значения в списки
        result = list(map(sum, zip(*values)))
        print(result)

    def get_project_description(self):
        """Az+: извлечение описания проекта"""
        return self.data.get("description")

    def set_project_description(self, text):
        """Az+: занесение описания проекта"""
        self.data["description"] = text

    def get_model_data(self, object_name=None, label_name=None, count=-1, pattern=r"^([^_]+)_([^_]+)"):
        """Az+: Извлечение строк для заполнения таблицы модели"""
        if self.data is None:
            return
        if object_name == "< all >":
            object_name = None  # устанавливаем пустыми, будем собирать все объекты
        if label_name == "< all labels >":
            label_name = None  # устанавливаем пустыми, будем собирать все метки

        data = []
        row_count = 0
        for im_name, image in self.data["images"].items():
            for shape in image["shapes"]:
                if count > 0:  # если стоит счетчик
                    if count < row_count:
                        break
                obj = ""  # изначально печально
                label = self.get_label_name(shape["cls_num"])
                match = re.search(pattern, im_name)  # ищем имя объекта

                if obj is not None:  # собираем сокращение "объекта", у нас общий сбор
                    obj = match.group(0)

                if object_name is None and label_name is None:  # получение всего перечня
                    row = [obj, im_name, label, str(shape["id"])]
                    data.append(row)
                    row_count += 1
                elif object_name is None and label_name is not None:  # фильтр по метке
                    if label == label_name:
                        row = [obj, im_name, label, str(shape["id"])]
                        data.append(row)
                        row_count += 1
                elif object_name is not None and label_name is None:  # фильтр по классу
                    if obj == object_name:
                        row = [obj, im_name, label, str(shape["id"])]
                        data.append(row)
                        row_count += 1
                elif object_name is not None and label_name is not None:  # фильтр и по метке и по классу
                    if obj == object_name and label == label_name:
                        row = [obj, im_name, label, str(shape["id"])]
                        data.append(row)
                        row_count += 1
        return data

    def get_group_objects(self, pattern=r"^([^_]+)_([^_]+)"):
        """
        Az+: Извлечение перечня объектов. Под объектами понимаются разновременные изображения одного и того же объекта,
        например в для изображения '138_DEU_2021-06_003.jpg' таким объектом будет '138_DEU'. Если использовать
        регулярные выражения, то шаблоном поиска будет r"^([^_]+)_([^_]+)", т.е. любая последовательность символов,
        с начала строки (^) и состоящей из 2 групп, разделенных символом "_".
        """
        objects = []
        for image in self.data["images"].keys():
            match = re.search(pattern, image)
            if match is not None:
                if match.group(0) not in objects:
                    objects.append(match.group(0))
        return objects


if __name__ == '__main__':
    proj_path = "D:/data_sets/nuclear_power_stations/project.json"
    proj = DatasetSAMAHandler(proj_path)
    print(proj.get_labels())
    print(proj.get_all_images_info())
