from PyQt5 import QtWidgets, QtGui, QtCore


class AzCalcStdMean(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculate mean and Std for channels of dataset images")
        self.setGeometry(300, 300, 300, 200)

        layout = QtWidgets.QVBoxLayout(self)

        # Создаем метку для отображения выбранного переключателя
        self.label = QtWidgets.QLabel("Выберите опцию:")
        layout.addWidget(self.label)

        # Создаем первый переключатель
        self.rb_images_prj_only = QtWidgets.QRadioButton("Опция 1")
        self.rb_images_from_dir = QtWidgets.QRadioButton("Опция 2")


        # Создаем кнопку для подтверждения выбора
        self.pb_calc = QtWidgets.QPushButton("Calculate")
        self.pb_save = QtWidgets.QPushButton("Write results to project")
        self.pb_calc.clicked.connect(self.on_button_clicked)

        widgets = [self.rb_images_prj_only, self.rb_images_from_dir]
        for widget in widgets:
            layout.addWidget(widget)

        # layout.addWidget(self.button)

        # self.setLayout(layout)

    def on_button_clicked(self):
        if self.radio1.isChecked():
            self.label.setText("Вы выбрали Опцию 1")
        elif self.radio2.isChecked():
            self.label.setText("Вы выбрали Опцию 2")
        else:
            self.label.setText("Выберите опцию")

    def translate_ui(self):
        self.translate_ui()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = AzCalcStdMean()
    window.show()
    sys.exit(app.exec_())
