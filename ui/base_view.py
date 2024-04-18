from qdarktheme.qtpy.QtCore import Qt, QSize, pyqtSignal
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel, \
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout, QTabBar, QLineEdit, QHBoxLayout, \
    QToolButton, QApplication, QMessageBox, QToolBar
from qdarktheme.qtpy.QtGui import QPixmap
from utils import AppSettings, UI_COLORS
from ui import AzButtonLineEdit, AzImageViewer, AzAction, coloring_icon
import os

the_colors = UI_COLORS.get("datasets_color")
the_colors2 = UI_COLORS.get("datasets_change_color")
current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class ViewDatasetUI(QWidget):
    """
    Класс виджета просмотра датасетов
    """
    mySignal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        self.actions_tool_bar = (
            AzAction("Load image", "glyph_pickaxe", the_colors2, the_colors),
            AzAction("Load dir", "glyph_flask", the_colors2, the_colors),
            AzAction("Load preset dataset", "glyph_eye", the_colors2, the_colors),
            AzAction("Automation", "glyph_highlight", the_colors2, the_colors),
            AzAction("Settings", "glyph_gear", the_colors2, the_colors)
        )

        layout = QVBoxLayout(self)
        # layout.setContentsMargins(5, 5, 5, 5)  # уменьшаем границу
        self.toolbar = QToolBar("Dataset viewer instruments")  # панель инструментов для просмотра датасетов
        self.toolbar.setFloatable(False)
        self.toolbar.toggleViewAction().setVisible(False)  # чтобы панель случайно не отключали
        self.toolbar.addWidget(QLabel("Current dataset"))
        self.toolbar.addSeparator()

        self.toolbtn = QToolButton()
        self.image_viewer = AzImageViewer()
        self.toolbar.addActions(self.actions_tool_bar)
        main_win = QMainWindow()
        button = QPushButton("Не надо")
        main_win.setCentralWidget(self.image_viewer)
        main_win.addToolBar(self.toolbar)
        layout.addWidget(main_win)
        layout.addWidget(button)
        # open_image(self"F:/data_prj/labed/labed/test.jpg"
        button.clicked.connect(self.hello)
        self.mySignal.connect(self.printrr)
        test_img = "F:/data_prj/labed/labed/test.jpg"



        self.image_viewer.setPixmap(QPixmap(test_img))



    def hello(self):
        self.mySignal.emit("Exercises from w3resource!")

    def printrr(self, str):
        print(str)

    def open_image(self, image_name):
        self.image_viewer.setPixmap(QPixmap(image_name))
        self.image_viewer.fitInView(self.image_viewer.pixmap_item, Qt.KeepAspectRatio)

#######################################################################

"""Module setting up ui of mdi window."""
# from qdarktheme.qtpy.QtWidgets import (
#     QHBoxLayout,
#     QLabel,
#     QMdiArea,
#     QMdiSubWindow,
#     QPushButton,
#     QSplitter,
#     QTextEdit,
#     QVBoxLayout,
#     QWidget,
# )

#
# class MdiUI:
#     """The ui class of mdi window."""

# def _make_mdi_area_test_widget(self, enable_tab_mode=False):
#     # Widgets
#     container = QWidget()
#     mdi_area = QMdiArea()
#     label_test_name = QLabel()
#     cascade_button = QPushButton("Cascade")
#     new_button = QPushButton("Add new")
#     tiled_button = QPushButton("Tiled")
#
#     # Setup widgets
#     if enable_tab_mode:
#         mdi_area.setViewMode(QMdiArea.ViewMode.TabbedView)
#         label_test_name.setText("QMdiArea(QMdiArea.viewMode = TabbedView)")
#     else:
#         label_test_name.setText("QMdiArea(QMdiArea.viewMode = SubWindowView)")
#
#     def add_new_sub_window():
#         sub_win = QMdiSubWindow(container)
#         sub_win_main_widget = QWidget(sub_win)
#         v_layout = QVBoxLayout(sub_win_main_widget)
#         v_layout.addWidget(QTextEdit("Sub window"))
#
#         sub_win.setWidget(sub_win_main_widget)
#         mdi_area.addSubWindow(sub_win)
#         sub_win.show()
#
#     add_new_sub_window()
#     new_button.pressed.connect(add_new_sub_window)
#     cascade_button.pressed.connect(mdi_area.cascadeSubWindows)
#     tiled_button.pressed.connect(mdi_area.tileSubWindows)
#     new_button.setDefault(True)
#
#     # Layout
#     h_layout = QHBoxLayout()
#     h_layout.addWidget(new_button)
#     h_layout.addWidget(cascade_button)
#     h_layout.addWidget(tiled_button)
#
#     v_main_layout = QVBoxLayout(container)
#     v_main_layout.addWidget(label_test_name)
#     v_main_layout.addLayout(h_layout)
#     v_main_layout.addWidget(mdi_area)
#     return container
#
# def setup_ui(self, win: QWidget) -> None:
#     """Set up ui."""
#     # Widgets
#     splitter = QSplitter()
#
#     # Setup widgets
#     mdi_area = self._make_mdi_area_test_widget()
#     mdi_area_with_tab = self._make_mdi_area_test_widget(enable_tab_mode=True)
#
#     # Layout
#     splitter.addWidget(mdi_area)
#     splitter.addWidget(mdi_area_with_tab)
#
#     main_layout = QVBoxLayout(win)
#     main_layout.addWidget(splitter)
