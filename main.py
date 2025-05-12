import requests
from fastapi import FastAPI, Request

app = FastAPI()

API_KEY = 'dd9f6e2b4116d6c124be61d261da444e'

# 日本の都道府県名から英名に変換する辞書（例: 東京 => Tokyo, 大阪 => Osaka）
city_mapping = {
    "東京": "Tokyo",
    "大阪": "Osaka",
    "名古屋": "Nagoya",
    "札幌": "Sapporo",
    "福岡": "Fukuoka",
    "京都": "Kyoto",
    "神戸": "Kobe",
    # 追加の都市をここに追加することができます
}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            message_text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            if "天気" in message_text:
                city = extract_city_name(message_text)
                if city:
                    weather_message = get_weather(city)
                else:
                    weather_message = "指定された都市の天気情報が見つかりませんでした。"
                send_line_reply(reply_token, weather_message)

    return {"status": "ok"}

def extract_city_name(message_text: str):
    # ユーザーのメッセージから「の天気」を除去し、都市名を抽出
    for city in city_mapping:
        if city in message_text:
            return city_mapping[city]  # 都市名を英名に変換して返す
    return None

def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        weather = data["weather"][0]["main"]  # 天気の概要 (Rain, Clear, Clouds, Snow など)
        temp = int(data["main"]["temp"])  # 温度を整数に変換

        # 天気の概要に応じたメッセージ
        if weather == "Clear":
            return f"{city}の天気は晴れです！🌞 今日の気温は{temp}度です！"
        elif weather == "Rain" or weather == "Drizzle":
            return f"{city}の天気は雨です☔ 傘を忘れずに！今日の気温は{temp}度です！"
        elif weather == "Clouds":
            return f"{city}の天気は曇りです☁️ 今日の気温は{temp}度です！"
        elif weather == "Snow":
            return f"{city}の天気は雪です❄️ 寒いので暖かくしてね！今日の気温は{temp}度です！"
        else:
            return f"{city}の天気がわかりません🤔 今日の気温は{temp}度です。"
    else:
        return f"{city}の天気情報の取得に失敗しました。"

def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="  # ここにあなたのLINEチャネルのアクセストークンを入力
    }
    body = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    res = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    print(f"LINE API status: {res.status_code}")
    print(f"LINE API response: {res.json()}")
