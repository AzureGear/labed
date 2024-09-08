import sys
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore


class NumpyTableWidget(QtWidgets.QWidget):
    def __init__(self, array=None):
        super().__init__()

        self.array = array
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Numpy Table Widget')
        self.setGeometry(100, 100, 600, 400)

        self.tableWidget = QtWidgets.QTableWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        if self.array is not None:
            self.updateTable(self.array)

    def updateTable(self, array):
        self.array = array
        self.tableWidget.setRowCount(self.array.shape[0])
        self.tableWidget.setColumnCount(self.array.shape[1])

        min_val = np.min(self.array)
        max_val = np.max(self.array)

        for i in range(self.array.shape[0]):
            for j in range(self.array.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(self.array[i, j]))
                self.tableWidget.setItem(i, j, item)

                # Линейная интерполяция цвета
                value = self.array[i, j]
                if max_val != min_val:
                    normalized_value = (value - min_val) / (max_val - min_val)
                    print (normalized_value)
                else:
                    normalized_value = 0.5  # Если все значения одинаковы, используем средний цвет

                if value < 0:
                    # Интерполяция от синего к белому
                    blue = int(255 * (1 - normalized_value))
                    red = int(255 * normalized_value)
                    green = int(255 * normalized_value)
                elif value > 0:
                    # Интерполяция от белого к красному # Больше нормализованное значение - синий и красный -> 0
                    # red = int(255 * normalized_value)
                    # blue = int(255 * (normalized_value))
                    # green = int(255 * (normalized_value))
                    red = int(255 * normalized_value)
                    blue = int(255 * (1-normalized_value))
                    green = int(255 * (1-normalized_value))
                    print(f"red {red}; blue {blue}; green {green}")
                else:
                    # Белый цвет для значений, равных нулю
                    red = 255
                    blue = 255
                    green = 255

                color = QtGui.QColor(red, green, blue, 127)
                item.setBackground(color)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Пример массива numpy
    array = np.array([[1, -2, 3], [4, -5, 6], [-7, 8, -9]])

    ex = NumpyTableWidget(array)
    ex.show()

    # # Пример обновления массива
    # new_array = np.array([[10, -20, 30], [40, -50, 60], [-70, 80, -90]])
    # ex.updateTable(new_array)

    sys.exit(app.exec_())
