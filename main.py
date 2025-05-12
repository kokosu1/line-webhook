import requests
from fastapi import FastAPI, Request

app = FastAPI()

API_KEY = 'dd9f6e2b4116d6c124be61d261da444e'

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("=== Webhook Body ===")
    print(body)
    
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            message_text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            if "天気" in message_text:
                city = "東京"  # ここで市を指定している。後で日本語にも対応
                weather_message = get_weather(city)
                send_line_reply(reply_token, weather_message)

    return {"status": "ok"}

def get_weather(city: str):
    if city == "東京":
        city = "Tokyo"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    print(f"Weather API status: {res.status_code}")
    print(f"Weather API response: {res.text}")
    if res.status_code == 200:
        data = res.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        # 天気によってメッセージを変える
        if "clear" in weather:
            return f"{city}の天気は晴れです！気温は{temp}℃です。今日も元気に過ごしてね！"
        elif "cloud" in weather:
            return f"{city}の天気は曇りです。気温は{temp}℃。お天気はちょっと曇りですが、頑張りましょう！"
        elif "rain" in weather:
            return f"{city}の天気は雨です。気温は{temp}℃。お出かけの際は傘を忘れずに！"
        elif "snow" in weather:
            return f"{city}の天気は雪です！気温は{temp}℃。寒いので暖かくしてね。"
        else:
            return f"{city}の天気は「{weather}」、気温は{temp}℃です。"
    else:
        return "天気情報の取得に失敗しました。"

def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="  # 自分のアクセストークンをここに入れる
    }
    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    res = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    print(f"LINE API status: {res.status_code}")
    print(f"LINE API response: {res.text}")
