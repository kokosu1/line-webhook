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
        # 最初に見つかったシートのA列から名前を取得
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        first_sheet = spreadsheet["sheets"][0]["properties"]["title"]
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{first_sheet}!A:A"
        ).execute()
        
        rows = result.get("values", [])
        # 空白・ヘッダー除いて名前だけ取得
        names = []
        for row in rows[1:]:  # 1行目はヘッダーなのでスキップ
            if row and row[0].strip():
                names.append(row[0].strip())
        return names
    except Exception as e:
        print(f"名前取得エラー: {e}")
        return []

def add_name(name: str):
    pass  # スプレッドシートから取得するので不要

def remove_name(name: str):
    pass  # スプレッドシートから取得するので不要
