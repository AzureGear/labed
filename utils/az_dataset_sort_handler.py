import ujson


class DatasetSortHandler:
    """
    Работа с данными таблицы фильтрата и статистике фильтрата (сортировка, разбиение на train/val).
    Сохраняются и загружаются файлы *.sort (по факту json)
    """

    def __init__(self):
        # инициализация
        self.data = dict()
        self.statistic = dict()
        self.data["path_to_images"] = ""
        self.data["labels"] = {}  # структура {int1 : "name1", int2 : name2, ...}
        self.data["full"] = {}  # общая структура {"image_name":str, [label1_counts:int, label2_counts:int, ... ] }
        self.data["unsort"] = {}
        self.data["train"] = {}
        self.data["val"] = {}
        self.data["test"] = {}
        self.statistic["full"] = {}
        self.statistic["train"] = {}
        self.statistic["val"] = {}
        self.statistic["test"] = {}
        self.is_correct_file = False
        self.export_data = []

    @staticmethod
    def check_json(json_project_data):  # примитивная проверка на наличие данных
        for field in ["path_to_images", "labels", "full", "unsort", "train", "val", "test"]:
            if field not in json_project_data:
                return False
        return True

    def save(self, json_path):
        with open(json_path, 'w', encoding='utf8') as f:
            ujson.dump(self.data, f)

    def create_new_sort_file(self, sama_data):  # создание нового проекта сортировщика по данным SAMA
        self.data["path_to_images"] = sama_data.data["path_to_images"]

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
        self.calc_init_stats()  # рассчитываем статистику для исходных данных self.data[full]
        return self.data

    def load_from_file(self, json_path):
        """Загрузка данных в класс из файла *.sort (по факту json)"""
        with open(json_path, 'r') as f:
            self.data = ujson.load(f)
            if self.check_json(self.data):
                self.is_correct_file = True
                self.calc_init_stats()

    def move_rows_by_images_names(self, start_dict, dest_dict, images_names, use_group=False):
        """Перемещение записей из start_dict (начального) словаря в dest_dict (конечный)"""
        for item in images_names:
            try:
                self.data[dest_dict][item] = self.data[start_dict].pop(item)
            except KeyError:  # если ключ в start_dict не существует сообщаем себе и продолжим работу
                print(f"Key error при перемещении таблицы в таблице сортировщика значения {item}")
                continue

        self.update_stats()  # обновление статистики

    def get_rows_labels_headers(self):
        """Возвращаем список наименований меток, где порядковый номер элемента соответствует метке"""
        return [self.data["labels"][str(i)] for i in range(self.get_cls_count())]

    def clear_train_val_test(self):
        """Очистка выборок"""
        self.data["train"] = {}
        self.data["val"] = {}
        self.data["test"] = {}

    def set_data(self, table_name, data):
        """Установка новых значений таблиц train, val или test"""
        self.data[table_name] = data

    def get_images_names_train_val_test(self):
        """Возвращаем имена изображений из словарей train, val и test"""
        merged = {**self.data["train"], **self.data["val"], **self.data["test"]}
        return merged.keys()

    def get_images_names(self, dict_name):
        """Возвращаем имена изображений из выбранного (dict_name) словаря"""
        return self.data[dict_name].keys()

    def calc_init_stats(self):
        """Рассчитывает и записывает статистику по всем изображениям и меткам в self.statistic["full"]"""
        full = self.data.get("full", [])
        if full:
            images_count, class_sum = self.sum_dict_values(full, self.get_cls_count())
            init_stats = {"images_count": images_count, "class_sum": class_sum}
            # статистика обо всех объектах (выношу отдельно, чтобы не было пустых пересчётов)
            self.statistic["full"] = init_stats
            self.update_stats()  # расчет статистики для таблиц Train, Val, Test

    @staticmethod
    def sum_dict_values(the_dict, count_cls):
        """Поэлементное суммирование значений внутри словаря для списка классов типа [0, 0, 1, 4, 0, 2...]"""
        summ = [0] * count_cls  # нулевой список result по количеству классов
        images_count = 0
        for key, value in the_dict.items():  # обходим весь словарь
            images_count += 1  # считаем количество изображений и...
            for i, val in enumerate(value):  # ...каждый элемент класса...
                summ[i] += val  # ...суммируем в пределах его класса (т.е. [0, 4, 2] + [1, 0, 7] = [1, 4, 9])
        return images_count, summ

    def get_cls_count(self):
        """Определение количества классов"""
        return len(next(iter(self.data["full"].items()))[1])

    def update_stats(self):
        """Обновление статистики"""
        # Статистика имеет вид (пример): строки = число классов + 2; столбцы = 4
        #                   | Train |   Val  |  Test  | Total |
        # Всего меток       |  11%  |   4%   |   0%   |  15%  |
        # Изображений всего |  280  |   119  |   0    |  19%  |
        # Class1_name       |  42   |   24   |   0    |  52%  |
        # Class2_name       |  7    |  ...
        # ...

        cls_count = self.get_cls_count()
        if not self.statistic["full"]:  # изображений и меток нет, расчет не имеет смысла
            return
        # 1. Собираем статистику по каждому из разделов
        dict_names = ["train", "val", "test"]  # будем использовать имена разделов
        for dict_name in dict_names:
            if self.data[dict_name]:  # проверяем, имеются ли данные в словаре?
                images_count, class_sum = self.sum_dict_values(self.data[dict_name], cls_count)
            else:  # иначе это нулевой список
                class_sum = [0] * cls_count
                images_count = 0  # изображения отсутствуют
            # записываем результаты статистики:
            self.statistic[dict_name] = {"images_count": images_count, "class_sum": class_sum}

        # делаем массив-пустышку для статистики
        result = [[0] * 4 for _ in range(cls_count + 2)]

        # 2. Считаем их сумму и количество изображений
        summ_train_val_test_cls = [0] * cls_count
        summ_train_val_test_img = 0
        for y, dict_name in enumerate(dict_names):
            result[1][y] = self.statistic[dict_name]["images_count"]  # статистика изображений
            summ_train_val_test_img += result[1][y]  # общая сумма снимков
            # x и y: сначала строки (x), затем столбцы/элементы (y)
            for x in range(cls_count):
                # сумма по каждому классу в процентах
                val = round(self.statistic[dict_name]["class_sum"][x] / self.statistic["full"]["class_sum"][x] * 100, 1)
                result[x + 2][y] = val
                summ_train_val_test_cls[x] += val
        sum_total = 0
        summ_total_train = 0
        summ_total_val = 0
        summ_total_test = 0
        for i in range(cls_count):
            result[i + 2][3] = round(summ_train_val_test_cls[i], 1)
            sum_total += round(summ_train_val_test_cls[i], 1)
            summ_total_train += result[i + 2][0]
            summ_total_val += result[i + 2][1]
            summ_total_test += result[i + 2][2]
        # итого изображений
        result[1][3] = round((summ_train_val_test_img / self.statistic["full"]["images_count"]) * 100, 1)
        # итого меток
        result[0][0] = round(summ_total_train / cls_count, 1)
        result[0][1] = round(summ_total_val / cls_count, 1)
        result[0][2] = round(summ_total_test / cls_count, 1)
        result[0][3] = round(sum_total / cls_count, 1)

        self.export_data = result
        return
        # # 3. Рассчитываем колонку с "итоговыми" данными (и заменяем на проценты количество)
        # summ_total = 0
        # summ_total_train = 0
        # summ_total_val = 0
        # summ_total_test = 0
        #
        # for i in range(cls_count):
        #     # итоговое количество объектов по каждой метке
        #     class_percent = (summ_train_val_test_cls[i] / self.statistic["full"]["class_sum"][i]) * 100
        #     result[i + 2][3] = round(class_percent, 1)
        #     # статистика
        #     summ_total_train += (result[i + 2][0] / self.statistic["full"]["class_sum"][i]) * 100
        #     summ_total_val += (result[i + 2][1] / self.statistic["full"]["class_sum"][i]) * 100
        #     summ_total_test += (result[i + 2][2] / self.statistic["full"]["class_sum"][i]) * 100
        #     # for j in range(dict_names):
        #     #     self.
        #     summ_total += class_percent  # итоговая сумма в процентах по всем классам
        # # итого изображений
        # result[1][3] = round((summ_train_val_test_img / self.statistic["full"]["images_count"]) * 100, 0)
        # # итого меток
        # result[0][3] = round(summ_total / cls_count, 0)
        # result[0][0] = round(summ_total_train / cls_count, 0)
        # result[0][1] = round(summ_total_val / cls_count, 0)
        # result[0][2] = round(summ_total_test / cls_count, 0)
        #
        # # сохраняем статистику
        # self.export_data = result
