import os
import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Optional: Store the root folder in your Drive where all CityMind data will go
DRIVE_ROOT_FOLDER_ID = st.secrets["gdrive"]["root_folder_id"]  # This should be your shared folder ID

def get_drive_service():
    # Reconstruct multiline private_key
    service_info = dict(st.secrets["gdrive"])
    service_info["private_key"] = service_info["private_key"].replace("\\n", "\n")

    # Create credentials object
    creds = service_account.Credentials.from_service_account_info(
        service_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

def ensure_drive_folder(service, folder_name, parent_id):
    """Create a folder if it doesn't exist under the parent_id. Returns the folder ID."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder['id']

def upload_file(local_path, remote_name, user_id):
    try:
        service = get_drive_service()

        print(f"[DRIVE UPLOAD] Getting or creating user folder for: user_{user_id}")
        user_folder_id = ensure_drive_folder(service, f"user_{user_id}", DRIVE_ROOT_FOLDER_ID)
        print(f"[DRIVE UPLOAD] Using folder ID: {user_folder_id}")

        file_metadata = {
            "name": remote_name,
            "parents": [user_folder_id]
        }

        media = MediaFileUpload(local_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        print(f"✅ [DRIVE UPLOAD] File uploaded: {remote_name} (ID: {file['id']})")

    except Exception as e:
        print(f"❌ [DRIVE UPLOAD] FAILED to upload {remote_name}: {e}")

