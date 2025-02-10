import time

from PyQt6.QtGui import QPixmap, QGuiApplication, QPainter, QPainterPath, QColor, QPen
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QSizePolicy, QGridLayout, QVBoxLayout, QFrame, \
    QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt, QSize, QRectF, QTime, QTimer
import sys

from soupsieve import match
from numpy.ma.core import floor
from excel import ExcelManager
from get_pictures import GetPictures
import sys
from PyQt6.QtGui import QFont, QFontDatabase

MAE_RED = '#f23e2c'
CEE_GREEN = '#2da12f'
BENG_BLUE = '#296de3'
ECE_YELLOW = '#edb50e'
CMPE_ORAGNE = "#ed8218"
TITLE_TEAL = "#00706d"
BACK_BLUE = "#cce9e8"
BACK_GREY = "#efefef"
BORDER_GREY = "#d9d9d9"
MAE_RED_DARK = '#b02d20'
CEE_GREEN_DARK = '#185919'
BENG_BLUE_DARK = '#224a8f'
ECE_YELLOW_DARK = '#a67f0d'
CMPE_ORAGNE_DARK = "#b56312"

MAJOR_ABBREVIATIONS = {"MAE":"Mechanical Engineer", "ECE":"Electrical Engineer", "CMPE":"Computer Engineer", "BENG":"Biological Engineer", "CEE":"Civil Engineer"}

