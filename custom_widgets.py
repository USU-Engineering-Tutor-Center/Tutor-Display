#import modules
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QPen, QFont, QFontDatabase
from PyQt6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QSize, QRectF

#define constants
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

class TutorCard(QFrame):
    """
    defines the layout of a tutor card so that it can easily be copied

    Methods:
        __init__(self, tutor_name, profile_image_path, major, progress, schedule)
            defines the layout of the tutor card based on the supplied arguments
    """

    def __init__(self, tutor_name, profile_image_path, major, progress, leaving_at):
        """
        defines the layout of the tutor card based on the supplied arguments
        :param tutor_name: the name of the tutor
        :param profile_image_path: the path to the tutor
        :param major: the major of the tutor
        :param progress: the progress (senior, junior, etc.) of the tutor
        :param leaving_at: what hours the tutor is here for
        """
        super().__init__()

        # define the font
        font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSR.TTF")
        if font_id < 0:
            print("Error loading font")
        families = QFontDatabase.applicationFontFamilies(font_id)

        # define constants
        self.spacing = 10

        # define the main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(self.spacing, self.spacing, 0, self.spacing)
        self.setLayout(main_layout)

        # define the profile picture
        profile_pic = RoundedImageLabel(profile_image_path, BORDER_GREY, 20)
        profile_pic.setStyleSheet(f"background-color: {BACK_GREY}")
        main_layout.addWidget(profile_pic)

        # define the widget to hold the details
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_widget.setLayout(details_layout)
        details_widget.setStyleSheet("background-color: transparent")
        main_layout.addWidget(details_widget)

        # define the widget for the name
        name_widget = QLabel(tutor_name)
        name_widget.setStyleSheet("color: black")
        name_widget.setFont(QFont(families[0], 25))
        details_layout.addWidget(name_widget)

        # get the border color from the tutors major
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

        # add a line under the name with their color
        line_widget = QWidget()
        line_widget.setFixedHeight(8)
        line_widget.setStyleSheet(
            f"border: 8px solid; "
            f"border-color: transparent transparent {color} transparent; "
            f"border-radius: 0"
        )
        details_layout.addWidget(line_widget)

        # define the widget for the major and the year of school they are in
        title_widget = QLabel(f"{major} ({progress})")
        title_widget.setStyleSheet("color: black")
        title_widget.setFont(QFont(families[0], 15))
        details_layout.addWidget(title_widget)

        # defile the widget for when they are leaving
        tutor_schedule_widget = QLabel(leaving_at)
        tutor_schedule_widget.setStyleSheet("color: black")
        tutor_schedule_widget.setFont(QFont(families[0], 15))
        details_layout.addWidget(tutor_schedule_widget)

        # format the overall card
        self.setStyleSheet(f"TutorCard {{background-color: {BACK_GREY}; border: 2px solid {BORDER_GREY}}}")

class RoundedImageLabel(QLabel):
    """
    widget for an image with rounded corners. ChatGPT made this for me and as such, I only kind of understand it

    Methods:
        __init__(self, image_path, border_color, corner_radius=20)
            saves the arguments as class variables

        resizeEvent(self, event)
            called on resize. defines the rounded corners and adds them
    """

    def __init__(self, image_path, border_color, corner_radius=20):
        """
        saves the arguments as class variables
        :param image_path: the path to the image
        :param border_color: the color of the border
        :param corner_radius: the radius of the corner
        """
        super().__init__()
        self.pixmap_original = QPixmap(image_path)  # Load the original image
        self.corner_radius = corner_radius
        self.border_color = border_color

    def resizeEvent(self, event):
        if self.pixmap_original.isNull():
            return

        # scale the pixmap to fit the label, maintaining aspect ratio
        scaled_pixmap = self.pixmap_original.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # create a new QPixmap for the result
        rounded_pixmap = QPixmap(scaled_pixmap.size())
        rounded_pixmap.fill(Qt.GlobalColor.transparent)

        # create the painter for drawing
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # draw the image with rounded corners (using clipping path)
        path = QPainterPath()
        r = self.corner_radius  # The radius of the corners
        rect = QRectF(scaled_pixmap.rect())  # Convert QRect to QRectF
        path.addRoundedRect(rect, r, r)  # Add rounded rect path
        painter.setClipPath(path)  # Set clipping path to make the image fit inside

        # draw the image
        painter.drawPixmap(0, 0, scaled_pixmap)

        # now draw the border on top of the image
        border_thickness = 5  # Set the thickness of the border
        border_color = QColor(self.border_color)  # Set the border color (red as an example)

        # create a QPen for the border with specified thickness and color
        pen = QPen(border_color)
        pen.setWidth(border_thickness)  # Set the width of the border
        painter.setPen(pen)  # Apply the pen to the painter
        painter.setBrush(Qt.GlobalColor.transparent)  # No fill for the border

        # draw the rounded rectangle border (without clipping)
        painter.drawRoundedRect(rect, r, r)

        # end the painter to finalize drawing
        painter.end()

        # set the pixmap with the final result (image + border)
        self.setPixmap(rounded_pixmap)

        super().resizeEvent(event)
        self.setFixedWidth(rounded_pixmap.width())

