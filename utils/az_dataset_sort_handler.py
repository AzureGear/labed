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

    def get_images_names(self, table_name):
        return self.data[table_name].keys()

    def load_from_file(self, json_path):  # загрузка данных в класс из файла *.sort (по факту json)
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
