import json
import math
import os
import pandas as pd
from datetime import datetime
from numpy.ma.core import floor

# noinspection PyTypeChecker
class ExcelManager:
    """
    Manages information grabbed from the local schedule spreadsheet.

    Methods:
        __init__(self)
            Defines variables.
        fetch_schedule(self)
            Gets the schedule information from the local Excel file.
        get_today_schedule(self)
            Specifically gets the schedule for today.
        get_on_shift(self)
            Gets a list of all the tutors on shift.
        get_now_index()
            Gets the index in today's schedule that corresponds to the current time.
    """
    def __init__(self):
        """
        Defines variables.
        """
        # Set up the variables
        self.friday_schedule = None
        self.thursday_schedule = None
        self.wednesday_schedule = None
        self.tuesday_schedule = None
        self.monday_schedule = None
        self.tutors = dict(dict())

    def fetch_schedule(self):
        """
        Gets the schedule information from the local spreadsheet file (Schedule.xlsx).
        Uses caching to avoid reprocessing if the file hasn't changed since the last run.
        """
        # Define local file paths
        schedule_file_path = "data/Schedule.xlsx"
        tutor_cache_path = "data/tutor_data.json"
        schedule_cache_path = "data/daily_schedules.json"

        # --- Check if local Excel file exists ---
        if not os.path.exists(schedule_file_path):
            print(f"Error: '{schedule_file_path}' not found. Cannot update schedule.")
            # Try to load from cache even if Excel file is missing, in case old data is sufficient.
            try:
                with open(tutor_cache_path, "r") as file:
                    self.tutors = json.load(file)
                with open(schedule_cache_path) as file:
                    temp_list = json.load(file)
                    self.monday_schedule = temp_list[0]
                    self.tuesday_schedule = temp_list[1]
                    self.wednesday_schedule = temp_list[2]
                    self.thursday_schedule = temp_list[3]
                    self.friday_schedule = temp_list[4]
            except FileNotFoundError:
                print("No cache found. Data remains uninitialized.")
            return

        # --- Caching logic: Compare cache time with file modification time ---
        do_update = False
        last_read_time = None

        try:
            # Read tutor data cache
            with open(tutor_cache_path, "r") as file:
                self.tutors = json.load(file)
            # Read schedule structure cache
            with open(schedule_cache_path) as file:
                temp_list = json.load(file)
                self.monday_schedule = temp_list[0]
                self.tuesday_schedule = temp_list[1]
                self.wednesday_schedule = temp_list[2]
                self.thursday_schedule = temp_list[3]
                self.friday_schedule = temp_list[4]

            # Get the timestamp from the last successful cache write
            last_read_time = datetime.strptime(self.tutors['last_fetch'], "%Y-%m-%d %H:%M:%S.%f")

        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            do_update = True

        # Get modification time of the source Excel file
        excel_mod_time = datetime.fromtimestamp(os.path.getmtime(schedule_file_path))

        # If cache exists and is newer than the Excel file, no need to update.
        if not do_update and last_read_time > excel_mod_time:
            # print("Cache is up to date.") # Optional: for debugging
            return

        # --- Process Excel file ---
        print("Updating schedule from local file...")
        self.tutors = {}
        self.monday_schedule = []
        self.tuesday_schedule = []
        self.wednesday_schedule = []
        self.thursday_schedule = []
        self.friday_schedule = []

        # Read data from the different sheets/sections of the Excel file
        try:
            self.monday_schedule = pd.read_excel(schedule_file_path, sheet_name='Print Schedule', usecols='B:AC', skiprows=3, nrows=6).values.tolist()
            self.tuesday_schedule = pd.read_excel(schedule_file_path, sheet_name='Print Schedule', usecols='B:AC', skiprows=12, nrows=6).values.tolist()
            self.wednesday_schedule = pd.read_excel(schedule_file_path, sheet_name='Print Schedule', usecols='B:AC', skiprows=21, nrows=6).values.tolist()
            self.thursday_schedule = pd.read_excel(schedule_file_path, sheet_name='Print Schedule', usecols='B:AC', skiprows=30, nrows=6).values.tolist()
            self.friday_schedule = pd.read_excel(schedule_file_path, sheet_name='Print Schedule', usecols='B:AC', skiprows=39, nrows=6).values.tolist()
            temp_tutor_schedule = pd.read_excel(schedule_file_path, sheet_name='Schedule', usecols='A:AE', skiprows=10, nrows=200).values.tolist()
            tutor_info = pd.read_excel(schedule_file_path, sheet_name='Tutor Info', usecols='A:J', nrows=30).values.tolist()
        except Exception as e:
            print(f"Error reading Excel file '{schedule_file_path}': {e}")
            return

        schedule_list = [self.monday_schedule, self.tuesday_schedule, self.wednesday_schedule, self.thursday_schedule, self.friday_schedule]

        # --- Data processing logic (unchanged) ---

        # Simplify the schedules to just be when we are open on that day
        for index, schedule in enumerate(schedule_list):
            first_open_index = 28
            last_open_index = 0

            # Find the earliest and the latest that we have a tutor here
            for row in schedule:
                for col, value in enumerate(row):
                    if str(value).lower() != "n": # Added str() conversion for safety
                        if col < first_open_index:
                            first_open_index = col
                        # Use elif for slight optimization and correctness in finding last index
                        if col > last_open_index:
                            last_open_index = col

            last_open_index += 1

            # Set all the times that we are not open to "C" so that we can know not to include them
            for row_index in range(len(schedule)):
                schedule_list[index][row_index] = ["C"] * first_open_index + schedule_list[index][row_index][first_open_index:last_open_index] + ["C"] * (len(schedule_list[index][row_index]) - last_open_index)

        # Get all the schedule information for all the tutors and iterate through it
        for row in temp_tutor_schedule:
            # Get the name of the tutor
            tutor_name = row[0]

            # Ignore if it is empty
            if pd.isna(tutor_name): # More reliable check for pandas NaN
                continue

            for j in range(len(row)):
                if pd.isna(row[j]):
                    row[j] = ""

            # If we have run into a tutor who it has not seen before
            if tutor_name.lower() not in self.tutors:
                # Build an empty tutor and add it to the dictionary of tutors
                empty_schedule_dict = {'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []}
                self.tutors[tutor_name.lower()] = {
                    'schedule': empty_schedule_dict,
                    "major": "",
                    'profile_image': 'default.png',
                    'academic_class': "",
                    "name": tutor_name
                }

            # Add the schedule and the major to the tutor
            self.tutors[row[0].lower()]["schedule"][row[1]] = row[3:]
            self.tutors[row[0].lower()]["major"] = row[2]

        # Get the information from all the tutors and iterate over it
        for row in tutor_info:
            # Get the name of the tutor
            tutor_name = row[0]
            if pd.isna(tutor_name):
                continue

            # Add the academic class to the tutor they belong to
            if tutor_name.lower() in self.tutors:
                self.tutors[tutor_name.lower()]['academic_class'] = row[3]

                # Update the profile picture if one is specified
                if not pd.isna(row[9]):
                    self.tutors[tutor_name.lower()]['profile_image'] = str(row[9]) # Ensure string conversion

        # --- Cache saving logic ---
        # Save the tutor dictionary to tutor_data.json
        with open(tutor_cache_path, 'w') as file:
            # Update the time that we last updated
            self.tutors['last_fetch'] = str(datetime.now())
            json.dump(self.tutors, file, indent=4)

        # Save the schedule dictionary to daily_schedules.json
        with open(schedule_cache_path, 'w') as file:
            json.dump(schedule_list, file, indent=4)

    def get_today_schedule(self):
        """
        Gets today's schedule.
        :return: today's schedule list or None if weekend/error.
        """
        # Make sure that you have an updated schedule (or load from cache)
        self.fetch_schedule()

        # Get the schedule for the specific weekday of today
        weekday = datetime.today().weekday()
        if weekday == 0:
            today_schedule = self.monday_schedule
        elif weekday == 1:
            today_schedule = self.tuesday_schedule
        elif weekday == 2:
            today_schedule = self.wednesday_schedule
        elif weekday == 3:
            today_schedule = self.thursday_schedule
        elif weekday == 4:
            today_schedule = self.friday_schedule
        else:
            today_schedule = None

        # Check if schedule data exists and remove the hidden extra row from the data
        if today_schedule and len(today_schedule) > 2:
            schedule_copy = list(today_schedule) # Create copy to avoid modifying class attribute repeatedly
            schedule_copy.pop(2)
            return schedule_copy
        return today_schedule

    def get_on_shift(self):
        """
        Finds all the tutors who are currently on shift.
        :return: A list of all the tutors on shift.
        """
        # Ensure data is loaded
        self.fetch_schedule()

        # Initialize the return list
        on_shift = []

        # Get the day of the week
        day_of_week = datetime.now().strftime('%A')

        # Get the index that corresponds to the current time block
        try:
            now_index = self.get_now_index()
        except ValueError: # Handle times outside operating hours if get_now_index raises error
            return []

        # Loop through all the tutors in the dictionary
        for tutor_name, tutor_data in self.tutors.items():
            # Skip metadata keys like 'last_fetch'
            if "schedule" not in tutor_data:
                continue

            # Get the tutor's schedule for the day
            try:
                tutors_schedule = tutor_data["schedule"][day_of_week]
            except KeyError:
                continue # Tutor might not have schedule data for this day

            # Basic validation of schedule length and index range
            if not isinstance(tutors_schedule, list) or not (0 <= now_index < len(tutors_schedule)):
                continue

            # Check if the tutor is currently on shift based on schedule code
            if str(tutors_schedule[now_index]).lower() in {"cp", "m", "ce", "el", "b"}:
                # Find end time: loop until the tutor is not on shift
                end_index = len(tutors_schedule) # Default to end of schedule length
                for j in range(now_index + 1, len(tutors_schedule)):
                    if str(tutors_schedule[j]).lower() not in {"cp", "m", "ce", "el", "b"}:
                        end_index = j
                        break

                # Calculate end time string
                end_schedule_hour = end_index / 2.0 + 7.0 # 7 AM start, 0.5 hour increments
                hour = int(floor(end_schedule_hour))
                minute = int((end_schedule_hour - hour) * 60)
                # Format to 12-hour clock
                display_hour = hour % 12
                if display_hour == 0:
                    display_hour = 12 # Midnight or Noon case

                tutor_data["here_until"] = f"{display_hour}:{minute:02d}"
                on_shift.append(tutor_data)

        return on_shift

    @staticmethod
    def get_now_index():
        """
        Gets the current index corresponding to the current time.
        Index 0 corresponds to 7:00 AM - 7:30 AM.
        :return: The index corresponding to the current time.
        :raises ValueError: If time is outside common schedule range (e.g., before 7 AM).
        """
        now = datetime.now()

        # Convert the current time to a fractional hour (e.g., 9:15 -> 9.25, 9:30 -> 9.5)
        # Round down to nearest half hour slot for index calculation
        hour = now.hour
        minute = now.minute
        if minute < 30:
            fractional_part = 0.0
        else:
            fractional_part = 0.5

        time_value = hour + fractional_part

        # Shift the hour so that index 0 = 7am (assuming schedule starts at 7 AM)
        # (time_value - 7) * 2 -> (7.0 - 7) * 2 = 0; (7.5 - 7) * 2 = 1; (8.0 - 7) * 2 = 2
        index = int((time_value - 7) * 2)

        if index < 0:
            raise ValueError("Time is before schedule start (7:00 AM).")

        return index

# Test the library
if __name__ == "__main__":
    em = ExcelManager()
    print("Fetching schedule data...")
    em.fetch_schedule()
    print("Schedule fetch complete.")

    print("\n--- Today's Schedule Structure ---")
    today_sched = em.get_today_schedule()
    if today_sched:
        for row in today_sched:
            print(row[:10]) # Print first few columns for brevity
    else:
        print("No schedule available for today.")

    print("\n--- Tutors Currently On Shift ---")
    on_shift_tutors = em.get_on_shift()
    if on_shift_tutors:
        for tutor in on_shift_tutors:
            print(f"{tutor['name']} (Major: {tutor['major']}) - Here until: {tutor['here_until']}")
    else:
        print("No tutors currently on shift.")