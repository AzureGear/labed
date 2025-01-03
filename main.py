from ui.base_gui import BaseGUI
from PyQt5 import QtWidgets
from datetime import datetime
import sys
import traceback

TESTING_MODE = True  # на этапе отладки желательно держать включённым
log_file_name = 'labed.log'  # имя файла ведения лога при ошибках


# TODO: сделать загрузку предустановленных датасетов self.tb_load_preset.addActions
# TODO: сделать сброс всех настроек по нажатию изменению настроек в файле settings.ini Reset = True
# TODO: сделать прогресс бар типа паровозика с вагончиками, со всплывающими фактами, типа "Факт №291: У акул зубы
#  обновляются всю жизнь. И поезда разные выезжают.
# TODO: Сделать тесты для объединения, разрезания
# TODO: инструмент для просмотра результатов работы сети (две картинки рядом)
# TODO: ошибки "libpng warning: iCCP: known incorrect sRGB profile" и "QLayout: Attempting to add QLayout "" to TabAttributesUI "", which already has a layout"


# Ловчий ошибок
def excepthook_catcher(t, v, tb):
    with open(log_file_name, 'w') as file:
        file.write("\n-------------- Errors log --------------\n")
        file.write("Timecode: %s\n" % datetime.now().strftime("%Y.%m.%d  %H:%M:%S"))
        traceback.print_exception(t, v, tb, file=file)


class MyWindow(BaseGUI):  # класс интерфейса
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Label Dataset Editor")


# Стандартная инициализация
if __name__ == '__main__':
    try:  # открываем, если имеется, в противном случае создаем новый файл
        file = open(log_file_name, 'a+')
    except IOError:
        file = open(log_file_name, 'w+')
    if TESTING_MODE:
        sys.excepthook = excepthook_catcher  # включение логирования
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
