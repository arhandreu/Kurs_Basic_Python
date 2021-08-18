from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload,MediaInMemoryUpload
import requests

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def create_uploader(token='token.json'):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def find_folder_id(uploader, folder_name):
    results = uploader.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name, mimeType, parents, createdTime)",
        q=f"name = '{folder_name}'").execute()
    return results['files'][0]['id']


def create_folder(uploader, file_name):
    #folder_id = '1uuecd6ndiZlj3d9dSVeZeKyEmEkC7qyr'
    file_metadata = {
        'name': file_name,
        'mimeType': 'application/vnd.google-apps.folder',
        #'parents': [folder_id]
    }
    return uploader.files().create(body=file_metadata, fields='id').execute()['id']


def upload(uploader, folder_id, file_path, file_name):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    # media = MediaFileUpload(file_path, resumable=True)
    media = MediaInMemoryUpload(requests.get(file_path).content)
    uploader.files().create(body=file_metadata, media_body=media, fields='id').execute()


if __name__ == '__main__':
    uploader = create_uploader()
    print(create_folder(uploader, 'Я папка'))
