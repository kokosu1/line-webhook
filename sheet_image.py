import os
import json
import urllib.request
from PIL import Image, ImageDraw, ImageFont
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

def get_font(size=14):
    font_path = "/tmp/NotoSans.otf"
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(
                "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf",
                font_path
            )
        except:
            return ImageFont.load_default()
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def sheet_to_image(sheet_name: str, output_path: str = "/tmp/shift.png"):
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}"
    ).execute()
    rows = result.get("values", [])
    if not rows:
        return None

    cell_w = 80
    cell_h = 30
    cols = max(len(row) for row in rows)
    img_w = cell_w * cols
    img_h = cell_h * len(rows)

    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)
    font = get_font(12)

    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = c * cell_w
            y = r * cell_h
            draw.rectangle([x, y, x + cell_w, y + cell_h], outline="#ccc")
            draw.text((x + 4, y + 8), str(cell), fill="black", font=font)

    img.save(output_path)
    return output_path
