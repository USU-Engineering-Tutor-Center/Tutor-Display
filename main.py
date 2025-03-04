# import modules
from PyQt6.QtGui import QGuiApplication, QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QStackedWidget, QWidget, QVBoxLayout, QLabel, \
    QHBoxLayout
from PyQt6.QtCore import QTime, QTimer, QSize, Qt
from numpy.ma.core import floor
import sys

# import custom modules
from excel import ExcelManager
import get_pictures
import custom_widgets
from constants import *
git commit -m "I refactored all the constants into their own file for better edit ability."
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
        sets up the main screen
        """
        super().__init__()

        # define constants
        self.screen_size = QGuiApplication.primaryScreen().size()
        self.spacing = 20
        self.corner_radius = 30

        # make the main layout a stack so that we can swap between updates
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setFixedSize(QSize(self.screen_size.width(), self.screen_size.height()))

        # create two widgets for swapping and add them to the stack layout
        self.active_widget = QWidget()
        self.hidden_widget = QWidget()
        self.stacked_widget.addWidget(self.active_widget)
        self.stacked_widget.addWidget(self.hidden_widget)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # update the pictures
        get_pictures.get_pictures()

        # update the schedules
        self.em = ExcelManager()
        self.schedule = self.em.get_today_schedule()

        # manually put them in rainbow order
        self.schedule[1], self.schedule[2], self.schedule[3], self.schedule[4] = self.schedule[4], self.schedule[3], self.schedule[1], self.schedule[2]

        # define the timer for auto updating
        self.timer = QTimer(self)
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.update_ui)

        # define the bold font
        bold_font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSB.TTF")
        if bold_font_id < 0:
            print("Error loading font")
        self.bold_families = QFontDatabase.applicationFontFamilies(bold_font_id)

        # define the normal font
        font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSR.TTF")
        if font_id < 0:
            print("Error loading font")
        self.families = QFontDatabase.applicationFontFamilies(font_id)

        # build the layout
        self.update_ui()

        # start the scheduled updates
        self.schedule_next_update()

        # show the screen
        self.showFullScreen()

    def update_ui(self):
        """
        defines the layout of the display and fills it in with the data fetched from the spreadsheet
        :return:
        """

        # set up the main screen
        self.setWindowTitle("Tutor Center")
        self.setStyleSheet(f"background-color: {BACK_BLUE}")

        # clear out the old main widget so that we can rebuild it
        if self.hidden_widget.layout():
            old_layout = self.hidden_widget.layout()

            # iterate through all children and mark them for deletion
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # mark the layout for deletion
            old_layout.deleteLater()

            # add a fresh widget
            self.hidden_widget = QWidget()
            self.stacked_widget.addWidget(self.hidden_widget)

        # set up the top layout and add it to the back widget
        top_layout = QVBoxLayout(self.hidden_widget)
        top_layout.setSpacing(0)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # create the title
        title = QLabel("Welcome to The Engineering Tutor Center")
        title.setFixedSize(QSize(self.screen_size.width(), int(self.screen_size.width() * 0.06)))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"background-color: {TITLE_TEAL}; font-weight: 700")
        title.setFont(QFont(self.bold_families[0], 60))
        top_layout.addWidget(title)

        # set up the base widget
        base_widget = QWidget()
        base_widget.setFixedSize(QSize(self.screen_size.width(), self.screen_size.height() - int(self.screen_size.width() * 0.06)))
        top_layout.addWidget(base_widget)

        # define the base layout
        base_layout = QHBoxLayout()
        base_widget.setLayout(base_layout)
        base_layout.setSpacing(self.spacing)
        base_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)

        # define the widget for the list of all the tutors
        tutor_list_widget = QWidget()
        tutor_list_widget.setFixedSize(QSize(int(self.screen_size.width() * 0.61), base_widget.size().height() - 2 * self.spacing))
        tutor_list_widget.setStyleSheet(f"background-color: white; border-radius: {self.corner_radius}")
        base_layout.addWidget(tutor_list_widget)

        # define the widget for the right side
        right_section_widget = QWidget()
        base_layout.addWidget(right_section_widget)

        # define the layout for the right side
        right_section_layout = QVBoxLayout()
        right_section_widget.setLayout(right_section_layout)
        right_section_layout.setSpacing(0)
        right_section_layout.setContentsMargins(0, 0, 0, 0)

        # add the call to sign in and the description
        sign_in_widget = QLabel("Please Sign In!")
        sign_in_widget.setStyleSheet("color: black")
        sign_in_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sign_in_widget.setFont(QFont(self.families[0], 50))
        sign_in_widget.setFixedHeight(80)
        description_widget = QLabel("Tutors are wearing colored\nlanyards according to the colors\nin the schedule below")
        description_widget.setStyleSheet("color: black")
        description_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_widget.setFont(QFont(self.families[0], 30))
        right_section_layout.addWidget(sign_in_widget)
        right_section_layout.addWidget(description_widget)

        # define the widget for the schedule title
        schedule_title_widget = QLabel("Today's Schedule")
        schedule_title_widget.setFixedHeight(int(self.screen_size.width() * 0.039))
        schedule_title_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        schedule_title_widget.setStyleSheet(
            f"background-color: {TITLE_TEAL}; "
            f"border-top-left-radius: {self.corner_radius}; "
            f"border-top-right-radius: {self.corner_radius}; "
            f"font-weight: 700"
        )
        schedule_title_widget.setFont(QFont(self.families[0], 35))
        right_section_layout.addWidget(schedule_title_widget)

        # define the schedule widget
        schedule_widget = QWidget()
        schedule_widget.setFixedHeight(int(self.screen_size.width() * 0.321))
        schedule_widget.setStyleSheet(
            f"background-color: white; "
            f"border-bottom-right-radius: {self.corner_radius}; "
            f"border-bottom-left-radius: {self.corner_radius}"
        )
        right_section_layout.addWidget(schedule_widget)

        # define the layout for the schedule itself
        schedule_layout = QGridLayout()
        schedule_widget.setLayout(schedule_layout)
        schedule_layout.setSpacing(0)
        schedule_layout.setContentsMargins(0, 0, 0, 0)

        # get the index of the current time so that it can be darkened
        now_index = self.em.get_now_index()

        while schedule_layout.count():
            item = schedule_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        start_index = 28
        end_index = 0

        for i, value in enumerate(self.schedule[0]):
            if value.lower() != "c" and i < start_index:
                start_index = i
            elif value.lower() != "c" and i > end_index:
                end_index = i

        # loop through all the cells and add them
        for row in range(5):
            for col in range(len(self.schedule[0])):
                if col < start_index or col > end_index:
                    continue

                schedule_layout.addWidget(
                    custom_widgets.ScheduleCell(
                        self.schedule[row][col], # the letter at the cell in the spreadsheet
                        row, # the current row for formatting
                        col, # the current col for formatting
                        col == now_index, # if this cell is for the current time slot and therefore needs to be dark
                        start_index,
                        end_index
                    ),
                    row + 3, # offset the position to account for labels and spacing
                    col + 3 # offset the position to account for labels and spacing
                )

        cell_width = int(schedule_widget.width() / (end_index - start_index - 1))

        # define spacers to make the layout look good and add them
        spacer = QLabel()
        spacer.setFixedSize(QSize(cell_width, self.spacing))
        spacer.setStyleSheet("background-color: transparent")
        spacer2 = QLabel()
        spacer2.setFixedSize(QSize(cell_width, self.spacing))
        spacer2.setStyleSheet("background-color: transparent")
        spacer3 = QLabel()
        spacer3.setFixedSize(QSize(cell_width, self.spacing))
        spacer3.setStyleSheet("background-color: transparent")

        schedule_layout.addWidget(spacer, 8, len(self.schedule[0]) + 3)
        schedule_layout.addWidget(spacer2, 1, 1)
        schedule_layout.addWidget(spacer3, 1, 2)

        # add the labels for the majors
        for i, major in enumerate(MAJORS):
            temp = QLabel(major)
            temp.setStyleSheet("color: black")
            temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp.setFont(QFont(self.families[0], 18))
            schedule_layout.addWidget(temp, i + 3, 1, 1, 2) # offset and spans multiple cols to make it look good

        # add the hour labels
        for i in range(15):
            label_text = f"{(i + 6) % 12 + 1}:00"
            if i * 2 < start_index or i * 2 > end_index + 1:
                continue

            temp = QLabel(label_text)
            temp.setStyleSheet("color: black")
            temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp.setFixedHeight(30)
            temp.setFont(QFont(self.families[0], 15))

            #the first and last label are a little different so take care of them
            if i * 2 == start_index:
                schedule_layout.addWidget(temp, 2, 2, 1, start_index+2) # FIXME I have been having problems with this line. If the time changes you should check this out
            elif i * 2 == end_index + 1:
                schedule_layout.addWidget(temp, 2, i * 2 + 2, 1, 40)  # spanning 40 columns seems like a good way to make sure it spans to the end
            else:
                schedule_layout.addWidget(temp, 2, i * 2 + 2, 1, 2) # offset and spans multiple cols to make it look good

        # define the layout of the tutor list
        tutor_list_layout = QGridLayout()
        tutor_list_layout.setSpacing(self.spacing)
        tutor_list_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, self.spacing)
        tutor_list_widget.setLayout(tutor_list_layout)

        def parse_time(time_str):
            """Convert hh:mm string to a comparable 24-hour format"""
            hours, minutes = map(int, time_str.split(":"))
            if hours < 9:  # Assume PM if hour is less than 9
                hours += 12
            return hours * 60 + minutes  # Convert to total minutes for easy sorting

        def sort_key(entry):
            """Sorting key function that sorts by major and then by converted time"""
            major_rank = MAJOR_ORDER.get(entry["major"], float("inf"))  # Default to last if unknown
            time_value = parse_time(entry["here_until"])
            return major_rank, time_value

        # get the tutors on shift and sort them by major then by time that they are leaving
        on_shift = sorted(self.em.get_on_shift(), key=sort_key)

        # keep track of what majors have a tutor on shift
        majors_not_on_shift = ["MAE", "ECE", "CMPE", "CEE", "BENG"]

        # loop through every slot in the tutor list
        for i in range(TUTOR_LIST_HEIGHT//2):
            for j in range(2):
                # convert the row and col to a single index
                display_order = 2 * i + j

                # if we have not already added every tutor
                if display_order < len(on_shift):
                    tutor = on_shift[display_order]

                    # add a tutor card to the layout
                    tutor_list_layout.addWidget(
                        custom_widgets.TutorCard(
                            tutor["name"], #the name of the tutor
                            f"Images/{tutor["profile_image"]}", # the path to the image
                            MAJOR_ABBREVIATIONS[tutor["major"]], # the name of the major
                            tutor["academic_class"], #softmore, junior, etc
                            f"Here until {tutor["here_until"]}" # when the tutor is leaving
                        ),
                        i,
                        j
                    )

                    # remove the major for the list of majors not on shift
                    if tutor["major"] in majors_not_on_shift:
                        majors_not_on_shift.remove(tutor["major"])
                # if we have added every tutor
                else:
                    # calculate how many spots wee need to fill
                    spots_left = TUTOR_LIST_HEIGHT - (i * 2 + j)

                    # add the "major will be back" cards to the very end
                    if spots_left <= len(majors_not_on_shift):
                        # get the major to add
                        current_major = MAJOR_ABBREVIATIONS[majors_not_on_shift[spots_left - 1]]

                        # get the schedule for the specific major
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

                        # find when the major will be back next
                        for block in range(now_index + 1, len(major_schedule)):
                            # if the current cell indicates that a tutor is in
                            if major_schedule[block].lower() in {"ma", "ce", "b", "el", "cp"}:
                                #calculate when the major will be in next and then break the loop
                                end_schedule = block / 2 + 9
                                next_in = f"at {int(floor(end_schedule - 1) % 12 + 1)}:{int((end_schedule - floor(end_schedule)) * 60):02d}"
                                break
                        # if it did not find a time when a tutor will be in then they must be coming in tomorrow
                        else:
                            next_in = "Tomorrow"

                        # add the widget
                        tutor_list_layout.addWidget(custom_widgets.WillReturn(current_major, next_in))
                    else:
                        # add a fake widget
                        tutor_list_layout.addWidget(QWidget(), i, j)

        # swap the active and the hidden widget now that the hidden widget has been created
        self.stacked_widget.setCurrentWidget(self.hidden_widget)
        self.active_widget, self.hidden_widget = self.hidden_widget, self.active_widget

    def schedule_next_update(self):
        """Calculates time until the next half-hour and sets the update timer."""

        #parse the current time
        now = QTime.currentTime()
        minutes_past_hour = now.minute()
        seconds_past_minute = now.second()

        # find next update time (either :00 or :30)
        if minutes_past_hour < 30:
            minutes_until_next = 30 - minutes_past_hour
        else:
            minutes_until_next = 60 - minutes_past_hour

        seconds_until_next = (minutes_until_next * 60) - seconds_past_minute

        # schedule the update
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

        # if the key is esc then close the program
        if event.key() == Qt.Key.Key_Escape:
            self.close()

# run the program
if __name__ == "__main__":
        app = QApplication([])
        window = MainWindow()
        sys.exit(app.exec())