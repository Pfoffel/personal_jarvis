import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

# --- Configuration ---
# Define the scopes your application needs.
# It's best practice to request the narrowest possible scopes.
# For full file management, 'https://www.googleapis.com/auth/drive' is needed.
# For app-specific files, 'https://www.googleapis.com/auth/drive.file' is often sufficient.
# Refer to the documentation for more scopes:
# https://developers.google.com/drive/api/guides/api-reference#rest-resource:-files
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',  # Access to files created or opened by the app
    'https://www.googleapis.com/auth/drive.metadata.readonly', # Read-only access to file metadata
    # 'https://www.googleapis.com/auth/drive', # Full, permissive access (use with caution)
]

# The path to your client secrets file downloaded from Google Cloud Console.
# IMPORTANT: In a production web application, you should load these credentials
# from environment variables or a secure secrets management system, NOT directly
# from a file committed to your repository.
CLIENT_SECRETS_FILE = 'secrets/credentials.json'

# The redirect URI configured in your Google Cloud project for "Web application" client ID.
# This must match exactly what you entered in the Google Cloud Console.
# REDIRECT_URI = 'http://localhost:5000/oauth2callback' # Example for a local Flask app

# --- Authentication and Authorization ---

def get_google_drive_service():
    """
    Authenticates the user and returns a Google Drive API service object.
    """
    creds = None
    
    if os.path.exists('secrets/token.json'):
        creds = Credentials.from_authorized_user_file('secrets/token.json', SCOPES)

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
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            
            # --- IMPORTANT CHANGE HERE ---
            # Use run_local_server() to handle the redirect automatically.
            # It will open a browser, handle the redirect, and fetch the token.
            # You usually don't need to manually enter the URL.
            try:
                creds = flow.run_local_server(port=0) # port=0 tells it to find an available port
            except Exception as e:
                print(f"Error running local server for authentication: {e}")
                print("Make sure you have a browser installed and that the redirect URI for your OAuth client in Google Cloud Console is set to 'http://localhost' (or a specific port if desired, but 0 is easiest).")
                return None # Exit if authentication fails
            # --- END IMPORTANT CHANGE ---

        with open('secrets/token.json', 'w') as token:
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

# --- Core Google Drive File Management Operations ---

