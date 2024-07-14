import ujson


class DatasetSortHandler:
    """
    Работа с данными таблицы фильтрата и статистике фильтрата (сортировка, разбиение на train/val).
    Сохраняются и загружаются файлы *.sort (по факту json)
    """

    def __init__(self):
        # инициализация
        self.data = dict()
        self.data["path_to_images"] = ""
        self.data["labels"] = {}  # структура {int1 : "name1", int2 : name2, ...}
        self.data["full"] = {}  # общая структура {"image_name":str, [label1_counts:int, label2_counts:int, ... ] }
        self.data["unsort"] = {}
        self.data["train"] = {}
        self.data["val"] = {}
        self.data["test"] = {}
        self.is_correct_file = False

    def create_new_sort_file(self, sama_data):  # создание нового проекта сортировщика по данным SAMA
        self.data["path_to_images"] = sama_data.data["path_to_images"]
        self.data["labels"] = sama_data.data["labels"]

        labels = {}  # заполняем метки
        for i in range(len(sama_data.get_labels())):
            labels[i] = sama_data.get_label_name(i)
        self.data["labels"] = labels

        # формируем перечень изображений
        self.data["full"] = sama_data.get_sort_data()  # получаем основную информацию
        self.data["unsort"] = self.data["full"]
        self.data["train"] = {}
        self.data["val"] = {}
        self.data["test"] = {}
        return self.data

    def move_rows_by_images_names(self, start_dict, dest_dict, images_names):
        """Перемещение записей словаря из start_dict (начального) словаря в dest_dict (конечный)"""
        for item in images_names:
            try:
                self.data[dest_dict][item] = self.data[start_dict].pop(item)
            except KeyError:  # если ключ в start_dict не существует сообщаем себе и продолжим работу
                print(f"Key error при перемещении таблицы в таблице сортировщика значения {item}")
                continue

        self.update_stats()  # обновление статистики

    def get_images_names_train_val_test(self):
        """Возвращаем имена изображений из словарей train, val и test"""
        merged = {**self.data["train"], **self.data["val"], **self.data["test"]}
        return merged.keys()

    def get_images_names(self, dict_name):
        """Возвращаем имена изображений из выбранного (table_name) словаря"""
        return self.data[dict_name].keys()

    def load_from_file(self, json_path):
        """Загрузка данных в класс из файла *.sort (по факту json)"""
        try:
            with open(json_path, 'r') as f:
                self.data = ujson.load(f)
                if self.check_json(self.data):
                    self.is_correct_file = True
        except ujson.JSONDecodeError:
            print(f"Файл {json_path} пустой, либо содержит некорректные данные.")
            return None

    @staticmethod
    def check_json(json_project_data):  # примитивная проверка на наличие данных
        for field in ["path_to_images", "labels", "full", "unsort", "train", "val", "test"]:
            if field not in json_project_data:
                return False
        return True

    def save(self, json_path):
        with open(json_path, 'w', encoding='utf8') as f:
            ujson.dump(self.data, f)

    def sum_dict_values(self, the_dict, count_cls):
        """Поэлементное суммирование значений внутри словаря для списка классов типа [0, 0, 1, 4, 0, 2...]"""
        summ = [0] * count_cls  # нулевой список result по количеству классов
        for key, value in the_dict.items():  # обходим весь словарь и...
            for i, val in enumerate(value):  # ...каждый элемент класса...
                summ[i] += val  # ...суммируем в пределах его класса (т.е. [0, 4, 2] + [1, 0, 7] = [1, 4, 9])
        return summ

    def update_stats(self):
        """Обновление статистики"""
        if not self.data["full"]:
            # TODO: сделать что-то если для датасета нет никаких значений
            pass
        count_classes = len(next(iter(self.data["full"].items()))[1])  # определяем количество классов
        dicts = [self.data["unsort"], self.data["train"], self.data["val"], self.data["test"]]
        if self.data["unsort"]:
            class_sum = self.sum_dict_values(self.data["unsort"], count_classes)
        else:
            class_sum = [0] * count_classes  # иначе это нулевой список

