# import os
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from googleapiclient.errors import HttpError
#
# # Constants
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
# SAMPLE_SPREADSHEET_ID = "1AxVYr1-BeCfCXffPfWZv4GX09YhXhF-_8qNsUQh52kQ"
# SAMPLE_RANGE_NAME = "A1:E5"
# CREDENTIALS_FILE = "../data/betmarket_creds.json"
#
#
# # Authentication and Service Building
# def get_credentials(scopes):
#     creds = None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', scopes)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.fetch_token(CREDENTIALS_FILE, scopes)
#             creds = flow.run_local_server(port=0)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     return creds
#
#
# class GoogleSheetsService:
#     def __init__(self, credentials):
#         self.service = build("sheets", "v4", credentials=credentials)
#
#     def append_values(self, spreadsheet_id, range_name, value_input_option, _values):
#         try:
#             body = {'values': _values}
#             result = self.service.spreadsheets().values().append(
#                     spreadsheetId=spreadsheet_id, range=range_name,
#                     valueInputOption=value_input_option, body=body).execute()
#             print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
#             return result
#         except HttpError as error:
#             print(f"An error occurred: {error}")
#             return None
#
#
# class GoogleDriveService:
#     def __init__(self, credentials):
#         self.service = build('drive', 'v3', credentials=credentials)
#
#     def upload_file(self, folder_id, name, file_path):
#         try:
#             file_metadata = {'name': name, 'parents': [folder_id]}
#             media = MediaFileUpload(file_path, resumable=True)
#             file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#             return file
#         except HttpError as error:
#             print(f"An error occurred: {error}")
#             return None
#
#     def create_folder(self, folder_name, parent_folder_id=None):
#         if self.search_folder(folder_name, parent_folder_id):
#             print(f"Folder '{folder_name}' already exists.")
#             return None
#
#         try:
#             file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
#             if parent_folder_id:
#                 file_metadata['parents'] = [parent_folder_id]
#             folder = self.service.files().create(body=file_metadata).execute()
#             return folder
#         except HttpError as error:
#             print(f"An error occurred: {error}")
#             return None
#
#     def search_folder(self, folder_name, parent_folder_id=None):
#         try:
#             query = f"mimeType='application/vnd.google-apps.folder' and trashed = false and name='{folder_name}'"
#             if parent_folder_id:
#                 query += f" and parents='{parent_folder_id}'"
#             else:
#                 query += " and 'root' in parents"
#
#             results = self.service.files().list(q=query, fields="files(id, name)").execute()
#             items = results.get('files', [])
#             if items:
#                 return items[0]
#             return None
#         except HttpError as error:
#             print(f"An error occurred: {error}")
#             return None
#
#
# # Initialize Services
# credentials = get_credentials(SCOPES)
# sheets_service = GoogleSheetsService(credentials)
# drive_service = GoogleDriveService(credentials)
#
#
#
# class GoogleSheetsService:
#
#     def __init__(self, credentials):
#         self.service = ("sheets", "v4", credentials=credentials)
#
#     def append_values(self, spreadsheet_id, range_name, value_input_option, _values):
#         try:
#             body = {'values': _values}
#             result = self.service.spreadsheets().values().append(
#                     spreadsheetId=spreadsheet_id, range=range_name,
#                     valueInputOption=value_input_option, body=body).execute()
#             print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
#             return result
#         except HttpError as error:
#             print(f"An error occurred: {error}")
#             return None
# # Example usage
# sheets_service.append_values(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, "RAW", [["Sample", "Data", "1", "2", "3"]])
# drive_service.create_folder("New Folder")
