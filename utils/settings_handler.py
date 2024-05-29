from qdarktheme.qtpy import QtCore
from utils import config


class AppSettings:
    """
    Взаимодействие с хранением, записью и сбросом настроек в реестре
    """

    def __init__(self):
        self.settings = QtCore.QSettings(config.ORGANIZATION, config.APPLICATION)

    def read_ui_stack_widget_cur_tab(self):  # активный виджет для боковой панели [r]
        return self.settings.value('ui/ui_stack_widget_current_tab', 0)

    def write_ui_stack_widget_cur_tab(self, ui_tab):  # активный виджет для боковой панели [w]
        self.settings.setValue('ui/ui_stack_widget_current_tab', ui_tab)

    def read_ui_proc_page(self):  # активная страница для 1 виджета, если он выбран [r]
        return self.settings.value('ui/ui_proc_page', 3)

    def write_ui_proc_page(self, proc_page):  # активная страница для 1 виджета, если он выбран [w]
        self.settings.setValue('ui/ui_proc_page', proc_page)

    def read_lang(self):  # язык [r]
        return self.settings.value('ui/language', 'English')

    def write_lang(self, lang):  # язык [w]
        self.settings.setValue('ui/language', lang)

    def read_ui_theme(self):  # тема интерфейса [r]
        return self.settings.value('ui/theme', 'light')

    def write_ui_theme(self, theme):  # тема интерфейса [w]
        self.settings.setValue('ui/theme', theme)

    def read_ui_position(self):  # позиция, размер и состояние окна приложения [r]
        # if len(screeninfo.get_monitors()) == 1: # TODO: что если отключили монитор?
        position = self.settings.value('ui/base_gui_position', QtCore.QPoint(250, 250))
        size = self.settings.value('ui/base_gui_size', QtCore.QSize(900, 565))
        state = self.settings.value('ui/base_gui_state', QtCore.Qt.WindowNoState)  # QWindow
        return position, size, state

    def write_ui_position(self, position, size, state):  # позиция, размер и состояние окна приложения [w]
        self.settings.setValue('ui/base_gui_position', position)
        self.settings.setValue('ui/base_gui_size', size)
        self.settings.setValue('ui/base_gui_state', state)

    def read_last_load_data(self):  # последние загружаемые данные (каталог/датасет) [r]
        return self.settings.value('common/last_load_data', '')

    def write_last_load_data(self, data):  # последние загружаемые данные (каталог/датасет) [w]
        self.settings.setValue('common/last_load_data', data)

    def read_last_dir(self):  # последняя открытая директория [r]
        return self.settings.value('common/last_dir', '')

    def write_last_dir(self, path):  # последняя открытая директория [w]
        self.settings.setValue('common/last_dir', path)

    def read_datasets_dir(self):  # "верхняя" директория для датасетов [r]
        return self.settings.value('common/datasets_dir', '')

    def write_datasets_dir(self, path):  # "верхняя" директория для датасетов [w]
        self.settings.setValue('common/datasets_dir', path)

    def read_default_output_dir(self):  # директория по умолчанию для выходных данных [r]
        return self.settings.value('common/output_dir', '')

    def write_default_output_dir(self, path):  # директория по умолчанию для выходных данных [w]
        self.settings.setValue('common/output_dir', path)

    def read_load_sub_dir(self):  # загружать ли подкаталоги, когда загружаешь каталог [r]
        return self.settings.value('common/with_sub_dirs', False)

    def write_load_sub_dir(self, b):  # загружать ли подкаталоги, когда загружаешь каталог [w]
        self.settings.setValue('common/with_sub_dirs', b)

    def read_slicing_input(self):  # исходный файл проекта для автонарезки [r]
        return self.settings.value('slicing/input_file', '')

    def write_slicing_input(self, path):  # исходный файл проекта для автонарезки [w]
        self.settings.setValue('slicing/input_file', path)

    def read_default_slice_overlap_pols(self):  # значение перекрытия для полигонов по умолчанию [r]
        return self.settings.value('slicing/default_slice_overlap_pols', 5)

    def write_default_slice_overlap_pols(self, percent):  # значение перекрытия для полигонов по умолчанию [w]
        self.settings.setValue('slicing/default_slice_overlap_pols', percent)

    def read_slice_window_overlap(self):  # значение перекрытия для сканирующего окна [r]
        return self.settings.value('slicing/default_slice_window_overlap', 50)

    def write_slice_window_overlap(self, percent):  # значение перекрытия для сканирующего окна [w]
        self.settings.setValue('slicing/default_slice_window_overlap', percent)
