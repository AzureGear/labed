from qdarktheme.qtpy.QtCore import Qt
from qdarktheme.qtpy.QtWidgets import QDockWidget, QTabWidget, QMainWindow, QTextEdit, QGroupBox, QVBoxLayout, QLabel,\
    QWidget, QSlider, QFormLayout, QComboBox, QScrollArea, QPushButton, QGridLayout


class SettingsUI:
    """
    Класс настройки
    """

    def setup_ui(self, win: QWidget):
        widget_container = QWidget()

        g_layout = QGridLayout(widget_container)
        g_layout.addWidget(QPushButton("Push button 1"), 0, 0)
        g_layout.addWidget(QPushButton("Push button 2"), 0, 1)
        g_layout.addWidget(QPushButton("Push button 3"), 1, 0)
        g_layout.addWidget(QPushButton("Push button 4"), 1, 1)

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget_container)

        v_main_layout = QVBoxLayout(win)
        v_main_layout.addWidget(scroll_area)


        # left_dock = QDockWidget("Left dock")
        # right_dock = QDockWidget("Right dock")
        # top_dock = QDockWidget("Top dock")
        # bottom_dock = QDockWidget("Bottom dock")
        #
        # # Setup widgets
        # left_dock.setWidget(QTextEdit("This is the left widget."))
        # right_dock.setWidget(QTextEdit("This is the right widget."))
        # top_dock.setWidget(QTextEdit("This is the top widget."))
        # bottom_dock.setWidget(QTextEdit("This is the bottom widget."))
        # for dock in (left_dock, right_dock, top_dock, bottom_dock):
        #     dock.setAllowedAreas(
        #         Qt.DockWidgetArea.LeftDockWidgetArea
        #         | Qt.DockWidgetArea.RightDockWidgetArea
        #         | Qt.DockWidgetArea.BottomDockWidgetArea
        #         | Qt.DockWidgetArea.TopDockWidgetArea
        #     )
        #
        # # Layout
        # main_win = QMainWindow()
        # main_win.setCentralWidget(QTextEdit("This is the central widget."))
        # main_win.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)
        # main_win.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
        # main_win.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, top_dock)
        # main_win.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)
        #
        # layout = QVBoxLayout(win)
        # layout.addWidget(main_win)
        # layout.setContentsMargins(0, 0, 0, 0)
