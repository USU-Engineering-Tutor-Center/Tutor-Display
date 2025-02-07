import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.files.file import File

class GetPictures:
    def get_pictures(self):
        # SharePoint site and credentials
        url = os.environ["TUTOR_CENTER_PATH"]
        username = os.environ["TUTOR_CENTER_EMAIL"]
        password = os.environ["TUTOR_CENTER_PASSWORD"]

        # Relative URL of the folder in SharePoint
        folder_url = "/sites/ENGRTCManagementTEST/Shared Documents/General/Tutoring Center Info/Pictures For Display"

        # Local folder to store images
        local_folder = "Images"

        # Authenticate
        ctx_auth = AuthenticationContext(url)
        ctx_auth.acquire_token_for_user(username, password)
        ctx = ClientContext(url, ctx_auth)

        # Get list of files in SharePoint folder
        folder = ctx.web.get_folder_by_server_relative_url(folder_url)
        files = folder.files
        ctx.load(files)
        ctx.execute_query()

        # Ensure local folder exists
        os.makedirs(local_folder, exist_ok=True)

        # Get list of existing local files
        local_files = set(os.listdir(local_folder))

        # Get list of images from SharePoint
        sharepoint_files = set()
        for file in files:
            file_name = file.properties["Name"]
            file_url = file.serverRelativeUrl

            # Only process image files
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                sharepoint_files.add(file_name)
                local_path = os.path.join(local_folder, file_name)

                # Download only if not already present
                if file_name not in local_files:
                    response = File.open_binary(ctx, file_url)
                    response.raise_for_status()
                    with open(local_path, "wb") as local_file:
                        for chunk in response.iter_content(32 * 1024):
                            local_file.write(chunk)
                    print(f"Downloaded {file_name}")

        # Delete local images that are no longer in SharePoint
        for local_file in local_files:
            if local_file not in sharepoint_files:
                os.remove(os.path.join(local_folder, local_file))
                print(f"Deleted {local_file} (no longer in SharePoint)")

if __name__ == "__main__":
    gp = GetPictures()
    gp.get_pictures()