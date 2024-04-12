from PyQt5.QtCore import Qt, QSettings, QPoint, QSize
from PyQt5.QtGui import QFont
import screeninfo
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

    def read_ui_position(self):
        # if len(screeninfo.get_monitors()) == 1: # TODO: что если отключили монитор?
        position = self.settings.value('ui/base_gui_position', QPoint(250, 250))
        size = self.settings.value('ui/base_gui_size', QSize(900, 565))
        state = self.settings.value('ui/base_gui_state', Qt.WindowNoState)  # QWindow
        return position, size, state

    def write_ui_position(self, position, size, state):
        self.settings.setValue('ui/base_gui_position', position)
        self.settings.setValue('ui/base_gui_size', size)
        self.settings.setValue('ui/base_gui_state', state)
