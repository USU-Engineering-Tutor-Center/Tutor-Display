# import re
# #
# # import requests
# #
# # url = "https://engineering.usu.edu/students/tutoring/tutors"
# HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.13 (KHTML, like Gecko) Mobile/15E148'}
# #
# # response = requests.get(url, headers=HEADERS)
# #
# # if response.status_code == 200:
# #     html_content = response.text
# #     for i, tag in enumerate(re.findall("<img.*?>", html_content)):
# #         print(i, tag)
# #
# #     print("\n\n\n")
# #     print(html_content)
# # else:
# #     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
#
# from requests_html import HTMLSession
#
# session = HTMLSession()
# response = session.get("https://engineering.usu.edu/students/tutoring/tutors", headers=HEADERS)
# response.html.render()
# response.html.render()
#
# html_content = response.html.html
#
# print(re.findall("<img.*?>", html_content))

import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# SharePoint site and credentials
site_url = os.environ["TUTOR_CENTER_PATH"]
username = os.environ["TUTOR_CENTER_EMAIL"]
password = os.environ["TUTOR_CENTER_PASSWORD"]

# Relative URL of the folder in SharePoint
folder_relative_url = "/sites/ENGRTCManagementTEST/Shared%20Documents/Engineering%20Memery"
#https://usu.sharepoint.com/sites/ENGRTCManagementTEST/Shared%20Documents/Engineering%20Memery

# Local path to save the files
local_folder_path = "downloaded_folder"
os.makedirs(local_folder_path, exist_ok=True)

# Authenticate and connect
ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))

# Function to download folder contents
def download_folder(folder_url, local_path):
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    ctx.load(folder)
    ctx.execute_query()

    # List and download files
    files = folder.files.execute_query()
    print("Files:", files)
    for file in files:
        try:
            file_name = file.name
            local_file_path = os.path.join(local_path, file_name)
            print(f"Downloading: {file_name}")
            with open(local_file_path, "wb") as local_file:
                file.download(local_file).execute_query()
            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Error downloading {file_name}: {e}")

    # List and handle subfolders
    subfolders = folder.folders.execute_query()
    print("Subfolders:", subfolders)
    for subfolder in subfolders:
        subfolder_name = subfolder.name
        subfolder_local_path = os.path.join(local_path, subfolder_name)
        os.makedirs(subfolder_local_path, exist_ok=True)
        download_folder(subfolder.serverRelativeUrl, subfolder_local_path)

# Start download
download_folder(folder_relative_url, local_folder_path)
print(f"Download complete. Files saved to: {local_folder_path}")
