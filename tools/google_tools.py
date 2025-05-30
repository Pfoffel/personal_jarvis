import os
import io
import json
from typing import Optional # Added for type hints
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

# --- Configuration ---
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
]
CLIENT_SECRETS_FILE = 'secrets/credentials.json'


class GoogleAuth:
    def __init__(self, client_secrets_file=CLIENT_SECRETS_FILE,
                 scopes=SCOPES,
                 token_file='secrets/token.json'):
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes
        self.token_file = token_file

    def get_drive_service(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Access token expired, attempting to refresh...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}. Re-authenticating...")
                    creds = None
            if not creds:
                print("No valid credentials found. Initiating new authorization flow...")
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
                try:
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error running local server for authentication: {e}")
                    print("Make sure you have a browser installed and that the redirect URI for your OAuth client in Google Cloud Console is set to 'http://localhost'.")
                    return None
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        try:
            service = build('drive', 'v3', credentials=creds)
            print("Google Drive service initialized successfully.")
            return service
        except HttpError as error:
            print(f"An HTTP error occurred during service build: {error}")
            print(f"Error details: {error.content.decode('utf-8')}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during service build: {e}")
            return None

# --- Google Drive Tool Implementations and Factories ---

# 1. Create Folder
def _create_folder_impl(drive_service, folder_name: str, parent_folder_id: Optional[str] = None):
    """
    Creates a new folder in Google Drive.

    Args:
        drive_service: The authenticated Google Drive API service object.
        folder_name: The name of the new folder.
        parent_folder_id: (Optional) The ID of the parent folder. If None, creates in My Drive root.

    Returns:
        The ID of the created folder, or None if an error occurred.
    """
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    try:
        folder = drive_service.files().create(body=file_metadata, fields='id, name').execute()
        print(f"Folder '{folder.get('name')}' created with ID: {folder.get('id')}")
        return folder.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while creating folder: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while creating folder: {e}")
        return None

def create_folder_tool_factory(drive_service):
    def create_folder_for_agent(folder_name: str, parent_folder_id: Optional[str] = None):
        return _create_folder_impl(drive_service, folder_name, parent_folder_id)
    create_folder_for_agent.__doc__ = _create_folder_impl.__doc__
    return create_folder_for_agent

# 2. Upload File
def _upload_file_impl(drive_service, file_path: str, file_name: str, mime_type: str, parent_folder_id: Optional[str] = None, convert_to_google_doc: bool = False):
    """
    Uploads a new file to Google Drive. Optionally converts it to Google Docs format.

    Args:
        drive_service: The authenticated Google Drive API service object.
        file_path: The local path to the file to upload.
        file_name: The desired name of the file in Google Drive.
        mime_type: The MIME type of the file (e.g., 'text/plain', 'image/jpeg').
        parent_folder_id: (Optional) The ID of the parent folder. If None, uploads to My Drive root.
        convert_to_google_doc: If True, attempts to convert the uploaded file to a Google Docs document.
                               Requires appropriate source file type.

    Returns:
        The ID of the uploaded file, or None if an error occurred.
    """
    file_metadata = {'name': file_name}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    if convert_to_google_doc:
        file_metadata['mimeType'] = 'application/vnd.google-apps.document'
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType',
        ).execute()
        conversion_status = "and converted to Google Doc" if file.get('mimeType') == 'application/vnd.google-apps.document' else ""
        print(f"File '{file.get('name')}' uploaded {conversion_status} with ID: {file.get('id')} (MIME: {file.get('mimeType')})")
        return file.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while uploading file: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while uploading file: {e}")
        return None

def upload_file_tool_factory(drive_service):
    def upload_file_for_agent(file_path: str, file_name: str, mime_type: str, parent_folder_id: Optional[str] = None, convert_to_google_doc: bool = False):
        return _upload_file_impl(drive_service, file_path, file_name, mime_type, parent_folder_id, convert_to_google_doc)
    upload_file_for_agent.__doc__ = _upload_file_impl.__doc__
    return upload_file_for_agent

