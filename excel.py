from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
from datetime import datetime

class ExcelManager:
    def __init__(self):
        self.friday_schedule = None
        self.thursday_schedule = None
        self.wednesday_schedule = None
        self.tuesday_schedule = None
        self.monday_schedule = None

    def fetch_schedule(self):
        url = os.environ["TUTOR_CENTER_PATH"]
        username = os.environ["TUTOR_CENTER_EMAIL"]
        password = os.environ["TUTOR_CENTER_PASSWORD"]
        relative_url = "/sites/ENGRTCManagementTEST/Shared Documents/General/Tutoring Center Info/Schedule.xlsx"
        # https://usu.sharepoint.com/sites/ENGRTCManagementTEST/Shared%20Documents/General/Tutoring%20Center%20Info/Tutor%20Center%20Teams.xlsx

        ctx_auth = AuthenticationContext(url)
        if ctx_auth.acquire_token_for_user(username, password):
            ctx = ClientContext(url, ctx_auth)
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

if __name__ == "__main__":
    em = ExcelManager()
    print(em.get_today_schedule())