import json
import math
from numpy.ma.core import floor
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
from datetime import datetime, timedelta


# noinspection PyTypeChecker
class ExcelManager:
    """
    manages information grabbed from the spreadsheet

    Methods:
        __init__(self)
            defines variables
        fetch_schedule(self)
            gets the schedule information from the spreadsheet
        get_today_schedule(self)
            specifically gets the schedule for today
        get_on_shift(self)
            gets a list of all the tutors on shift
        get_now_index()
            gets the index in today's schedule that corresponds to the current time
    """
    def __init__(self):
        """
        defines variables
        """

        #set up the variables
        self.friday_schedule = None
        self.thursday_schedule = None
        self.wednesday_schedule = None
        self.tuesday_schedule = None
        self.monday_schedule = None
        self.tutors = dict(dict())

    def fetch_schedule(self):
        """
        gets the schedule information from the spreadsheet
        """

        # SharePoint site and credentials
        url = os.environ["TUTOR_CENTER_PATH"]
        username = os.environ["TUTOR_CENTER_EMAIL"]
        password = os.environ["TUTOR_CENTER_PASSWORD"]
        relative_url = "/sites/ENGRTCManagementTEST/Shared Documents/General/Tutoring Center Info/Schedule.xlsx"

        # Authenticate
        ctx_auth = AuthenticationContext(url)
        ctx_auth.acquire_token_for_user(username, password)
        ctx = ClientContext(url, ctx_auth)

        #find the last time the share point was modified
        file = ctx.web.get_file_by_server_relative_url(relative_url)
        ctx.load(file)
        ctx.execute_query()
        last_modified = file.properties["TimeLastModified"]

        #read the saved json files and save them to variables
        with open("tutor_data.json", "r") as file:
            self.tutors = json.load(file)

        with open("daily_schedules.json") as file:
            temp_list = json.load(file)
            self.monday_schedule = temp_list[0]
            self.tuesday_schedule = temp_list[1]
            self.wednesday_schedule = temp_list[2]
            self.thursday_schedule = temp_list[3]
            self.friday_schedule = temp_list[4]

        # find the last time we updated our list
        last_read = datetime.strptime(self.tutors['last_fetch'], "%Y-%m-%d %H:%M:%S.%f")

        #if our list is up to date then do nothing
        if last_read > last_modified - timedelta(hours=7):
            return

        #get the schedule
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        response = File.open_binary(ctx, relative_url)

        # save data to BytesIO stream
        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)  # set file object to start

        #get the different schedules for the different days
        self.monday_schedule =      pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=3, nrows=6).values.tolist()
        self.tuesday_schedule =     pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=12, nrows=6).values.tolist()
        self.wednesday_schedule =   pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=21, nrows=6).values.tolist()
        self.thursday_schedule =    pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=30, nrows=6).values.tolist()
        self.friday_schedule =      pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=39, nrows=6).values.tolist()

        #get the all the schedule information for all the tutors and iterate through it
        temp_tutor_schedule =       pd.read_excel(bytes_file_obj, sheet_name='Schedule', usecols='A:S', skiprows=10, nrows=200).values.tolist()
        for row in temp_tutor_schedule:
            #get the name of the tutor
            tutor_name = row[0]

            #ignore if it is empty
            if str(tutor_name) == "nan":
                continue

            #if we have run into a tutor who it has not seen before
            if tutor_name.lower() not in self.tutors:
                #build an empty tutor and add it to the dictionary of tutors
                empty_schedule_dict = {'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []}
                self.tutors[tutor_name.lower()] = {
                    'schedule': empty_schedule_dict,
                    "major": "",
                    'profile_image': 'default.png',
                    'academic_class': "",
                    "name": tutor_name
                }

            #add the schedule and the major to the tutor
            self.tutors[row[0].lower()]["schedule"][row[1]] = row[3:]
            self.tutors[row[0].lower()]["major"] = row[2]

        #get the information from all the tutors and iterate over it
        tutor_info = pd.read_excel(bytes_file_obj, sheet_name='Tutor Info', usecols='A:J', nrows=30).values.tolist()
        for row in tutor_info:
            # get the name of the tutor
            tutor_name = row[0]

            #add the academic class to the tutor they belong to
            self.tutors[tutor_name.lower()]['academic_class'] = row[3]

            #update the profile picture if one is specified
            if str(row[9]) != "nan":
                self.tutors[tutor_name.lower()]['profile_image'] = row[9]

        #save the tutor dictionary to tutor_data.json
        with open('tutor_data.json', 'w') as file:
            #update the time that we last updated
            self.tutors['last_fetch'] = str(datetime.now())

            #save the dictionary
            json.dump(self.tutors, file, indent=4)

        #save the schedule dictionary to daily_schedules.json
        with open("daily_schedules.json", 'w') as file:
            #organize it in a list
            temp_list = [self.monday_schedule, self.tuesday_schedule, self.wednesday_schedule, self.thursday_schedule, self.friday_schedule]

            #save the dictionary
            json.dump(temp_list, file, indent=4)

    def get_today_schedule(self):
        """
        gets today's schedule
        :return: today's schedule
        """

        #make sure that you have an updated schedule
        self.fetch_schedule()

        #get the schedule for the specific weekday of today
        match datetime.today().weekday():
            case 0:
                today_schedule = self.monday_schedule
            case 1:
                today_schedule = self.tuesday_schedule
            case 2:
                today_schedule = self.wednesday_schedule
            case 3:
                today_schedule = self.thursday_schedule
            case 4:
                today_schedule = self.friday_schedule
            case _: today_schedule = None

        #remove the hidden extra row from the data
        today_schedule.pop(2)

        #return the schedule
        return today_schedule

    def get_on_shift(self):
        """
        finds all the tutors who are currently on shift
        :return: a list of all the tutors on shift
        """
        #initizize the return list
        on_shift = []

        #get the day of the week
        day_of_week = datetime.now().strftime('%A')

        #get the index the corresponds to the current time block
        now_index = self.get_now_index()

        #loop through all the tutors
        for tutor in self.tutors:
            tutor = self.tutors[tutor]

            #skip empty tutors
            if "schedule" not in tutor:
                continue

            #get the tutors schedule for the day
            tutors_schedule = tutor["schedule"][day_of_week]

            #see if the tutor is currently on shift
            if str(tutors_schedule[now_index]).lower() in {"cp", "m", "ce", "el", "b"}:
                #loop until the tutor is not on shift
                for j in range(now_index, len(tutors_schedule)):
                    #if the tutor is now not on shift
                    if tutors_schedule[j].lower() not in {"cp", "m", "ce", "el", "b"}:
                        #get the time block for the current value of j
                        end_schedule = j / 2 + 9

                        #get the current hour and minute
                        current_hour = int(floor(end_schedule - 1) % 12 + 1)
                        current_minute = int((end_schedule - floor(end_schedule)) * 60)

                        #update the tutors "here_until" value
                        tutor["here_until"] = f"{current_hour}:{current_minute:02d}"

                        #stop looping
                        break
                # fun python feature. This will only run if the for loop finished without breaking
                else:
                    #get time block for the end of the day
                    end_schedule = (len(tutors_schedule)) / 2 + 9

                    # get the current hour and minute
                    current_hour = int(floor(end_schedule - 1) % 12 + 1)
                    current_minute = int((end_schedule - floor(end_schedule)) * 60)

                    #update the tutor's "here_until" value
                    tutor["here_until"] = f"{current_hour}:{current_minute:02d}"

                #add the tutor to the return list
                on_shift.append(tutor)

        #return the values
        return on_shift

    @staticmethod #this is a decorator and just shows that this method doesn't do anything with the class itself
    def get_now_index():
        """
        gets the current index corresponding to the current time
        :return: the index corresponding to the current time
        """

        #get the current time
        now = datetime.now()

        #convert the current time to a fractional hour
        hour = now.timetuple().tm_hour
        fractional_hour = math.floor(now.timetuple().tm_min / 30) * 0.5
        hour = hour + fractional_hour

        #shift the hour so that index 0 = 9am and then multiply by 2 to account for the half hours
        return int((hour - 9) * 2)

#test the library
if __name__ == "__main__":
    em = ExcelManager()
    em.fetch_schedule()

    for i in em.get_on_shift():
        print(i["here_until"])