import os
import random
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

user_mode = {}

city_mapping = {
    "東京": "Tokyo",
    "大阪": "Osaka",
    "札幌": "Sapporo",
    "名古屋": "Nagoya",
    "福岡": "Fukuoka"
}

omikuji_result = ["大吉", "中吉", "小吉", "吉", "末吉", "凶"]

prefecture_quiz = {
    "北海道": "日本で一番面積が広い都道府県はどこ？",
    "沖縄": "美しい海で有名な南の島の都道府県はどこ？",
    "東京都": "日本の首都がある都道府県は？"
}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            if "おみくじ" in text:
                result = random.choice(omikuji_result)
                send_line_reply(reply_token, f"今日の運勢は…『{result}』！")

            elif "クイズ" in text:
                question = random.choice(list(prefecture_quiz.values()))
                answer = [k for k, v in prefecture_quiz.items() if v == question][0]
                user_mode[user_id] = {"mode": "quiz", "answer": answer}
                send_line_reply(reply_token, f"都道府県クイズ！\n{question}")

            elif user_mode.get(user_id, {}).get("mode") == "quiz":
                if text == user_mode[user_id]["answer"]:
                    send_line_reply(reply_token, "正解！すごいね！")
                else:
                    send_line_reply(reply_token, "残念…もう一度考えてみて！")
                user_mode[user_id] = None

            elif "天気" in text:
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気が知りたい？例: 東京、札幌、大阪")

            elif user_mode.get(user_id) == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "指定された都市の天気情報が見つかりませんでした。")
                else:
                    weather_message = get_weather_with_advice(city)
                    send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None

            else:
                send_line_reply(reply_token, "「おみくじ」「クイズ」「天気」など送ってみてね！")

    return {"status": "ok"}

def detect_city(text):
    for jp, en in city_mapping.items():
        if jp in text:
            return en
    return "Unknown"

def get_weather_with_advice(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])

    if temp >= 25:
        advice = "今日は暑いからTシャツでOK！"
    elif 15 <= temp < 25:
        advice = "今日は過ごしやすいね。長袖がちょうどいいよ。"
    else:
        advice = "今日は寒いよ！コートを着て出かけてね。"

    if weather == "Clear":
        comment = f"晴れだよ！{temp}℃くらい。{advice}☀️"
    elif weather == "Clouds":
        comment = f"くもりかな〜。気温は{temp}℃。{advice}☁️"
    elif weather in ["Rain", "Drizzle"]:
        comment = f"雨が降ってるよ。{temp}℃。傘と{advice}☔"
    elif weather == "Snow":
        comment = f"雪が降ってるよ。{temp}℃！{advice}❄️"
    else:
        comment = f"{temp}℃で天気は{weather}。{advice}"

    return comment

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
