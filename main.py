import math
import json
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSizePolicy, QGridLayout, QVBoxLayout, QFrame, \
    QHBoxLayout
from PyQt6.QtCore import Qt, QSize
import sys

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

        #parse the json file
        with open('data.json', 'r') as file:
            #load the file
            tutor_data_array = json.load(file)

            tutor_data_array = tutor_data_array[:-8]

        self.screen_size = QGuiApplication.primaryScreen().size()
        self.spacing = 20
        self.corner_radius = 40

        #set up the main screen
        self.setWindowTitle("Tutor Center")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #cce9e8")

        #set up the central widget
        central_widget = QWidget()
        central_widget.setFixedSize(QSize(self.screen_size.width(), self.screen_size.height()))
        self.setCentralWidget(central_widget)

        #set up the top layout
        top_layout = QVBoxLayout()
        top_layout.setSpacing(0)
        top_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(top_layout)

        #set up the title
        title = QLabel("Welcome to The Engineering Tutor Center")
        title.setFixedSize(QSize(self.screen_size.width(), int(self.screen_size.width()*0.06)))
        title.setStyleSheet("background-color: #00706d")
        top_layout.addWidget(title)

        #set up the base widget
        base_widget = QWidget()
        base_widget.setFixedSize(QSize(self.screen_size.width(), self.screen_size.height()-int(self.screen_size.width()*0.06)))
        top_layout.addWidget(base_widget)

        base_layout = QHBoxLayout()
        base_widget.setLayout(base_layout)
        base_layout.setSpacing(self.spacing)
        base_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)

        tutor_list_widget = QWidget()
        tutor_list_widget.setFixedSize(QSize(int(self.screen_size.width()*0.61),base_widget.size().height()-2*self.spacing))
        tutor_list_widget.setStyleSheet(f"background-color: #ffffff; border-radius: {self.corner_radius}")
        base_layout.addWidget(tutor_list_widget)

        right_section_widget = QWidget()
        base_layout.addWidget(right_section_widget)

        right_section_layout = QVBoxLayout()
        right_section_widget.setLayout(right_section_layout)
        right_section_layout.setSpacing(0)
        right_section_layout.setContentsMargins(0, 0, 0, 0)

        sign_in_widget = QLabel("Please Sign In!")
        description_widget = QLabel("Tutors are wearing colored lanyards and name tags")
        right_section_layout.addWidget(sign_in_widget)
        right_section_layout.addWidget(description_widget)

        schedule_title_widget = QLabel("Today's Schedule")
        schedule_title_widget.setFixedHeight(int(self.screen_size.width() * 0.039))
        schedule_title_widget.setStyleSheet(f"background-color: #00706d; border-top-left-radius: {self.corner_radius}; border-top-right-radius: {self.corner_radius}")
        right_section_layout.addWidget(schedule_title_widget)

        schedule_widget = QWidget()
        schedule_widget.setFixedHeight(int(self.screen_size.width()*0.321))
        schedule_widget.setStyleSheet(f"background-color: white; border-bottom-right-radius: {self.corner_radius}; border-bottom-left-radius: {self.corner_radius}")
        right_section_layout.addWidget(schedule_widget)

        schedule_layout = QGridLayout()
        schedule_widget.setLayout(schedule_layout)

        #add each tutor to the grid layout
        # for i, tutor_data in enumerate(tutor_data_array):
        #     #set up the widget
        #     widget = TutorCard(
        #         tutor_data['tutorName'],
        #         tutor_data['profilePath'],
        #         tutor_data['major'],
        #         tutor_data['class'],
        #         tutor_data['schedule']
        #     )

            #add the widget to the correct spot
        #     layout.addWidget(widget, math.floor(i/cols) + 1, (i % cols) + 1)
        #
        # #format the grid layout
        # layout.setContentsMargins(10, 10, 10, 10)
        # layout.setSpacing(10)

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
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.setStyleSheet(f"TutorCard {{background-color: white; border: 5px solid {color}}}")

    def sizeHint(self):
        return QSize(640, 480)

#run the program
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()

    sys.exit(app.exec())