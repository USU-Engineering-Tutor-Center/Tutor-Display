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
    """
    The main window of the program

    Methods:
        __init__(self)
            formats the screen, parses the data.json file, and adds all the tutor widgets.

        keyPressEvent(self, event)
            is responsible for closing the program when the esc key is pressed
    """
    def __init__(self):
        """
        formats the screen, parses the data.json file, and adds all the tutor widgets
        """

        super().__init__()

        #set up the main screen
        self.setWindowTitle("Tutor Center")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout()
        central_widget.setLayout(layout)
        self.setStyleSheet("background-color: #ede1be")

        #parse the json file
        with open('data.json', 'r') as file:
            #load the file
            tutor_data_array = json.load(file)

            #calculate the optimal grid layout
            rows, cols = calculate_grid(len(tutor_data_array),
                                        QGuiApplication.primaryScreen().size().height(),
                                        QGuiApplication.primaryScreen().size().width())

            #add each tutor to the grid layout
            for i, tutor_data in enumerate(tutor_data_array):
                #set up the widget
                widget = TutorCard(
                    tutor_data['tutorName'],
                    tutor_data['profilePath'],
                    tutor_data['major'],
                    tutor_data['class'],
                    tutor_data['schedule']
                )

                #add the widget to the correct spot
                layout.addWidget(widget, math.floor(i/(rows + 1)) + 1, (i % cols) + 1)

        #format the grid layout
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        #show the screen
        self.showFullScreen()

    def keyPressEvent(self, event):
        """
        is responsible for closing the program when the esc key is pressed
        :param event: the event to react to
        """

        #if the key is esc then close the program
        if event.key() == Qt.Key.Key_Escape:
            self.close()

class TutorCard(QFrame):
    """
    defines the layout of a tutor card so that it can easily be copied

    Methods:
        __init__(self, tutor_name, profile_image_path, major, progress, schedule)
            defines the layout of the tutor card based on the supplied arguments
    """
    def __init__(self, tutor_name, profile_image_path, major, progress, schedule):
        """
        defines the layout of the tutor card based on the supplied arguments
        :param tutor_name: the name of the tutor
        :param profile_image_path: the path to the tutor
        :param major: the major of the tutor
        :param progress: the progress (senior, junior, etc.) of the tutor
        :param schedule: what hours the tutor is here for
        """
        super().__init__()

        #set up the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

        #add the name label
        tutor_name_label = QLabel(tutor_name)
        tutor_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tutor_name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: black; background-color: transparent")
        layout.addWidget(tutor_name_label)

        #add the image label
        profile_image_label = QLabel()
        pixmap = QPixmap(profile_image_path)
        profile_image_label.setPixmap(pixmap)
        profile_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_image_label.setStyleSheet("background-color: transparent")
        layout.addWidget(profile_image_label)

        #add the major label
        major_label = QLabel(f"Major: {major} ({progress})")
        major_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        major_label.setStyleSheet("font-size: 12px; color: black; background-color: transparent")
        layout.addWidget(major_label)

        #add the schedule label
        schedule_label= QLabel(f"Here from {schedule}")
        schedule_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        schedule_label.setStyleSheet("font-size: 12px; color: black; background-color: transparent")
        layout.addWidget(schedule_label)

        #get the border color from the tutors major
        match major:
            case "Biological Engineering":
                color = 'blue'
            case "Civil Engineering":
                color = 'green'
            case "Electrical Engineering":
                color = 'yellow'
            case "Computer Engineering":
                color = 'orange'
            case "Mechanical Engineering":
                color = 'red'
            case _:
                color = 'black'

        #format the overall card
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setStyleSheet(f"TutorCard {{background-color: white; border: 5px solid {color}}}")

#run the program
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()

    sys.exit(app.exec())