class MainWindow(QMainWindow):
    """
    The main window of the program

    Methods:
        __init__(self)
            formats the screen, parses the tutor_data.json file, and adds all the tutor widgets.

        keyPressEvent(self, event)
            is responsible for closing the program when the esc key is pressed
    """
    def __init__(self):
        """
        formats the screen, parses the tutor_data.json file, and adds all the tutor widgets
        """
        super().__init__()

        self.screen_size = QGuiApplication.primaryScreen().size()
        self.spacing = 20
        self.corner_radius = 30

        # Stack to manage two widgets
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Create two widgets for swapping
        self.active_widget = QWidget()
        self.hidden_widget = QWidget()

        # Add them to the stacked layout
        self.stacked_widget.addWidget(self.active_widget)
        self.stacked_widget.addWidget(self.hidden_widget)

        self.stacked_widget.setFixedSize(QSize(self.screen_size.width(), self.screen_size.height()))

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        #update the pictures
        gp = GetPictures()
        gp.get_pictures()

        #update the schedules
        self.em = ExcelManager()
        self.schedule = self.em.get_today_schedule()

        # put them in rainbow order
        self.schedule[1], self.schedule[2], self.schedule[3], self.schedule[4] = self.schedule[4], self.schedule[3], \
        self.schedule[1], self.schedule[2]

        self.timer = QTimer(self)  # Timer must be explicitly created for QMainWindow
        self.timer.timeout.connect(self.update_ui)

        #build the layout
        self.update_ui()

        #start the scheduled updates
        self.schedule_next_update()

        #show the screen
        self.showFullScreen()

    def update_ui(self):
        bold_font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSB.TTF")
        if bold_font_id < 0:
            print("Error loading font")

        bold_families = QFontDatabase.applicationFontFamilies(bold_font_id)

        font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSR.TTF")
        if font_id < 0:
            print("Error loading font")

        families = QFontDatabase.applicationFontFamilies(font_id)

        majors = ["MAE", "CMPE", "ECE", "CEE", "BENG"]

        # set up the main screen
        self.setWindowTitle("Tutor Center")
        self.setStyleSheet(f"background-color: {BACK_BLUE}")

        if self.hidden_widget.layout():
            old_layout = self.hidden_widget.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            old_layout.deleteLater()
            self.hidden_widget = QWidget()
            self.stacked_widget.addWidget(self.hidden_widget)

        # set up the top layout
        top_layout = QVBoxLayout(self.hidden_widget)
        top_layout.setSpacing(0)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # set up the title
        title = QLabel("Welcome to The Engineering Tutor Center")
        title.setFixedSize(QSize(self.screen_size.width(), int(self.screen_size.width() * 0.06)))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"background-color: {TITLE_TEAL}; font-weight: 700")
        title.setFont(QFont(bold_families[0], 60))
        top_layout.addWidget(title)

        # set up the base widget
        base_widget = QWidget()
        base_widget.setFixedSize(
            QSize(self.screen_size.width(), self.screen_size.height() - int(self.screen_size.width() * 0.06)))
        top_layout.addWidget(base_widget)

        base_layout = QHBoxLayout()
        base_widget.setLayout(base_layout)
        base_layout.setSpacing(self.spacing)
        base_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)

        tutor_list_widget = QWidget()
        tutor_list_widget.setFixedSize(
            QSize(int(self.screen_size.width() * 0.61), base_widget.size().height() - 2 * self.spacing))
        tutor_list_widget.setStyleSheet(f"background-color: white; border-radius: {self.corner_radius}")
        base_layout.addWidget(tutor_list_widget)

        right_section_widget = QWidget()
        base_layout.addWidget(right_section_widget)

        right_section_layout = QVBoxLayout()
        right_section_widget.setLayout(right_section_layout)
        right_section_layout.setSpacing(0)
        right_section_layout.setContentsMargins(0, 0, 0, 0)

        sign_in_widget = QLabel("Please Sign In!")
        sign_in_widget.setStyleSheet("color: black")
        sign_in_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sign_in_widget.setFont(QFont(families[0], 50))
        sign_in_widget.setFixedHeight(80)
        description_widget = QLabel("Tutors are wearing colored\nlanyards and name tags")
        description_widget.setStyleSheet("color: black")
        description_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_widget.setFont(QFont(families[0], 30))
        right_section_layout.addWidget(sign_in_widget)
        right_section_layout.addWidget(description_widget)

        schedule_title_widget = QLabel("Today's Schedule")
        schedule_title_widget.setFixedHeight(int(self.screen_size.width() * 0.039))
        schedule_title_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        schedule_title_widget.setStyleSheet(
            f"background-color: {TITLE_TEAL}; border-top-left-radius: {self.corner_radius}; border-top-right-radius: {self.corner_radius}; font-weight: 700")
        schedule_title_widget.setFont(QFont(families[0], 35))
        right_section_layout.addWidget(schedule_title_widget)

        schedule_widget = QWidget()
        schedule_widget.setFixedHeight(int(self.screen_size.width() * 0.321))
        schedule_widget.setStyleSheet(
            f"background-color: white; border-bottom-right-radius: {self.corner_radius}; border-bottom-left-radius: {self.corner_radius}")
        right_section_layout.addWidget(schedule_widget)

        schedule_layout = QGridLayout()
        schedule_widget.setLayout(schedule_layout)
        schedule_layout.setSpacing(0)
        schedule_layout.setContentsMargins(0, 0, 0, 0)

        now_index = self.em.get_now_index()

        for row in range(5):
            for col in range(16):
                schedule_layout.addWidget(ScheduleCell(self.schedule[row][col], row, col, col == now_index), row + 3,
                                          col + 3)

        cell_width = int((self.screen_size.width() - tutor_list_widget.width() - 3 * self.spacing) / 19)

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
            temp.setFont(QFont(families[0], 18))
            schedule_layout.addWidget(temp, i + 3, 1, 1, 2)

        for i in range(9):
            temp = QLabel(f"{(i + 8) % 12 + 1}:00")
            temp.setStyleSheet("color: black")
            temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp.setFixedHeight(30)
            temp.setFont(QFont(families[0], 15))
            schedule_layout.addWidget(temp, 2, i * 2 + 2, 1, 2)

        tutor_list_layout = QGridLayout()
        tutor_list_layout.setSpacing(self.spacing)
        tutor_list_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        tutor_list_widget.setLayout(tutor_list_layout)

        # for i, tutor in enumerate(em.get_on_shift()):
        #     tutor_list_layout.addWidget(TutorCard(tutor["name"], f"Images/{tutor["profile_image"]}", tutor["major"], tutor["progress"], f"Here until {tutor["here_until"]}"), math.floor(i/2)+1, i % 2 + 1)

        on_shift = self.em.get_on_shift()

        #print(on_shift)

        major_order = {"MAE": 0, "CMPE": 1, "ECE": 2, "CEE": 3, "BENG": 4}
        def parse_time(time_str):
            """Convert hh:mm string to a comparable 24-hour format"""
            hours, minutes = map(int, time_str.split(":"))
            if hours < 9:  # Assume PM if hour is less than 9
                hours += 12
            return hours * 60 + minutes  # Convert to total minutes for easy sorting

        def sort_key(entry):
            """Sorting key function that sorts by major and then by converted time"""
            major_rank = major_order.get(entry["major"], float("inf"))  # Default to last if unknown
            time_value = parse_time(entry["here_until"])
            return major_rank, time_value

        on_shift = sorted(on_shift, key=sort_key)

        majors_not_on_shift = ["MAE", "ECE", "CMPE", "CEE", "BENG"]

        for i in range(5):
            for j in range(2):
                display_order = 2 * i + j

                if display_order < len(on_shift):
                    tutor = on_shift[display_order]

                    tutor_list_layout.addWidget(
                        TutorCard(tutor["name"], f"Images/{tutor["profile_image"]}",
                                  MAJOR_ABBREVIATIONS[tutor["major"]], tutor["progress"],
                                  f"Here until {tutor["here_until"]}"), i, j)

                    if tutor["major"] in majors_not_on_shift:
                        majors_not_on_shift.remove(tutor["major"])
                else:
                    spots_left = 10 - (i * 2 + j)
                    if spots_left <= len(majors_not_on_shift):
                        current_major = MAJOR_ABBREVIATIONS[majors_not_on_shift[spots_left - 1]]
                        match current_major:
                            case "Biological Engineer":
                                major_schedule = self.schedule[4]
                            case "Civil Engineer":
                                major_schedule = self.schedule[3]
                            case "Electrical Engineer":
                                major_schedule = self.schedule[2]
                            case "Computer Engineer":
                                major_schedule = self.schedule[1]
                            case "Mechanical Engineer":
                                major_schedule = self.schedule[0]
                            case _:
                                major_schedule = []

                        next_in = ""

                        for block in range(now_index + 1, len(major_schedule)):
                            if major_schedule[block].lower() in {"ma", "ce", "b", "el", "cp"}:
                                end_schedule = block / 2 + 9
                                next_in = f"at {int(floor(end_schedule - 1) % 12 + 1)}:{int((end_schedule - floor(end_schedule)) * 60):02d}"
                                break
                        else:
                            next_in = "Tomorrow"

                        tutor_list_layout.addWidget(WillReturn(current_major, next_in))
                    else:
                        tutor_list_layout.addWidget(QWidget(), i, j)

        self.stacked_widget.setCurrentWidget(self.hidden_widget)

        self.active_widget, self.hidden_widget = self.hidden_widget, self.active_widget

    def schedule_next_update(self):
        """Calculates time until the next half-hour and sets the update timer."""
        now = QTime.currentTime()
        minutes_past_hour = now.minute()
        seconds_past_minute = now.second()

        # Find next update time (either :00 or :30)
        if minutes_past_hour < 30:
            minutes_until_next = 30 - minutes_past_hour
        else:
            minutes_until_next = 60 - minutes_past_hour

        seconds_until_next = (minutes_until_next * 60) - seconds_past_minute

        # Convert to minutes and seconds
        minutes_display = seconds_until_next // 60
        seconds_display = seconds_until_next % 60

        print(f"Next update in {minutes_display} minutes and {seconds_display} seconds")

        # Start a one-time timer to trigger the first update
        QTimer.singleShot(seconds_until_next * 1000, self.update_data)

    def update_data(self):
        """Updates the UI and switches to a 30-minute repeating update."""
        self.update_ui()
        self.schedule_next_update()


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
    def __init__(self, tutor_name, profile_image_path, major, progress, schedule, fake=False):
        """
        defines the layout of the tutor card based on the supplied arguments
        :param tutor_name: the name of the tutor
        :param profile_image_path: the path to the tutor
        :param major: the major of the tutor
        :param progress: the progress (senior, junior, etc.) of the tutor
        :param schedule: what hours the tutor is here for
        """
        super().__init__()

        if fake:
            return

        bold_font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSB.TTF")
        if bold_font_id < 0:
            print("Error loading font")

        bold_families = QFontDatabase.applicationFontFamilies(bold_font_id)

        font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSR.TTF")
        if font_id < 0:
            print("Error loading font")

        families = QFontDatabase.applicationFontFamilies(font_id)

        self.spacing = 10

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(self.spacing, self.spacing, 0, self.spacing)
        self.setLayout(main_layout)

        profile_pic = RoundedImageLabel(profile_image_path, BORDER_GREY,20)
        profile_pic.setStyleSheet(f"background-color: {BACK_GREY}")
        main_layout.addWidget(profile_pic)

        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_widget.setLayout(details_layout)
        details_widget.setStyleSheet("background-color: transparent")
        main_layout.addWidget(details_widget)

        #get the border color from the tutors major
        match major:
            case "Biological Engineer":
                color = BENG_BLUE
            case "Civil Engineer":
                color = CEE_GREEN
            case "Electrical Engineer":
                color = ECE_YELLOW
            case "Computer Engineer":
                color = CMPE_ORAGNE
            case "Mechanical Engineer":
                color = MAE_RED
            case _:
                color = 'black'

        name_widget = QLabel(tutor_name)
        name_widget.setStyleSheet("color: black")
        name_widget.setFont(QFont(families[0], 25))
        details_layout.addWidget(name_widget)

        line_widget = QWidget()
        line_widget.setFixedHeight(8)
        line_widget.setStyleSheet(f"border: 8px solid; border-color: transparent transparent {color} transparent; border-radius: 0")
        details_layout.addWidget(line_widget)

        title_widget = QLabel(f"{major} ({progress})")
        title_widget.setStyleSheet("color: black")
        title_widget.setFont(QFont(families[0], 15))
        details_layout.addWidget(title_widget)

        tutor_schedule_widget = QLabel(schedule)
        tutor_schedule_widget.setStyleSheet("color: black")
        tutor_schedule_widget.setFont(QFont(families[0], 15))
        details_layout.addWidget(tutor_schedule_widget)

        #format the overall card
        self.setStyleSheet(f"TutorCard {{background-color: {BACK_GREY}; border: 2px solid {BORDER_GREY}}}")