# 3. Update File Content
def _update_file_content_impl(drive_service, file_id: str, new_file_path: str, new_mime_type: Optional[str] = None, new_name: Optional[str] = None, convert_to_google_doc: bool = False):
    """
    Updates the content and/or metadata of an existing file in Google Drive.
    Optionally converts it to Google Docs format during update.

    Args:
        drive_service: The authenticated Google Drive API service object.
        file_id: The ID of the file to update.
        new_file_path: The local path to the new content for the file.
        new_mime_type: (Optional) The new MIME type of the file.
        new_name: (Optional) The new name for the file.
        convert_to_google_doc: If True, attempts to convert the updated file to a Google Docs document.

    Returns:
        The ID of the updated file, or None if an error occurred.
    """
    file_metadata = {}
    if new_name:
        file_metadata['name'] = new_name
    if convert_to_google_doc:
        file_metadata['mimeType'] = 'application/vnd.google-apps.document'
    media = MediaFileUpload(new_file_path, mimetype=new_mime_type, resumable=True)
    try:
        updated_file = drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType'
        ).execute()
        conversion_status = "and converted to Google Doc" if updated_file.get('mimeType') == 'application/vnd.google-apps.document' else ""
        print(f"File '{updated_file.get('name')}' (ID: {updated_file.get('id')}) updated {conversion_status} successfully. (MIME: {updated_file.get('mimeType')})")
        return updated_file.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while updating file: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while updating file: {e}")
        return None

def update_file_content_tool_factory(drive_service):
    def update_file_content_for_agent(file_id: str, new_file_path: str, new_mime_type: Optional[str] = None, new_name: Optional[str] = None, convert_to_google_doc: bool = False):
        return _update_file_content_impl(drive_service, file_id, new_file_path, new_mime_type, new_name, convert_to_google_doc)
    update_file_content_for_agent.__doc__ = _update_file_content_impl.__doc__
    return update_file_content_for_agent

# 4. Download Binary File
def _download_binary_file_impl(drive_service, file_id: str, local_save_path: str):
    """
    Downloads a non-Google Workspace file from Google Drive.

    Args:
        drive_service: The authenticated Google Drive API service object.
        file_id: The ID of the file to download.
        local_save_path: The local path where the file should be saved.

    Returns:
        True if the file was downloaded successfully, False otherwise.
    """
    try:
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")
        with open(local_save_path, 'wb') as f:
            f.write(fh.getvalue())
        print(f"File downloaded successfully to: {local_save_path}")
        return True
    except HttpError as error:
        print(f"An HTTP error occurred while downloading file: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while downloading file: {e}")
        return False

def download_binary_file_tool_factory(drive_service):
    def download_binary_file_for_agent(file_id: str, local_save_path: str):
        return _download_binary_file_impl(drive_service, file_id, local_save_path)
    download_binary_file_for_agent.__doc__ = _download_binary_file_impl.__doc__
    return download_binary_file_for_agent

# 5. Export Google Workspace Document
def _export_google_workspace_doc_impl(drive_service, file_id: str, export_mime_type: str, local_save_path: str):
    """
    Exports a Google Workspace document (e.g., Docs, Sheets) to a specified MIME type.

    Args:
        drive_service: The authenticated Google Drive API service object.
        file_id: The ID of the Google Workspace document to export.
        export_mime_type: The MIME type to export to (e.g., 'application/pdf').
        local_save_path: The local path where the exported file should be saved.

    Returns:
        True if the file was exported successfully, False otherwise.
    """
    try:
        request = drive_service.files().export(fileId=file_id, mimeType=export_mime_type)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Export progress: {int(status.progress() * 100)}%")
        with open(local_save_path, 'wb') as f:
            f.write(fh.getvalue())
        print(f"Google Workspace document exported successfully to: {local_save_path}")
        return True
    except HttpError as error:
        print(f"An HTTP error occurred while exporting document: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while exporting document: {e}")
        return False

def export_google_workspace_doc_tool_factory(drive_service):
    def export_google_workspace_doc_for_agent(file_id: str, export_mime_type: str, local_save_path: str):
        return _export_google_workspace_doc_impl(drive_service, file_id, export_mime_type, local_save_path)
    export_google_workspace_doc_for_agent.__doc__ = _export_google_workspace_doc_impl.__doc__
    return export_google_workspace_doc_for_agent

# 6. List Files and Folders
def _list_files_and_folders_impl(drive_service, folder_id: Optional[str] = None, page_size: int = 100):
    """
    Lists files and folders in Google Drive, with optional query filtering and pagination.

    Args:
        drive_service: The authenticated Google Drive API service object.
        folder_id: (Optional) ID of the folder in which folders and files should be listed from, if not provided it will be the root folder.
        page_size: The number of items to return per page.

    Returns:
        A list of dictionaries, each representing a file or folder, or an empty list if an error occurred.
    """
    results = []
    page_token = None
    if folder_id:
        query = f"'{folder_id}' in parents and trashed = false"
    else:
        query = f"'root' in parents and trashed = false"
    try:
        while True:
            params = {
                'pageSize': page_size,
                'fields': "nextPageToken, files(id, name, mimeType, parents, modifiedTime)",
                'spaces': 'drive',
            }
            if query:
                params['q'] = query
            if page_token:
                params['pageToken'] = page_token
            response = drive_service.files().list(**params).execute()
            items = response.get('files', [])
            results.extend(items)
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
        if not results:
            print("No files or folders found matching the criteria.")
        return results
    except HttpError as error:
        print(f"An HTTP error occurred while listing files: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while listing files: {e}")
        return []

