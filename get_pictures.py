import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.files.file import File

# SharePoint site and credentials
url = os.environ["TUTOR_CENTER_PATH"]
username = os.environ["TUTOR_CENTER_EMAIL"]
password = os.environ["TUTOR_CENTER_PASSWORD"]

# Relative URL of the folder in SharePoint
folder_url = "/sites/ENGRTCManagementTEST/Shared Documents/Engineering Memery"
#https://usu.sharepoint.com/sites/ENGRTCManagementTEST/Shared%20Documents/Engineering%20Memery

ctx_auth = AuthenticationContext(url)
ctx_auth.acquire_token_for_user(username, password)
ctx = ClientContext(url, ctx_auth)

folder = ctx.web.get_folder_by_server_relative_url(folder_url)
files = folder.files
ctx.load(files)
ctx.execute_query()

def download_large_file(ctx, file_url, local_path):
    response = File.open_binary(ctx, file_url)
    response.raise_for_status()
    with open(local_path, "wb") as local_file:
        for chunk in response.iter_content(32 * 1024):
            local_file.write(chunk)

for file in files:
    file_url = file.serverRelativeUrl
    file_name = file.properties["Name"]
    local_path = os.path.join("downloaded_images", file_name)
    download_large_file(ctx, file_url, local_path)
    print(f"Downloaded {file_name}")