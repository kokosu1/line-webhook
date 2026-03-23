import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_service():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    return service

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def get_names():
    try:
        service = get_service()
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        
        # 全シートからA列の名前を収集
        names = []
        for sheet in spreadsheet["sheets"]:
            sheet_title = sheet["properties"]["title"]
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{sheet_title}!A2:A"
            ).execute()
            rows = result.get("values", [])
            for row in rows:
                if row and row[0].strip() and row[0].strip() not in names:
                    names.append(row[0].strip())
        return names
    except Exception as e:
        print(f"名前取得エラー: {e}")
        return []

def add_name(name: str):
    pass  # スプレッドシートから取得するので不要

def remove_name(name: str):
    pass  # スプレッドシートから取得するので不要