class RoundedImageLabel(QLabel):
    """
    taken from chat GPT+
    """
    def __init__(self, image_path, border_color, corner_radius=20):
        super().__init__()
        self.pixmap_original = QPixmap(image_path)  # Load the original image
        self.corner_radius = corner_radius
        self.border_color = border_color

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

        # Draw the image with rounded corners (using clipping path)
        path = QPainterPath()
        r = self.corner_radius  # The radius of the corners
        rect = QRectF(scaled_pixmap.rect())  # Convert QRect to QRectF
        path.addRoundedRect(rect, r, r)  # Add rounded rect path
        painter.setClipPath(path)  # Set clipping path to make the image fit inside

        # Draw the image
        painter.drawPixmap(0, 0, scaled_pixmap)

        # Now draw the border on top of the image
        border_thickness = 5  # Set the thickness of the border
        border_color = QColor(self.border_color)  # Set the border color (red as an example)

        # Create a QPen for the border with specified thickness and color
        pen = QPen(border_color)
        pen.setWidth(border_thickness)  # Set the width of the border
        painter.setPen(pen)  # Apply the pen to the painter
        painter.setBrush(Qt.GlobalColor.transparent)  # No fill for the border

        # Draw the rounded rectangle border (without clipping)
        painter.drawRoundedRect(rect, r, r)

        # End the painter to finalize drawing
        painter.end()

        # Set the pixmap with the final result (image + border)
        self.setPixmap(rounded_pixmap)

        super().resizeEvent(event)
        self.setFixedWidth(rounded_pixmap.width())


