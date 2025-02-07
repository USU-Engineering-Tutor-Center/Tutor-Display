import json
import math

from dateutil.rrule import weekday
from numpy.ma.core import floor
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
from datetime import datetime, timedelta

class ExcelManager:
    def __init__(self):
        self.friday_schedule = None
        self.thursday_schedule = None
        self.wednesday_schedule = None
        self.tuesday_schedule = None
        self.monday_schedule = None

        self.tutors = dict(dict())

    def fetch_schedule(self):
        url = os.environ["TUTOR_CENTER_PATH"]
        username = os.environ["TUTOR_CENTER_EMAIL"]
        password = os.environ["TUTOR_CENTER_PASSWORD"]
        relative_url = "/sites/ENGRTCManagementTEST/Shared Documents/General/Tutoring Center Info/Schedule.xlsx"
        # https://usu.sharepoint.com/sites/ENGRTCManagementTEST/Shared%20Documents/General/Tutoring%20Center%20Info/Tutor%20Center%20Teams.xlsx

        ctx_auth = AuthenticationContext(url)
        if ctx_auth.acquire_token_for_user(username, password):
            ctx = ClientContext(url, ctx_auth)

            file = ctx.web.get_file_by_server_relative_url(relative_url)
            ctx.load(file)
            ctx.execute_query()
            last_modified = file.properties["TimeLastModified"]

            with open("tutor_data.json", "r") as file:
                self.tutors = json.load(file)

            with open("daily_schedules.json") as file:
                temp_list = json.load(file)
                self.monday_schedule = temp_list[0]
                self.tuesday_schedule = temp_list[1]
                self.wednesday_schedule = temp_list[2]
                self.thursday_schedule = temp_list[3]
                self.friday_schedule = temp_list[4]

            last_read = datetime.strptime(self.tutors['last_fetch'], "%Y-%m-%d %H:%M:%S.%f")

            if last_read > last_modified - timedelta(hours=7):
                print("up to date")
                print(f"last read: {last_read}")
                print(f"last edited: {last_modified - timedelta(hours=7)}")
                return
            else:
                print("updating")

            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            response = File.open_binary(ctx, relative_url)

            # save data to BytesIO stream
            bytes_file_obj = io.BytesIO()
            bytes_file_obj.write(response.content)
            bytes_file_obj.seek(0)  # set file object to start

            # read file into pandas dataframe
            self.monday_schedule =      pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=3, nrows=6).values.tolist()
            self.tuesday_schedule =     pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=12, nrows=6).values.tolist()
            self.wednesday_schedule =   pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=21, nrows=6).values.tolist()
            self.thursday_schedule =    pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=30, nrows=6).values.tolist()
            self.friday_schedule =      pd.read_excel(bytes_file_obj, sheet_name='Print Schedule', usecols='B:Q', skiprows=39, nrows=6).values.tolist()

            temp_tutor_schedule =       pd.read_excel(bytes_file_obj, sheet_name='Schedule', usecols='A:S', skiprows=10, nrows=200).values.tolist()
            for row in temp_tutor_schedule:
                if str(row[0]) == "nan":
                    continue

                if row[0].lower() not in self.tutors:
                    temp_dict = {'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []}
                    self.tutors[row[0].lower()] = {'schedule': temp_dict, "major": "", 'profile_image': 'default.png', 'progress': "", "name": row[0]}

                self.tutors[row[0].lower()]["schedule"][row[1]] = row[3:]
                self.tutors[row[0].lower()]["major"] = row[2]

            tutor_info =                pd.read_excel(bytes_file_obj, sheet_name='Tutor Info', usecols='A:J', nrows=30).values.tolist()
            for row in tutor_info:
                self.tutors[row[0].lower()]['progress'] = row[3]

                if str(row[9]) != "nan":
                    self.tutors[row[0].lower()]['profile_image'] = row[9]

            with open('tutor_data.json', 'w') as file:
                self.tutors['last_fetch'] = str(datetime.now())
                json.dump(self.tutors, file, indent=4)

            with open("daily_schedules.json", 'w') as file:
                temp_list = [self.monday_schedule, self.tuesday_schedule, self.wednesday_schedule, self.thursday_schedule, self.friday_schedule]
                json.dump(temp_list, file, indent=4)
        else:
            return False

    def get_today_schedule(self):
        self.fetch_schedule()

        today_schedule = None

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

        today_schedule.pop(2)
        return today_schedule

    def get_on_shift(self):
        on_shift = []
        now = datetime.now()
        day_of_week = now.strftime('%A')
        now_index = self.get_now_index()

        for tutor in self.tutors:
            tutor = self.tutors[tutor]

            if "schedule" not in tutor:
                continue

            today_schedule = tutor["schedule"][day_of_week]

            if str(today_schedule[now_index]).lower() in {"cp", "m", "ce", "el", "b"}:
                for j in range(now_index, len(today_schedule)):
                    if today_schedule[j].lower() not in {"cp", "m", "ce", "el", "b"}:
                        end_schedule = j / 2 + 9
                        tutor["here_until"] = f"{int(floor(end_schedule - 1) % 12 + 1)}:{int((end_schedule - floor(end_schedule)) * 60):02d}"
                        break
                else:
                    end_schedule = (len(today_schedule)) / 2 + 9
                    tutor[
                        "here_until"] = f"{int(floor(end_schedule - 1) % 12 + 1)}:{int((end_schedule - floor(end_schedule)) * 60):02d}"

                on_shift.append(tutor)

        return on_shift

    def get_now_index(self):
        now = datetime.now()
        return int((now.timetuple().tm_hour + (math.floor(now.timetuple().tm_min / 30) * 0.5) - 9) * 2)

if __name__ == "__main__":
    em = ExcelManager()
    em.fetch_schedule()

    for i in em.get_on_shift():
        print(i["here_until"])