class WillReturn(QLabel):
    """
    widget for showing when a tutor will return

    Methods:
        __init__(self, major, return_time)
            defines the widget
    """
    def __init__(self, major, return_time):
        """
        defines the widget
        :param major: the major that will return
        :param return_time: when the tutor will return as a full string
        """
        super().__init__()

        # define the font
        font_id = QFontDatabase.addApplicationFont("berlin-sans-fb/BRLNSR.TTF")
        if font_id < 0:
            print("Error loading font")
        families = QFontDatabase.applicationFontFamilies(font_id)

        # define constants
        self.spacing = 10
        offset = 30

        # define the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(self.spacing, self.spacing, self.spacing, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        # add a spacer
        spacer = QLabel()
        spacer.setStyleSheet("background: transparent")
        spacer.setFixedHeight(offset - 15)
        main_layout.addWidget(spacer)

        # add the main text
        main_text = QLabel(f"{major}ing\nWill Return {return_time}")
        main_text.setStyleSheet("color: black; background-color: transparent")
        main_text.setFont(QFont(families[0], 25))
        main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(main_text)

        # get the color of the major
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

        # add another spacer
        spacer2 = QLabel()
        spacer2.setStyleSheet(
            f"border: 6px solid; "
            f"border-color: {bar_color} transparent transparent transparent; "
            f"background: transparent"
        )
        spacer2.setFixedSize(QSize(int(self.width() * 5 / 8), offset + 15))
        main_layout.addWidget(spacer2)

        # format the overall widget
        self.setStyleSheet(f"WillReturn {{background-color: {BACK_GREY}; border: 2px solid {BORDER_GREY}}}")

class ScheduleCell(QLabel):
    """
    a widget for the individual cells of the schedule

    Methods:
        __init__(self, major, row, col, dark)
            defines the widget
    """
    def __init__(self, major, row, col, dark):
        """
        defines the widget
        :param major: the abbreviation of the major
        :param row: the row where it will be added (for format reasons)
        :param col: the column where it will be added (for format reasons)
        :param dark: if the cell should be a little darker because it is the current hour
        """
        super().__init__()

        #define colors
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

        #define default border colors
        top_border = 'transparent'
        bottom_border = border_color
        left_border = 'transparent'
        right_border = '#2e2e2e'

        #define default border widths
        right_border_width = '2px'
        left_border_width = '2px'
        bottom_border_width = '3px'

        #define default border styles
        right_border_style = 'solid'

        #set the top border if it is on the top
        if row == 0:
            top_border = border_color

        #set the bottom border if it is on the bottom
        if row == 4:
            bottom_border = border_color
            bottom_border_width = '3px'

        #set the 30-minute mark lines to dashed
        if col % 2 == 0:
            right_border_width = '1px'
            right_border_style = 'dashed'

        #set the left border if we are at the start
        if col == 0:
            left_border = border_color
            left_border_width = '3px'

        #TODO this will need to not be a magic number
        #set the right border if we are at the end
        if col == 15:
            right_border = border_color
            right_border_width = '3px'

        #set the style
        self.setStyleSheet(
            f"background-color: {color}; "
            f"border-width: 4px {right_border_width} {bottom_border_width} {left_border_width}; "
            f"border-style: solid {right_border_style} solid solid; "
            f"border-color: {top_border} {right_border} {bottom_border} {left_border}"
        )

        #set the size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)