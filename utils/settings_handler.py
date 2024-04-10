from PyQt5.QtCore import QSettings
from utils import config


class AppSettings:
    """
    Взаимодействие с хранением, записью и сбросом настроек в реестре
    """
    def __init__(self):
        self.settings = QSettings(config.ORGANIZATION, config.APPLICATION)

    def write_ui_stack_widget_cur_tab(self, ui_tab):
        self.settings.setValue('ui/ui_stack_widget_current_tab', ui_tab)

    def read_ui_stack_widget_cur_tab(self):
        return self.settings.value('ui/ui_stack_widget_current_tab', 0)

    def read_lang(self):
        return self.settings.value('ui/language', 'English')

    def write_lang(self, lang):
        self.settings.setValue('ui/language', lang)

    def read_ui_theme(self):
        return self.settings.value('ui/theme', 'light')

    def write_ui_theme(self, theme):
        self.settings.setValue('ui/theme', theme)
