from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from utils import AppSettings
from utils import UI_COLORS
import numpy as np
import os

current_folder = os.path.dirname(os.path.abspath(__file__))  # каталога проекта + /ui/


class AutomationUI(QtWidgets.QWidget):
    """
    Класс виджета автоматизации
    """

    def __init__(self, parent):
        super().__init__()
        self.settings = AppSettings()  # настройки программы
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # уменьшаем границу
        main_win = QtWidgets.QMainWindow()
        txt = """           A = np.stack([x, np.ones_like(x)]).T \n
            print(np.linalg.solve(np.dot(A.T, A), np.dot(A.T, y))) \n
            It does linear regression of data by finding normal solution to the usually overdetermined linear system.
            """
        text = QtWidgets.QTextEdit()
        text.setText(txt)
        button = QtWidgets.QPushButton("Не надо")
        main_win.setCentralWidget(text)
        layout.addWidget(main_win)
        layout.addWidget(button)
        button.clicked.connect(self.turtle)

    def turtle(self):
        import turtle as t
        from random import random as r
        t.mode("logo"), t.bgcolor(0, 0, 0)
        t.hideturtle()
        step, angle = 6, 30
        t.tracer(2, 500)

        def f(t, l):
            if l >= step:
                t.color(r(), r(), r())
                t.forward(l)

                lt = t.clone()
                lt.left(angle)
                f(lt, l - step)

                rt = t.clone()
                rt.right(angle)
                f(rt, l - step)

        f(t, 60)
        t.exitonclick()

    def rapple(self):
        x = np.linspace(0, 4, 100)
        y = 2.3 * x + 1.3 + np.random.randn(100) * 0.5
        A = np.stack([x, np.ones_like(x)]).T
        print(np.linalg.solve(np.dot(A.T, A), np.dot(A.T, y)))