def list_files_and_folders_tool_factory(drive_service):
    def list_files_and_folders_for_agent(query: Optional[str] = None, page_size: int = 100):
        return _list_files_and_folders_impl(drive_service, query, page_size)
    list_files_and_folders_for_agent.__doc__ = _list_files_and_folders_impl.__doc__
    return list_files_and_folders_for_agent

# 7. Create Google Doc
def _create_google_doc_impl(drive_service, doc_name: str, parent_folder_id: Optional[str] = None):
    """
    Creates a new EMPTY Google Docs document in Google Drive.

    Args:
        drive_service: The authenticated Google Drive API service object.
        doc_name: The desired name of the Google Docs document.
        parent_folder_id: (Optional) The ID of the parent folder.

    Returns:
        The ID of the created Google Docs document, or None if an error occurred.
    """
    file_metadata = {
        'name': doc_name,
        'mimeType': 'application/vnd.google-apps.document'
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    try:
        doc = drive_service.files().create(body=file_metadata, fields='id, name, mimeType').execute()
        print(f"Google Docs document '{doc.get('name')}' created with ID: {doc.get('id')} (MIME: {doc.get('mimeType')})")
        return doc.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while creating Google Docs document: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while creating Google Docs document: {e}")
        return None

def create_google_doc_tool_factory(drive_service):
    def create_google_doc_for_agent(doc_name: str, parent_folder_id: Optional[str] = None):
        return _create_google_doc_impl(drive_service, doc_name, parent_folder_id)
    create_google_doc_for_agent.__doc__ = _create_google_doc_impl.__doc__
    return create_google_doc_for_agent


if __name__ == '__main__':
    print("--- Testing GoogleAuth and Standalone Google Drive Tools (Factory Pattern) ---")

    if not os.path.exists('secrets'):
        os.makedirs('secrets')
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"Warning: Client secrets file '{CLIENT_SECRETS_FILE}' not found.")
        print("Please ensure it is present and correctly configured for actual Google Drive operations.")
        with open(CLIENT_SECRETS_FILE, 'w') as f:
            json.dump({"installed": {"client_id": "YOUR_CLIENT_ID", "project_id": "YOUR_PROJECT_ID", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_secret": "YOUR_CLIENT_SECRET", "redirect_uris": ["http://localhost"]}}, f)
        print(f"Created a dummy '{CLIENT_SECRETS_FILE}'. Replace with your actual credentials.")

    auth = GoogleAuth()
    drive_service = auth.get_drive_service()

    if drive_service:
        print("Successfully obtained Google Drive service.")

        print("\n--- Example: Listing top 5 files/folders ---")
        try:
            # Get the agent-facing function from the factory
            list_files_func = list_files_and_folders_tool_factory(drive_service)
            # Call the agent-facing function
            files_list = list_files_func(page_size=5)

            if files_list:
                print(f"Found {len(files_list)} files/folders:")
                for f_item in files_list:
                    print(f"  - {f_item.get('name')} ({f_item.get('mimeType')}) (ID: {f_item.get('id')})")
            elif files_list == []:
                print("No files found or an empty list was returned by list_files_and_folders.")
            else:
                print("Could not list files (method might have returned None or other error state).")

            print("\n--- Example: Creating a test folder ---")
            test_folder_name = "Test Folder Created by Factory - OK to Delete"
            # Get the agent-facing function from the factory
            create_folder_func = create_folder_tool_factory(drive_service)
            # Call the agent-facing function
            folder_id = create_folder_func(folder_name=test_folder_name)

            if folder_id:
                print(f"Test folder '{test_folder_name}' created successfully with ID: {folder_id}")
            else:
                print(f"Failed to create test folder '{test_folder_name}'. This might be expected if authentication failed or a real 'credentials.json' is not present.")

        except HttpError as e:
            print(f"An HttpError occurred during tool execution: {e}")
            print("This is often due to authentication issues or insufficient permissions.")
        except Exception as e:
            print(f"An unexpected error occurred during tool execution: {e}")
    else:
        print("Failed to obtain Google Drive service. Please check your 'secrets/credentials.json' file and the authentication flow.")

    print("\n--- Testing complete ---")