class WillReturn(QLabel):
    def __init__(self, major, return_time):
        super().__init__()

        bold_font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSB.TTF")
        if bold_font_id < 0:
            print("Error loading font")

        bold_families = QFontDatabase.applicationFontFamilies(bold_font_id)

        font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSR.TTF")
        if font_id < 0:
            print("Error loading font")

        families = QFontDatabase.applicationFontFamilies(font_id)

        self.spacing = 10
        offset = 30

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        spacer = QLabel()
        spacer.setStyleSheet("background: transparent")
        spacer.setFixedHeight(offset - 15)
        main_layout.addWidget(spacer)

        main_text = QLabel(f"{major}ing\nWill Return {return_time}")
        main_text.setStyleSheet("color: black; background-color: transparent")
        main_text.setFont(QFont(families[0], 25))
        main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(main_text)

        match major:
            case "Biological Engineer":
                bar_color = BENG_BLUE
            case "Civil Engineer":
                bar_color = CEE_GREEN
            case "Electrical Engineer":
                bar_color = ECE_YELLOW
            case "Computer Engineer":
                bar_color = CMPE_ORAGNE
            case "Mechanical Engineer":
                bar_color = MAE_RED
            case _:
                bar_color = 'black'

        spacer2 = QLabel()
        spacer2.setStyleSheet(f"border: 6px solid; border-color: {bar_color} transparent transparent transparent; background: transparent")
        spacer2.setFixedSize(QSize(int(self.width()*5/8), offset + 15))
        main_layout.addWidget(spacer2)

        self.setStyleSheet(f"WillReturn {{background-color: {BACK_GREY}; border: 2px solid {BORDER_GREY}}}")


