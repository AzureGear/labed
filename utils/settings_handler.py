from PyQt5 import QtCore
from utils import config


class AppSettings:
    """
    Взаимодействие с хранением, записью и сбросом настроек в реестре
    """

    def __init__(self):
        self.settings = QtCore.QSettings(config.ORGANIZATION, config.APPLICATION)

    def read_ui_stack_widget_cur_tab(self):
        """Активный виджет для боковой панели [r]"""
        return self.settings.value('ui/ui_stack_widget_current_tab', 0)

    def write_ui_stack_widget_cur_tab(self, ui_tab):
        """Активный виджет для боковой панели [w]"""
        self.settings.setValue('ui/ui_stack_widget_current_tab', ui_tab)

    def read_ui_proc_page(self):
        """Активная страница для 1 виджета, если он выбран [r]"""
        return self.settings.value('ui/ui_proc_page', 3)

    def write_ui_proc_page(self, proc_page):
        """Активная страница для 1 виджета, если он выбран [w]"""
        self.settings.setValue('ui/ui_proc_page', proc_page)

    def read_lang(self):
        """Язык [r] """
        return self.settings.value('ui/language', 'English')

    def write_lang(self, lang):
        """Язык [w]"""
        self.settings.setValue('ui/language', lang)

    def read_ui_theme(self):
        """Тема интерфейса [r]"""
        return self.settings.value('ui/theme', 'light')

    def write_ui_theme(self, theme):
        """Тема интерфейса [w]"""
        self.settings.setValue('ui/theme', theme)

    def read_ui_position(self):
        """Позиция, размер и состояние окна приложения [r]"""
        # if len(screeninfo.get_monitors()) == 1: # TODO: что если отключили монитор?
        position = self.settings.value('ui/base_gui_position', QtCore.QPoint(250, 250))
        size = self.settings.value('ui/base_gui_size', QtCore.QSize(900, 565))
        state = self.settings.value('ui/base_gui_state', QtCore.Qt.WindowState.WindowNoState)  # QWindow
        return position, size, state

    def write_ui_position(self, position, size, state):
        """Позиция, размер и состояние окна приложения [w]"""
        self.settings.setValue('ui/base_gui_position', position)
        self.settings.setValue('ui/base_gui_size', size)
        self.settings.setValue('ui/base_gui_state', state)

    def read_last_load_data(self):
        """Последние загружаемые данные (каталог/датасет) [r]"""
        return self.settings.value('common/last_load_data', '')

    def write_last_load_data(self, data):
        """Последние загружаемые данные (каталог/датасет) [w]"""
        self.settings.setValue('common/last_load_data', data)

    def read_last_dir(self):  #
        """Последняя открытая директория [r]"""
        return self.settings.value('common/last_dir', '')

    def write_last_dir(self, path):
        """Последняя открытая директория [w]"""
        self.settings.setValue('common/last_dir', path)

    def read_load_sub_dir(self):
        """Загружать ли подкаталоги, когда загружаешь каталог [r]"""
        return self.settings.value('common/with_sub_dirs', False, type=bool)

    def write_load_sub_dir(self, flag):
        """Загружать ли подкаталоги, когда загружаешь каталог [w]"""
        self.settings.setValue('common/with_sub_dirs', flag)

    def read_default_output_dir(self):
        """Директория по умолчанию для выходных данных [r]"""
        return self.settings.value('common/output_dir', '')

    def write_default_output_dir(self, path):
        """Директория по умолчанию для выходных данных [w]"""
        self.settings.setValue('common/output_dir', path)

    def read_datasets_dir(self):
        """'Верхняя' директория для датасетов [r]"""
        return self.settings.value('common/datasets_dir', '')

    def write_datasets_dir(self, path):
        """'Верхняя' директория для датасетов [w]"""
        self.settings.setValue('common/datasets_dir', path)

    def read_dataset_mnist(self):
        """Датасет MNIST [r]"""
        return self.settings.value('datasets/mnist', '')

    def write_dataset_mnist(self, path):
        """Датасет MNIST [w]"""
        self.settings.setValue('datasets/mnist', path)

    def read_slicing_input(self):
        """Исходный файл проекта для автонарезки [r] """
        return self.settings.value('slicing/input_file', '')

    def write_slicing_input(self, path):
        """Исходный файл проекта для автонарезки [w] """
        self.settings.setValue('slicing/input_file', path)

    def read_default_slice_overlap_pols(self):
        """Значение перекрытия для полигонов по умолчанию [r]"""
        return self.settings.value('slicing/default_slice_overlap_pols', 5)

    def write_default_slice_overlap_pols(self, percent):
        """Значение перекрытия для полигонов по умолчанию [w]"""
        self.settings.setValue('slicing/default_slice_overlap_pols', percent)

    def read_slice_window_overlap(self):
        """Значение перекрытия для сканирующего окна [r]"""
        return self.settings.value('slicing/default_slice_window_overlap', 50)

    def write_slice_window_overlap(self, percent):
        """Значение перекрытия для сканирующего окна [w]"""
        self.settings.setValue('slicing/default_slice_window_overlap', percent)

    def read_slice_crop_size(self):
        """Размер сканирующего окна/окна кадрирования [r]"""
        return self.settings.value('slicing/slice_crop_size', 1280)

    def write_slice_crop_size(self, size):
        """Размер сканирующего окна/окна кадрирования [w]"""
        self.settings.setValue('slicing/slice_crop_size', size)

    def read_attributes_input(self):
        """Файл проекта для страницы атрибутов [r]"""
        return self.settings.value('attributes/input_file', '')

    def write_attributes_input(self, path):
        """Файл проекта для страницы атрибутов [w]"""
        self.settings.setValue('attributes/input_file', path)

    def read_sort_file_input(self):
        """Файл сортировки train-val-test для страницы атрибутов [r]"""
        return self.settings.value('attributes/sort_file', '')

    def write_sort_file_input(self, path):
        """Файл сортировки train-val-test для страницы атрибутов [w]"""
        self.settings.setValue('attributes/sort_file', path)

    def read_mnist_model_file(self):
        """Путь к обученной модели - MNIST [r]"""
        return self.settings.value('experiments/mnist_model_file', "")

    def write_mnist_model_file(self, path):
        """Путь к обученной модели - MNIST [w]"""
        self.settings.setValue('experiments/mnist_model_file', path)

    def read_mnist_epochs(self):
        """Количество эпох для вкладки Эксперименты - MNIST [r]"""
        return self.settings.value('experiments/mnist_epochs', '3')

    def write_mnist_epochs(self, epoch):
        """Количество эпох для вкладки Эксперименты - MNIST [w]"""
        self.settings.setValue('experiments/mnist_epochs', epoch)

    def read_mnist_learning_rate(self):
        """Скорость обучения для вкладки Эксперименты - MNIST [r]"""
        return self.settings.value('experiments/mnist_learning_rate', '0.01')

    def write_mnist_learning_rate(self, rate):
        """Скорость обучения для вкладки Эксперименты - MNIST [w]"""
        self.settings.setValue('experiments/mnist_learning_rate', rate)

    def read_mnist_dataset_using(self):
        """Объем используемого датасета в процентах вкладки Эксперименты - MNIST [r]"""
        return self.settings.value('experiments/mnist_dataset_using', '50')

    def write_mnist_dataset_using(self, percent):
        """Объем используемого датасета в процентах вкладки Эксперименты - MNIST [w]"""
        self.settings.setValue('experiments/mnist_dataset_using', percent)

    def read_mnist_shuffle_dataset(self):
        """Флаг перемешивание датасета для вкладки Эксперименты - MNIST [r]"""
        return self.settings.value('experiments/mnist_shuffle_dataset', False, type=bool)

    def write_mnist_shuffle_dataset(self, flag):
        """Флаг перемешивание датасета для вкладки Эксперименты - MNIST [w]"""
        self.settings.setValue('experiments/mnist_shuffle_dataset', flag)

    def read_mnist_activ_func(self):
        """Функция активации для вкладки Эксперименты - MNIST [r]"""
        return self.settings.value('experiments/mnist_activ_func', "ReLU")

    def write_mnist_activ_func(self, value):
        """Функция активации для вкладки Эксперименты - MNIST [w]"""
        self.settings.setValue('experiments/mnist_activ_func', value)

    def read_mnist_layers_number(self):
        """Количество слоёв во вкладке Эксперименты - MNIST [r]"""
        return self.settings.value('experiments/mnist_layers_num', "2")

    def write_mnist_layers_number(self, value):
        """Количество слоёв во вкладке Эксперименты - MNIST [w]"""
        self.settings.setValue('experiments/mnist_layers_num', value)
