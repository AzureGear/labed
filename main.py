import os
import sys
from datetime import datetime
import traceback

from PyQt5 import QtWidgets
from ui.base_gui import BaseGUI


def _qt_wayland_to_xcb_for_nix() -> None:
    """Для Wayland PyQt5 не является стабильной библиотекой, следует использовать XWayland (xcb).
    Данный метод используется в shell.nix, когда direnv/nix-shell активен.
    shell.nix делает то же самое, когда direnv/nix-shell активен — debugpy/IDE часто не наследует этот хук.
    """
    plat = (os.environ.get("QT_QPA_PLATFORM") or "").lower()
    if plat in ("wayland", "wayland-egl"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"  # устанавливаем XWayland
        
# TODO: сделать загрузку предустановленных датасетов self.tb_load_preset.addActions
# TODO: сделать загрузку данных SAMA, label_me, YOLO, MMSeg
# TODO: сделать сброс всех настроек по нажатию изменению настроек в файле settings.ini Reset = True
# TODO: сделать прогресс бар типа паровозика с вагончиками, со всплывающими фактами, типа "Факт №291: У акул зубы
#  обновляются всю жизнь. И поезда разные выезжают.
# TODO: инструмент для просмотра результатов работы сети (две картинки рядом)


class MyWindow(BaseGUI):  # класс интерфейса
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Label Dataset Editor")


# Стандартная инициализация
if __name__ == '__main__':
    _qt_wayland_to_xcb_for_nix()
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
