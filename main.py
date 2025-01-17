import math
import json
from PyQt6.QtGui import QPixmap, QGuiApplication, QImage, QPainter, QPainterPath, QRegion
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSizePolicy, QGridLayout, QVBoxLayout, QFrame, \
    QHBoxLayout
from PyQt6.QtCore import Qt, QSize, QRect
import sys

from excel import ExcelManager

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

        em = ExcelManager()
        schedule = em.get_today_schedule()

        majors = ["MAE", "CEE", "BENG", "ECE", "CMPE"]

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
        schedule_layout.setSpacing(0)
        schedule_layout.setContentsMargins(0, 0, 0, 0)

        for row in range(5):
            for col in range(16):
                schedule_layout.addWidget(ScheduleCell(schedule[row][col], row, col), row + 3, col + 3)

        cell_width = int((self.screen_size.width() - tutor_list_widget.width() - 3 * self.spacing)/19)
        print(cell_width)

        spacer = QLabel()
        spacer.setFixedSize(QSize(cell_width, self.spacing))
        spacer.setStyleSheet("background-color: transparent")

        spacer2 = QLabel()
        spacer2.setFixedSize(QSize(cell_width, self.spacing))
        spacer2.setStyleSheet("background-color: transparent")

        spacer3 = QLabel()
        spacer3.setFixedSize(QSize(cell_width, self.spacing))
        spacer3.setStyleSheet("background-color: transparent")

        schedule_layout.addWidget(spacer, 8, 19)
        schedule_layout.addWidget(spacer2, 1, 1)
        schedule_layout.addWidget(spacer3, 1, 2)

        for i, major in enumerate(majors):
            temp = QLabel(major)
            temp.setStyleSheet("color: black")
            temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            schedule_layout.addWidget(temp, i + 3, 1, 1, 2)

        for i in range(9):
            temp = QLabel(f"{(i+8)%12 + 1}:00")
            temp.setStyleSheet("color: black")
            temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp.setFixedHeight(30)
            schedule_layout.addWidget(temp, 2, i*2 + 2, 1, 2)

        tutor_list_layout = QGridLayout()
        tutor_list_layout.setSpacing(self.spacing)
        tutor_list_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        tutor_list_widget.setLayout(tutor_list_layout)

        for i in range(5):
            for j in range(2):
                tutor_list_layout.addWidget(TutorCard("Kyler", "Images/fredericks-kyler-400x600.jpg", "Computer Engineer", "Senior", "Here until 7:00"), i + 1, j + 1)

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

        self.spacing = 20

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        self.setLayout(main_layout)

        # profile_pic = QLabel()
        # profile_pixmap = QPixmap(profile_image_path)
        # profile_pixmap_scaled = profile_pixmap.scaled(profile_pic.size(), Qt.AspectRatioMode.KeepAspectRatio)
        # profile_pic.setPixmap(profile_pixmap)
        # profile_pic.setScaledContents(True)
        # profile_pic.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        # profile_pic.setStyleSheet(f"border-radius: {40}")

        profile_pic = RoundedImageLabel(profile_image_path, 20)
        main_layout.addWidget(profile_pic)

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
        self.setStyleSheet(f"TutorCard {{background-color: #efefef; border: 2px solid #d9d9d9}}")

class RoundedImageLabel(QLabel):
    """
    taken from chat GPT+
    """
    def __init__(self, image_path, corner_radius=20):
        super().__init__()
        self.pixmap_original = QPixmap(image_path)  # Load the original image
        self.corner_radius = corner_radius

    def resizeEvent(self, event):
        if self.pixmap_original.isNull():
            return

        # Scale the pixmap to fit the label, maintaining aspect ratio
        scaled_pixmap = self.pixmap_original.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Create a new QPixmap for the result
        rounded_pixmap = QPixmap(scaled_pixmap.size())
        rounded_pixmap.fill(Qt.GlobalColor.transparent)

        # Create the painter for drawing
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create a QRegion for the full image
        rect = scaled_pixmap.rect()
        r = self.corner_radius

        # Create region for the full rectangle (without rounded corners)
        region = QRegion(rect)

        # Increase the size of the square cutouts to remove the bottom gap
        square_size = r + 1  # Slightly larger square size to ensure no gaps

        # Create larger square cutouts for the left corners
        square_top_left = QRegion(QRect(rect.left(), rect.top(), square_size, square_size))
        square_bottom_left = QRegion(QRect(rect.left(), rect.bottom() - square_size + 1, square_size, square_size))

        # Subtract the larger squares from the region
        region -= square_top_left
        region -= square_bottom_left

        # Add the circular arcs back to the left corners (quarter circles)
        arc_top_left = QRegion(QRect(rect.left(), rect.top(), r * 2, r * 2), QRegion.RegionType.Ellipse)
        arc_bottom_left = QRegion(QRect(rect.left(), rect.bottom() - r * 2 + 1, r * 2, r * 2), QRegion.RegionType.Ellipse)

        # Add the circular arcs back to the region
        region += arc_top_left
        region += arc_bottom_left

        # Set the region as the clip region for the painter
        painter.setClipRegion(region)

        # Draw the image with the new region (rounded left corners)
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()

        # Set the pixmap with the final result
        self.setPixmap(rounded_pixmap)

        super().resizeEvent(event)


class ScheduleCell(QLabel):
    def __init__(self, major, row, col):
        super().__init__()

        match major:
            case "MA":
                color = 'red'
            case "CE":
                color = 'green'
            case "B":
                color = 'blue'
            case "EL":
                color = 'yellow'
            case "CP":
                color = 'orange'
            case _:
                color = 'white'

        top_border = 'transparent'
        bottom_border = 'black'
        left_border = 'transparent'
        right_border = '#757575'

        right_border_width = '2px'
        left_border_width = '2px'
        bottom_border_width = '3px'

        right_border_style = 'solid'

        if row == 0:
            top_border = 'black'

        if row == 4:
            bottom_border = 'black'
            bottom_border_width = '3px'

        if col % 2 == 0:
            right_border_width = '1px'
            right_border_style = 'dashed'

        if col == 0:
            left_border = 'black'
            left_border_width = '3px'

        if col == 15:
            right_border = "black"
            right_border_width = '3px'

        self.setStyleSheet(f"background-color: {color}; border-width: 4px {right_border_width} {bottom_border_width} {left_border_width}; border-style: solid {right_border_style} solid solid; border-color: {top_border} {right_border} {bottom_border} {left_border}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

#run the program
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()

    sys.exit(app.exec())