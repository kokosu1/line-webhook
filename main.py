import os
import re
import json
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

user_mode = {}

# 都市マッピングの読み込み
def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

city_mapping = load_city_mapping()

# LINEへのテキスト返信
def send_line_reply(token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

# 天気取得
def get_weather_by_city(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

def format_weather_message(weather, temp):
    messages = {
        "Clear": f"晴れだよ！☀️気温は{temp}℃。お出かけ日和だね！",
        "Clouds": f"くもり空🌤️だよ。気温は{temp}℃。今日も一日頑張ろう！",
        "Rain": f"雨が降ってるよ🌧️気温は{temp}℃。傘を忘れずにね！",
        "Snow": f"雪が降ってるよ！🌨️気温は{temp}℃、あったかくしてね。",
        "Thunderstorm": f"雷が鳴ってるかも！⛈️気温は{temp}℃、気をつけて！",
        "Drizzle": f"小雨が降ってるよ🌦️気温は{temp}℃。傘が必要かもね！",
        "Mist": f"🌫️ 霧が出てるよ。気温は{temp}℃。運転には注意してね！"
    }
    return messages.get(weather, f"現在の天気は「{weather}」で、気温は{temp}℃くらいだよ。")

# Webhookエンドポイント
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        # テキストメッセージ
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            if "paypay.ne.jp" in text:
                send_line_reply(reply_token, "現在この機能は開発中です。完成までお待ちください。")
                return {"status": "ok"}

            if text == "天気":
                user_mode[user_id] = "awaiting_city"
                send_line_reply(reply_token, "どこの都市の天気を知りたいですか？例: 「東京」や「大阪」など、都市名を送ってください。")
                return {"status": "ok"}

            if user_mode.get(user_id) == "awaiting_city":
                city = text
                city_name = city_mapping.get(city, city)
                weather_message = get_weather_by_city(city_name)
                send_line_reply(reply_token, f"{city}の天気予報: {weather_message}")
                user_mode[user_id] = None
                return {"status": "ok"}

    return {"status": "ok"}
