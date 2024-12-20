# Хранение безопасных настроек

# QSettings
ORGANIZATION = 'azura'
APPLICATION = 'lab_ed'

# каталог для переводов по умолчанию
LOCALIZATION_FOLDER = 'l10n'

# размеры окна (высота в процентах от ширины)
APP_MIN_SIZE = {"WIDTH": 720,
                "HEIGHT": 0.95}

# проверка доступности датасетов и их расположений
DEFAULT_DATASET_USAGE = {"MNIST": {"check": True, "path": "MNIST/mnist.npz"}}

# высота кнопки в некоторых классах, для избежания срезания текста в ней при наследовании
BUTTON_H = 22

# цвета интерфейса
UI_COLORS = {
    "sidepanel_color": "dodgerblue",
    "processing_color": "deeppink",
    "experiments_color": "limegreen",
    "datasets_color": "mediumorchid",
    "datasets_change_color": "goldenrod",
    "automation_color": "darkorange",
    "settings_color": "deepskyblue",
    "default_color": "grey",
    "line_color": "deepskyblue",  # цвет отображения границ меток по умолчанию - голубой"
    "crop_color": "yellow",  # цвет центральной точки и границ для ручного кадрирования
    "train_color": "darkorange",  # цвет таблицы Train - оранжевый
    "val_color": "deepskyblue",  # цвет таблицы Val - голубой
    "test_color": "red"  # цвет таблицы Test - красный
}

# настройка Интерфейса доступных модулей:
UI_ENABLE = {
    "process": {"merge": True, "slice": True, "attributes": True, "sort": True, "geometry": True},
    "automation": True,
    "experiment": {"mnist": True, "nor": True},
}

# настройки интерфейса Widget'ов с поддержкой DockWidgets со структурой:
# dock_widget : { "widget_name":
# 0 - show, 1 - closable, 2 - movable, 3 - floatable, 4 - no_caption, 5 - no_actions }
#
# base_view.py
UI_BASE_VIEW = {
    "top_dock": [False, False, False, False, True, True],
    "files_dock": [True, True, True, False, False, False]
}
# bace_proc_attrs.py
UI_BASE_ATTRS = {
    "bottom_dock": [False, False, True, False, False, True]
}

# az_slice_manual_crop.py
UI_AZ_SLICE_MANUAL = {
    "top_dock": [True, False, False, False, True, True],
    "files_dock": [True, False, True, False, False, False]
}

# az_exp_mnist.py
UI_AZ_MNIST_ICON_PANEL = 24  # размер иконок для панели инструментов
UI_AZ_MNIST_DIGITS_SIZE = 24  # размер цифр для вкладки MNIST

# base_proc_merge.py
UI_AZ_PROC_MERGE_ICON_PANEL = 30  # размер иконок панели инструментов вкладки Merge

# base_proc_attrs.py
UI_AZ_PROC_ATTR_ICON_SIZE = 24  # размер иконок вкладки Обработка-Атрибуты на главной таблице
UI_AZ_PROC_ATTR_IM_ICON_SIZE = 22  # размер иконок виджета таблицы фильтрата

# настройка приближения/отдаления для отображения изображений
MINIMUM_ZOOM = -2
MAXIMUM_ZOOM = 50

# минимальное и максимальное значения кадрирования
MAX_CROP_SIZE = 8000
MIN_CROP_SIZE = 16

ALPHA = 230  # степень прозрачности заливки у меток по умолчанию (0 ... 255)

UI_OUTPUT_TYPES = ["SAMA.json"]  # типы выходных данных
UI_INPUT_TYPES = ["LabelMe.json", "SAMA.json"]  # типы входных данных
UI_AZ_EXPORT_TYPES = ["SAMA (split and copy according to selected tran/test/val)", "YOLO Seg", "YOLO Box", "MMSegmentation"]

UI_READ_LINES = 3  # количество загружаемых строк в проектах *.json для предпросмотра