def create_folder(service, folder_name, parent_folder_id=None):
    """
    Creates a new folder in Google Drive.

    Args:
        service: Google Drive API service object.
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
        folder = service.files().create(body=file_metadata, fields='id, name').execute()
        print(f"Folder '{folder.get('name')}' created with ID: {folder.get('id')}")
        return folder.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while creating folder: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while creating folder: {e}")
        return None

def upload_file(service, file_path, file_name, mime_type, parent_folder_id=None):
    """
    Uploads a new file to Google Drive.

    Args:
        service: Google Drive API service object.
        file_path: The local path to the file to upload.
        file_name: The desired name of the file in Google Drive.
        mime_type: The MIME type of the file (e.g., 'text/plain', 'image/jpeg').
        parent_folder_id: (Optional) The ID of the parent folder. If None, uploads to My Drive root.

    Returns:
        The ID of the uploaded file, or None if an error occurred.
    """
    file_metadata = {'name': file_name}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
        print(f"File '{file.get('name')}' uploaded with ID: {file.get('id')}")
        return file.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while uploading file: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while uploading file: {e}")
        return None

def update_file_content(service, file_id, new_file_path, new_mime_type=None, new_name=None):
    """
    Updates the content and/or metadata of an existing file in Google Drive.

    Args:
        service: Google Drive API service object.
        file_id: The ID of the file to update.
        new_file_path: The local path to the new content for the file.
        new_mime_type: (Optional) The new MIME type of the file.
        new_name: (Optional) The new name for the file.

    Returns:
        The ID of the updated file, or None if an error occurred.
    """
    file_metadata = {}
    if new_name:
        file_metadata['name'] = new_name
    if new_mime_type:
        file_metadata['mimeType'] = new_mime_type

    media = MediaFileUpload(new_file_path, mimetype=new_mime_type, resumable=True)
    try:
        updated_file = service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        print(f"File '{updated_file.get('name')}' (ID: {updated_file.get('id')}) updated successfully.")
        return updated_file.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while updating file: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while updating file: {e}")
        return None

def download_binary_file(service, file_id, local_save_path):
    """
    Downloads a non-Google Workspace file from Google Drive.

    Args:
        service: Google Drive API service object.
        file_id: The ID of the file to download.
        local_save_path: The local path where the file should be saved.

    Returns:
        True if the file was downloaded successfully, False otherwise.
    """
    try:
        request = service.files().get_media(fileId=file_id)
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

def export_google_workspace_doc(service, file_id, export_mime_type, local_save_path):
    """
    Exports a Google Workspace document (e.g., Docs, Sheets) to a specified MIME type.

    Args:
        service: Google Drive API service object.
        file_id: The ID of the Google Workspace document to export.
        export_mime_type: The MIME type to export to (e.g., 'application/pdf',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document' for DOCX).
        local_save_path: The local path where the exported file should be saved.

    Returns:
        True if the file was exported successfully, False otherwise.
    """
    try:
        request = service.files().export(fileId=file_id, mimeType=export_mime_type)
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

def list_files_and_folders(service, query=None, page_size=100):
    """
    Lists files and folders in Google Drive, with optional query filtering and pagination.

    Args:
        service: Google Drive API service object.
        query: (Optional) A query string to filter results (e.g., "mimeType='image/jpeg'").
               Refer to https://developers.google.com/drive/api/guides/search-files for query syntax.
        page_size: The number of items to return per page.

    Returns:
        A list of dictionaries, each representing a file or folder, or an empty list if an error occurred.
    """
    results = []
    page_token = None
    
    try:
        while True:
            # Define fields to retrieve for each file.
            # 'nextPageToken' is essential for pagination.
            # 'files(id, name, mimeType, parents, modifiedTime)' are common useful fields.
            params = {
                'pageSize': page_size,
                'fields': "nextPageToken, files(id, name, mimeType, parents, modifiedTime)",
                'spaces': 'drive', # Restrict to Drive files (not photos, etc.)
            }
            if query:
                params['q'] = query
            if page_token:
                params['pageToken'] = page_token

            response = service.files().list(**params).execute()
            items = response.get('files', [])
            results.extend(items)
            page_token = response.get('nextPageToken', None)
            
            if not page_token:
                break
        
        if not results:
            print("No files or folders found matching the criteria.")
        else:
            print(f"Found {len(results)} files/folders:")
            for item in results:
                print(f"  Name: {item.get('name')}, ID: {item.get('id')}, Type: {item.get('mimeType')}")
        return results
    except HttpError as error:
        print(f"An HTTP error occurred while listing files: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while listing files: {e}")
        return []

# --- Example Usage ---
if __name__ == '__main__':
    # 1. Get the Google Drive service object
    drive_service = get_google_drive_service()

    if drive_service:
        print("\n--- Performing example operations ---")

        # Create a dummy file for testing uploads/updates
        dummy_file_content = "This is a test document created by the Python script."
        with open("test_upload.txt", "w") as f:
            f.write(dummy_file_content)
        
        updated_dummy_file_content = "This content has been updated by the script."
        with open("test_update.txt", "w") as f:
            f.write(updated_dummy_file_content)

        # Example 1: Create a folder
        # my_app_folder_id = create_folder(drive_service, "MyWebAppFiles")
        my_app_folder_id = "1bdoTuKf91iuOjGWUC-36wuM1Dww0sdxp"
        
        if my_app_folder_id:
            # Example 2: Upload a file to the created folder
            uploaded_file_id = upload_file(
                drive_service,
                "test_upload.txt",
                "MyFirstWebAppDoc.txt",
                "text/plain",
                parent_folder_id=my_app_folder_id
            )

            if uploaded_file_id:
                # Example 3: Update the content of the uploaded file
                update_file_content(
                    drive_service,
                    uploaded_file_id,
                    "test_update.txt",
                    new_name="MyUpdatedWebAppDoc.txt"
                )

                # Example 4: Download the updated file
                download_binary_file(
                    drive_service,
                    uploaded_file_id,
                    "downloaded_updated_doc.txt"
                )
            
            # Example 5: List files within the created folder
            print(f"\nListing files in folder '{my_app_folder_id}':")
            list_files_and_folders(drive_service, query=f"'{my_app_folder_id}' in parents and trashed = false")

        # Example 6: List all text files in My Drive
        # print("\nListing all text files in My Drive:")
        # list_files_and_folders(drive_service, query="mimeType='text/plain'")

        # Example 7: Export a hypothetical Google Docs file (replace with a real ID if you have one)
        # For this to work, you need a Google Docs file ID that your app has access to.
        # google_doc_example_id = "YOUR_GOOGLE_DOC_FILE_ID_HERE"
        # if google_doc_example_id != "YOUR_GOOGLE_DOC_FILE_ID_HERE":
        #     export_google_workspace_doc(
        #         drive_service,
        #         google_doc_example_id,
        #         "application/pdf",
        #         "exported_google_doc.pdf"
        #     )
        # else:
        #     print("\nSkipping Google Docs export example. Provide a real Google Docs ID to test.")

        # Clean up dummy files
        if os.path.exists("test_upload.txt"):
            os.remove("test_upload.txt")
        if os.path.exists("test_update.txt"):
            os.remove("test_update.txt")
        
        print("\n--- Example operations complete ---")
    else:
        print("Failed to initialize Google Drive service. Please check your setup.")

