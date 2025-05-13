import os
import requests
import random
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

user_mode = {}  # user_idごとのモード管理

city_mapping = {
    "東京": "Tokyo",
    "大阪": "Osaka",
    "名古屋": "Nagoya",
    "札幌": "Sapporo",
    "府中市": "Fuchu"
}

prefectures = list(city_mapping.keys())

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            mode = user_mode.get(user_id, {}).get("mode")

            if text == "おみくじ":
                user_mode[user_id] = {"mode": "omikuji"}
                result = random.choice(["大吉", "中吉", "小吉", "凶", "大凶"])
                send_line_reply(reply_token, f"おみくじの結果は…「{result}」でした！")

            elif text == "天気":
                user_mode[user_id] = {"mode": "weather"}
                send_line_reply(reply_token, "どこの天気を知りたいですか？例: 東京、大阪、札幌")

            elif text == "都道府県クイズ":
                prefecture = random.choice(prefectures)
                user_mode[user_id] = {"mode": "quiz", "answer": prefecture}
                send_line_reply(reply_token, f"{prefecture}の県庁所在地はどこでしょう？")

            elif mode == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "都市名が見つかりませんでした。他の都市名で試してね！")
                else:
                    weather_message = get_weather(city)
                    send_line_reply(reply_token, weather_message)
                user_mode[user_id] = {"mode": None}

            elif mode == "quiz":
                correct = user_mode[user_id].get("answer")
                if correct and correct in text:
                    send_line_reply(reply_token, "正解！すごい！")
                else:
                    send_line_reply(reply_token, f"うーん、正解は「{correct}」でした！")
                user_mode[user_id] = {"mode": None}

            else:
                send_line_reply(reply_token, "「おみくじ」「天気」「都道府県クイズ」と送ってね！")

    return {"status": "ok"}

def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])

    if weather == "Clear":
        return f"今日は晴れだよ！{temp}℃くらい。良い一日を！☀️"
    elif weather == "Clouds":
        return f"今日はくもりかな〜。気温は{temp}℃くらいだよ。☁️"
    elif weather in ["Rain", "Drizzle"]:
        return f"今日は雨っぽいよ。{temp}℃くらいだから傘忘れずにね！☔"
    elif weather == "Snow":
        return f"今日は雪が降ってるみたい！寒いから気をつけてね〜 {temp}℃だよ。❄️"
    else:
        return f"{temp}℃で天気は{weather}ってなってるよ！"

def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
