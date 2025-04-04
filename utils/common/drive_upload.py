import os
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Optional: Store the root folder in your Drive where all CityMind data will go
DRIVE_ROOT_FOLDER_ID = st.secrets["gdrive"]["root_folder_id"]  # This should be your shared folder ID

def get_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gdrive"],
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
    """Uploads file to a per-user subfolder in Google Drive"""
    service = get_drive_service()
    user_folder_id = ensure_drive_folder(service, f"user_{user_id}", DRIVE_ROOT_FOLDER_ID)

    file_metadata = {
        "name": remote_name,
        "parents": [user_folder_id]
    }
    media = MediaFileUpload(local_path, resumable=True)
    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
