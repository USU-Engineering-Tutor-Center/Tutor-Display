from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd

url = os.environ["TUTOR_CENTER_PATH"]
username = os.environ["TUTOR_CENTER_EMAIL"]
password = os.environ["TUTOR_CENTER_PASSWORD"]
relative_url = "/sites/ENGRTCManagementTEST/Shared Documents/General/Tutoring Center Info/Schedule.xlsx"
#https://usu.sharepoint.com/sites/ENGRTCManagementTEST/Shared%20Documents/General/Tutoring%20Center%20Info/Tutor%20Center%20Teams.xlsx
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
    df = pd.read_excel(bytes_file_obj, sheet_name=['Print Schedule', 'Tutor Info'])


else:
    print("Can't authenticate")