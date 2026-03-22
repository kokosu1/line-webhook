import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import calendar

SCOPES = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"

]

# 環境変数からGoogle認証情報を取得

def get_service():
creds_json = os.environ.get(“GOOGLE_CREDENTIALS_JSON”)
creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
service = build(“sheets”, “v4”, credentials=creds)
return service

SPREADSHEET_ID = os.environ.get(“SPREADSHEET_ID”)

def write_shift(name: str, dates: list[int], period: str, year: int, month: int):
“””
name: スタッフ名
dates: 選択した日付のリスト（例：[1, 3, 5, 10]）
period: “first”（前半1-15）or “second”（後半16-末）
year, month: 対象年月
“””
service = get_service()

```
# シート名を「2025年4月前半」などに設定
period_label = "前半" if period == "first" else "後半"
sheet_name = f"{year}年{month}月{period_label}"

# シートが存在するか確認・なければ作成
spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
sheet_names = [s["properties"]["title"] for s in spreadsheet["sheets"]]

if sheet_name not in sheet_names:
    _create_sheet(service, sheet_name, year, month, period)

# 名前の行を探す or 追加する
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"{sheet_name}!A:A"
).execute()

rows = result.get("values", [])
name_row = None
for i, row in enumerate(rows):
    if row and row[0] == name:
        name_row = i + 1  # 1-indexed
        break

if name_row is None:
    # 名前を新しい行に追加
    name_row = len(rows) + 1
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A{name_row}",
        valueInputOption="RAW",
        body={"values": [[name]]}
    ).execute()

# 日付列に○を入力
if period == "first":
    start_day = 1
    end_day = 15
else:
    start_day = 16
    end_day = calendar.monthrange(year, month)[1]

# ヘッダー行の日付を取得
header = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"{sheet_name}!1:1"
).execute().get("values", [[]])[0]

updates = []
for date in dates:
    if date < start_day or date > end_day:
        continue
    col_label = str(date)
    if col_label in header:
        col_index = header.index(col_label) + 1  # 1-indexed
        col_letter = _col_letter(col_index)
        updates.append({
            "range": f"{sheet_name}!{col_letter}{name_row}",
            "values": [["○"]]
        })

if updates:
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "RAW", "data": updates}
    ).execute()

return True
```

def _create_sheet(service, sheet_name, year, month, period):
“”“新しいシートを作成してヘッダーを設定”””
# シート追加
service.spreadsheets().batchUpdate(
spreadsheetId=SPREADSHEET_ID,
body={“requests”: [{“addSheet”: {“properties”: {“title”: sheet_name}}}]}
).execute()

```
if period == "first":
    days = list(range(1, 16))
else:
    last_day = calendar.monthrange(year, month)[1]
    days = list(range(16, last_day + 1))

# ヘッダー行（A1=名前, B1〜=日付）
headers = ["名前"] + [str(d) for d in days]
service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=f"{sheet_name}!A1",
    valueInputOption="RAW",
    body={"values": [headers]}
).execute()
```

def _col_letter(n):
“”“列番号をアルファベットに変換（1→A, 2→B, …）”””
result = “”
while n > 0:
n, r = divmod(n - 1, 26)
result = chr(65 + r) + result
return result