# Хранение безопасных настроек

# QSettings
ORGANIZATION = 'azura'
APPLICATION = 'lab_ed'

# каталог для переводов по умолчанию
LOCALIZATION_FOLDER = 'l10n'

# размеры окна (высота в процентах от ширины)
APP_MIN_SIZE = {"WIDTH": 720,
                "HEIGHT": 0.628}

# цвета интерфейса
UI_COLORS = {
    "sidepanel_color": "dodgerblue",
    "processing_color": "deeppink",
    "experiments_color": "forestgreen",
    "datasets_color": "mediumorchid",
    "datasets_change_color": "goldenrod",
    "automation_color": "darkorange",
    "settings_color": "deepskyblue",
}

# настройки Интерфейса
# base_view
# dock_widget : { "widget_name":
# 0 - show, 1 - closable, 2 - movable, 3 - floatable, 4 - no_caption, 5 - no_actions }
UI_BASE_VIEW = {
    "top_dock": [False, False, False, False, True, True],
    "files_dock": [True, True, True, False, False, False]
}

UI_OUTPUT_TYPES = ["SAMA.json"]
UI_READ_LINES = 35

# (dark) c:\venvs\lab-ed\Lib\site-packages>python -m qdarktheme.widget_gallery
