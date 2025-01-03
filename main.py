import math

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSizePolicy, QGridLayout, QVBoxLayout
from PyQt6.QtCore import Qt
import sys


def calculate_grid(desired_squares, height, width):
    """
    calculates the largest tillable square that will fit in the given rectangle
    :param desired_squares: the number of square that you want to fit
    :param height: the height of the rectangle
    :param width: the width of the rectangle
    :return: the size of the largest tillable square
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

    return square_size

def print_grid(square_size, height, width):
    """
    prints a grid based on the given parameters
    :param square_size: the size of the square to be printed
    :param height: the height of the rectangle that the squares will be in
    :param width: the width of the rectangle that the squares will be in
    """
    print_buf = ""
    vertical_num = math.floor(height / square_size)
    horizontal_num = math.floor(width / square_size)

    #loop through all rows
    for y in range(vertical_num):
        #start with a different color each time
        print_x = y % 2 == 0

        #loop through all the columns
        for x in range(horizontal_num):
            #print the color
            if print_x:
                print_buf += ("\033[31m @ \033[0m" * square_size)
            else:
                print_buf += ("\033[34m @ \033[0m" * square_size)

            #alternate color
            print_x = not print_x

        #pad the end with @ so fit to the width
        print_buf += (" @ " * (width - (square_size * horizontal_num)))
        print_buf += "\n"

        #print and then reset the print buffer
        print(print_buf * square_size, end="")
        print_buf = ""

    #print extra lines wit fit the height
    print(((" @ " * width) + "\n") * (height - (square_size * vertical_num)))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutor Center")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout()
        central_widget.setLayout(layout)

        for row in range(4):
            for col in range(3):
                widget = TutorCard("Frodo", "Images/Frodo.png", "Bioengineering", "Senior", "9:00 - 5:00")
                layout.addWidget(widget, row, col)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

class TutorCard(QWidget):
    def __init__(self, tutor_name, profile_image_path, major, progress, schedule):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

        tutor_name_label = QLabel(tutor_name)
        tutor_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tutor_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        profile_image_label = QLabel()
        pixmap = QPixmap(profile_image_path)
        profile_image_label.setPixmap(pixmap)
        profile_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        major_label = QLabel(f"Major: {major} ({progress})")
        major_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        major_label.setStyleSheet("font-size: 12px; color:gray")

        schedule_label= QLabel(f"Here from {schedule}")
        schedule_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        schedule_label.setStyleSheet("font-size: 12px; color:gray")

        layout.addWidget(tutor_name_label)
        layout.addWidget(profile_image_label)
        layout.addWidget(major_label)
        layout.addWidget(schedule_label)


        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: lightblue; border: 5px solid orange")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()

    sys.exit(app.exec())