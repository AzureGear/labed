
# ----------------------------------------------------------------------------------------------------------------------
# def junk():
#     # For future test of sorting
#     start_time = time.time()
# 
#     # file = "c:/Users/user/Dropbox/sort_info.json"
#     # big_real_data = helper.load(file)

#     cur_ratio = 0.8
#     # result = optimum_by_greed_with_group(big_real_data, cur_ratio)
#     result = optimum_by_greed_with_group(test_real_uranium, cur_ratio,
#                                          group_pattern=helper.PATTERNS.get("double_underscore"))
#     train = result["train"].values()
#     val = result["val"].values()
#     # print(big_real_data)
#     # train, val, count = optimum_split_for_data(unsort, 0.8, 6.5)
#     end_time = time.time()
#     sec = (end_time - start_time)  # / 3600
#     train_per, val_per = calc_ratio(result['ratio'][0], result['ratio'][1])
#     print(f"Обработано строк: {len(test_real_uranium.keys())}; занятое время: {format_time(sec, 'ru')},"
#           f"error: {result['error']:.1f};\n%t:",
#           [f"{p:.0f}" for p in train_per], ";\n%v:",
#           [f"{p:.0f}" for p in val_per])
    
# ----------------------------------------------------------------------------------------------------------------------    



# import sys
# import itertools
# import numpy as np

# mns = np.arange(0.0, 0.8, 0.1).tolist()
# conf = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# for conf_value, mns_value in itertools.product(conf, mns):
#     print(conf_value, mns_value)

#
# def check_palindrome(text: str):
#     zip_text = text.replace(" ", "")
#     if len(zip_text) < 2:
#         print("Введенный текст по умолчанию является палиндромом, поскольку имеет менее 2 символов.")
#         return True
#     for i in range(0, int(len(zip_text)/2)):
#         print(f"{zip_text[i].lower()} compare to {zip_text[-i-1].lower()}")
#         if zip_text[i].lower() != zip_text[-i-1].lower():
#             return False
#     return True
#
# def fibbonachi(limit):
#     num1 = 0
#     num2 = 1
#     next_number = num2
#     while next_number <= limit:
#         print(next_number, end=" ")
#         num1, num2 = num2, next_number
#         next_number = num1 + num2
#
# if __name__ == '__main__':
#     palin_true = "А роза упала на лапу Азора"
#     text = "А роза свалилась на лапу Азора"
#
#     print(f"Этот текст '{palin_true}' является палиндромом: {check_palindrome(palin_true)}")
#     print(f"А этот текст '{text}' является палиндромом: {check_palindrome(text)}")

# import sys
# import numpy as np
# from PyQt5 import QtWidgets, QtGui, QtCore
#
#
# class NumpyTableWidget(QtWidgets.QWidget):
#     def __init__(self, array=None):
#         super().__init__()
#
#         self.array = array
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('Numpy Table Widget')
#         self.setGeometry(100, 100, 600, 400)
#
#         self.tableWidget = QtWidgets.QTableWidget()
#
#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(self.tableWidget)
#         self.setLayout(layout)
#
#         if self.array is not None:
#             self.updateTable(self.array)
#
#     def updateTable(self, array):
#         self.array = array
#         self.tableWidget.setRowCount(self.array.shape[0])
#         self.tableWidget.setColumnCount(self.array.shape[1])
#
#         min_val = np.min(self.array)
#         max_val = np.max(self.array)
#
#         for i in range(self.array.shape[0]):
#             for j in range(self.array.shape[1]):
#                 item = QtWidgets.QTableWidgetItem(str(self.array[i, j]))
#                 self.tableWidget.setItem(i, j, item)
#
#                 # Линейная интерполяция цвета
#                 value = self.array[i, j]
#                 if max_val != min_val:
#                     normalized_value = (value - min_val) / (max_val - min_val)
#                     print (normalized_value)
#                 else:
#                     normalized_value = 0.5  # Если все значения одинаковы, используем средний цвет
#
#                 if value < 0:
#                     # Интерполяция от синего к белому
#                     blue = int(255 * (1 - normalized_value))
#                     red = int(255 * normalized_value)
#                     green = int(255 * normalized_value)
#                 elif value > 0:
#                     # Интерполяция от белого к красному # Больше нормализованное значение - синий и красный -> 0
#                     # red = int(255 * normalized_value)
#                     # blue = int(255 * (normalized_value))
#                     # green = int(255 * (normalized_value))
#                     red = int(255 * normalized_value)
#                     blue = int(255 * (1-normalized_value))
#                     green = int(255 * (1-normalized_value))
#                     print(f"red {red}; blue {blue}; green {green}")
#                 else:
#                     # Белый цвет для значений, равных нулю
#                     red = 255
#                     blue = 255
#                     green = 255
#
#                 color = QtGui.QColor(red, green, blue, 127)
#                 item.setBackground(color)
#
#         self.tableWidget.resizeColumnsToContents()
#         self.tableWidget.resizeRowsToContents()
#
#
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#
#     # Пример массива numpy
#     array = np.array([[1, -2, 3], [4, -5, 6], [-7, 8, -9]])
#
#     ex = NumpyTableWidget(array)
#     ex.show()
#
#     # # Пример обновления массива
#     # new_array = np.array([[10, -20, 30], [40, -50, 60], [-70, 80, -90]])
#     # ex.updateTable(new_array)
#
#     sys.exit(app.exec_())