class ScheduleCell(QLabel):
    def __init__(self, major, row, col, dark):
        super().__init__()

        border_color = 'black'
        
        if dark:
            match major:
                case "MA":
                    color = MAE_RED_DARK
                case "CE":
                    color = CEE_GREEN_DARK
                case "B":
                    color = BENG_BLUE_DARK
                case "EL":
                    color = ECE_YELLOW_DARK
                case "CP":
                    color = CMPE_ORAGNE_DARK
                case _:
                    color = '#9e9e9e'
        else:
            match major:
                case "MA":
                    color = MAE_RED
                case "CE":
                    color = CEE_GREEN
                case "B":
                    color = BENG_BLUE
                case "EL":
                    color = ECE_YELLOW
                case "CP":
                    color = CMPE_ORAGNE
                case _:
                    color = 'white'

        top_border = 'transparent'
        bottom_border = border_color
        left_border = 'transparent'
        right_border = '#2e2e2e'#757575'

        right_border_width = '2px'
        left_border_width = '2px'
        bottom_border_width = '3px'

        right_border_style = 'solid'

        if row == 0:
            top_border = border_color

        if row == 4:
            bottom_border = border_color
            bottom_border_width = '3px'

        if col % 2 == 0:
            right_border_width = '1px'
            right_border_style = 'dashed'

        if col == 0:
            left_border = border_color
            left_border_width = '3px'

        if col == 15:
            right_border = border_color
            right_border_width = '3px'

        self.setStyleSheet(f"background-color: {color}; border-width: 4px {right_border_width} {bottom_border_width} {left_border_width}; border-style: solid {right_border_style} solid solid; border-color: {top_border} {right_border} {bottom_border} {left_border}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

#run the program
if __name__ == "__main__":
        app = QApplication([])
        window = MainWindow()
        sys.exit(app.exec())