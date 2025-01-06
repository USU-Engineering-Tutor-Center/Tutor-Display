import math
import json
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSizePolicy, QGridLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt
import sys


def calculate_grid(desired_squares, height, width):
    """
    calculates the largest tillable square that will fit in the given rectangle
    :param desired_squares: the number of square that you want to fit
    :param height: the height of the rectangle
    :param width: the width of the rectangle
    :return: a tuple with the size of the largest tillable square, the number of columns and the number of rows
    """

    horizontal_num = 1
    vertical_num = 1
    square_size = min(width, height)

    #add in the squares 1 by 1
    for square_count in range(1, desired_squares + 1):
        #recalculate grid if there are no free spots available
        if vertical_num * horizontal_num < square_count:
            horizontal_dif = width - (horizontal_num * square_size)
            vertical_dif = height - (vertical_num * square_size)

            #find the biggest gap and squeeze in a new square
            if horizontal_dif > vertical_dif:
                horizontal_num += 1
                square_size = math.floor(width / horizontal_num)
            else:
                vertical_num += 1
                square_size = math.floor(height / vertical_num)

    return vertical_num, horizontal_num

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutor Center")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout()
        central_widget.setLayout(layout)

        with open('data.json', 'r') as file:
            tutor_data_array = json.load(file)

            rows, cols = calculate_grid(len(tutor_data_array),
                                        QGuiApplication.primaryScreen().size().height(),
                                        QGuiApplication.primaryScreen().size().width())

            for i, tutor_data in enumerate(tutor_data_array):
                widget = TutorCard(
                    tutor_data['tutorName'],
                    tutor_data['profilePath'],
                    tutor_data['major'],
                    tutor_data['class'],
                    tutor_data['schedule']
                )
                layout.addWidget(widget, math.floor(i/(rows + 1)) + 1, (i % cols) + 1)
                print(math.floor(i/rows), (i % cols))

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

class TutorCard(QFrame):
    def __init__(self, tutor_name, profile_image_path, major, progress, schedule):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

        tutor_name_label = QLabel(tutor_name)
        tutor_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tutor_name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: black")

        profile_image_label = QLabel()
        pixmap = QPixmap(profile_image_path)
        profile_image_label.setPixmap(pixmap)
        profile_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # profile_image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

        major_label = QLabel(f"Major: {major} ({progress})")
        major_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        major_label.setStyleSheet("font-size: 12px; color: black")

        schedule_label= QLabel(f"Here from {schedule}")
        schedule_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        schedule_label.setStyleSheet("font-size: 12px; color: black")

        layout.addWidget(tutor_name_label)
        layout.addWidget(profile_image_label)
        layout.addWidget(major_label)
        layout.addWidget(schedule_label)

        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setStyleSheet("TutorCard {background-color: lightblue; border: 5px solid orange}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()

    sys.exit(app.exec())