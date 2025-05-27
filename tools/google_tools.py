import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
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
            # https://personaljarvis.streamlit.app
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

def upload_file(service, file_path, file_name, mime_type, parent_folder_id=None, convert_to_google_doc=False):
    """
    Uploads a new file to Google Drive. Optionally converts it to Google Docs format.

    Args:
        service: Google Drive API service object.
        file_path: The local path to the file to upload.
        file_name: The desired name of the file in Google Drive.
        mime_type: The MIME type of the file (e.g., 'text/plain', 'image/jpeg').
        parent_folder_id: (Optional) The ID of the parent folder. If None, uploads to My Drive root.
        convert_to_google_doc: If True, attempts to convert the uploaded file to a Google Docs document.
                               Requires appropriate source file type (e.g., text/plain, application/msword).

    Returns:
        The ID of the uploaded file, or None if an error occurred.
    """
    file_metadata = {'name': file_name}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    # --- THE CRITICAL CHANGE FOR CONVERSION IS HERE ---
    if convert_to_google_doc:
        file_metadata['mimeType'] = 'application/vnd.google-apps.document'
    # --- END CRITICAL CHANGE ---

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        file = service.files().create(
            body=file_metadata, # This body now includes the target MIME type if converting
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

def update_file_content(service, file_id, new_file_path, new_mime_type=None, new_name=None, convert_to_google_doc=False):
    """
    Updates the content and/or metadata of an existing file in Google Drive.
    Optionally converts it to Google Docs format during update.

    Args:
        service: Google Drive API service object.
        file_id: The ID of the file to update.
        new_file_path: The local path to the new content for the file.
        new_mime_type: (Optional) The new MIME type of the file.
                       This should be the source MIME type of the content being uploaded.
        new_name: (Optional) The new name for the file.
        convert_to_google_doc: If True, attempts to convert the updated file to a Google Docs document.
                               Requires appropriate source file type. This implies the target file
                               will become a Google Doc if it wasn't already.

    Returns:
        The ID of the updated file, or None if an error occurred.
    """
    file_metadata = {}
    if new_name:
        file_metadata['name'] = new_name
    
    # --- THE CRITICAL CHANGE FOR CONVERSION IS HERE (for updates) ---
    # When converting an existing file type to a Google Doc during an update,
    # you explicitly set the target MIME type in the body.
    if convert_to_google_doc:
        file_metadata['mimeType'] = 'application/vnd.google-apps.document'
    # --- END CRITICAL CHANGE ---

    media = MediaFileUpload(new_file_path, mimetype=new_mime_type, resumable=True)
    
    try:
        updated_file = service.files().update(
            fileId=file_id,
            body=file_metadata, # This body now includes the target MIME type if converting
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

def create_google_doc(service, doc_name, parent_folder_id=None):
    """
    Creates a new EMPTY Google Docs document in Google Drive.
    To add content, use upload_file with convert_to_google_doc=True
    or update_file_content with convert_to_google_doc=True.

    Args:
        service: Google Drive API service object.
        doc_name: The desired name of the Google Docs document.
        parent_folder_id: (Optional) The ID of the parent folder. If None, creates in My Drive root.

    Returns:
        The ID of the created Google Docs document, or None if an error occurred.
    """
    file_metadata = {
        'name': doc_name,
        'mimeType': 'application/vnd.google-apps.document'  # MIME type for Google Docs
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    try:
        doc = service.files().create(body=file_metadata, fields='id, name, mimeType').execute()
        print(f"Google Docs document '{doc.get('name')}' created with ID: {doc.get('id')} (MIME: {doc.get('mimeType')})")
        return doc.get('id')
    except HttpError as error:
        print(f"An HTTP error occurred while creating Google Docs document: {error}")
        print(f"Error details: {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while creating Google Docs document: {e}")
        return None

# --- Example Usage ---
if __name__ == '__main__':
    # 1. Get the Google Drive service object
    drive_service = get_google_drive_service()

    if drive_service:
        print("\n--- Performing example operations ---")

        # Create dummy files for testing uploads/updates
        # Content for a new document
        doc_initial_content = "This is the initial content for the Google Doc.\n\n" \
                              "It demonstrates how to create a Google Doc from a plain text file."
        with open("doc_initial.txt", "w") as f:
            f.write(doc_initial_content)
        
        # Content for updating an existing document
        doc_updated_content = "This content has been UPDATED for the Google Doc.\n\n" \
                              "This shows that you can revise Google Docs by uploading new content."
        with open("doc_updated.txt", "w") as f:
            f.write(doc_updated_content)

        # Content for a regular text file upload
        regular_text_content = "This is a regular text file, not a Google Doc."
        with open("regular_text_file.txt", "w") as f:
            f.write(regular_text_content)


        # Example 1: Create a folder
        # my_app_folder_id = create_folder(drive_service, "MyWebAppDocs")   
        my_app_folder_id = "1bdoTuKf91iuOjGWUC-36wuM1Dww0sdxp"
        
        if my_app_folder_id:
            # --- NEW EXAMPLE: Upload a plain text file and convert it to a Google Doc ---
            print("\n--- Creating Google Doc from local text file ---")
            converted_doc_id = upload_file(
                drive_service,
                r"outputs\writing\manuals\The_Journey_Newsletter_Manual.md",
                "Converted Google Doc from Text",
                "text/markdown", # Source MIME type
                parent_folder_id=my_app_folder_id,
                convert_to_google_doc=True
            )

            if converted_doc_id:
                print(f"Created Google Doc from text with ID: {converted_doc_id}")

                # --- NEW EXAMPLE: Update the content of the CONVERTED Google Doc ---
                # print("\n--- Updating content of the converted Google Doc ---")
                # updated_converted_doc_id = update_file_content(
                #     drive_service,
                #     converted_doc_id,
                #     "doc_updated.txt",
                #     new_mime_type="text/plain", # Source MIME type of the content being uploaded for update
                #     new_name="Updated Converted Google Doc",
                #     # No need for convert_to_google_doc=True here if it's already a Google Doc
                # )
                # if updated_converted_doc_id:
                #     print(f"Updated Google Doc with ID: {updated_converted_doc_id}")
            
            # --- Original Example: Upload a regular file (not converted) ---
            # print("\n--- Uploading a regular text file ---")
            # uploaded_file_id = upload_file(
            #     drive_service,
            #     "regular_text_file.txt",
            #     "MyRegularWebAppDoc.txt",
            #     "text/plain",
            #     parent_folder_id=my_app_folder_id
            # )

            # if uploaded_file_id:
            #     print(f"Uploaded regular text file with ID: {uploaded_file_id}")
            
            # --- Original Example: List files within the created folder ---
            print(f"\nListing files in folder '{my_app_folder_id}':")
            list_files_and_folders(drive_service, query=f"'{my_app_folder_id}' in parents and trashed = false")

            # --- Original Example: Create an empty Google Docs document (still valid for empty docs) ---
            # print("\n--- Creating an empty Google Docs document ---")
            # empty_doc_id = create_google_doc(drive_service, "My Empty Google Doc", parent_folder_id=my_app_folder_id)
            # if empty_doc_id:
            #     print(f"Created empty Google Doc with ID: {empty_doc_id}")
            
        # Example: Export a hypothetical Google Docs file (replace with a real ID if you have one)
        # For this to work, you need a Google Docs file ID that your app has access to.
        # This can be the `converted_doc_id` from the new example above!
        # if converted_doc_id: # Use the ID from the newly created doc
        #     export_google_workspace_doc(
        #         drive_service,
        #         converted_doc_id,
        #         "application/pdf",
        #         "exported_converted_doc.pdf"
        #     )
        # else:
        #     print("\nSkipping Google Docs export example. Create a Google Doc first.")

        # Clean up dummy files
        if os.path.exists("doc_initial.txt"):
            os.remove("doc_initial.txt")
        if os.path.exists("doc_updated.txt"):
            os.remove("doc_updated.txt")
        if os.path.exists("regular_text_file.txt"):
            os.remove("regular_text_file.txt")
        if os.path.exists("test_markdown_converted.html"):
            os.remove("test_markdown_converted.html")
        
        print("\n--- Example operations complete ---")
    else:
        print("Failed to initialize Google Drive service. Please check your setup.")

