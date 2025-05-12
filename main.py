import requests
from fastapi import FastAPI, Request

app = FastAPI()

API_KEY = 'dd9f6e2b4116d6c124be61d261da444e'  # OpenWeatherMap APIキー

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            message_text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            if "天気" in message_text:  # メッセージに「天気」が含まれている場合
                city = "東京"  # デフォルトの都市を東京に設定
                weather_message = get_weather(city)  # 天気情報を取得
                send_line_reply(reply_token, weather_message)  # LINEにメッセージを送信

    return {"status": "ok"}

# 天気情報を取得する関数
def get_weather(city: str):
    if city == "東京":
        city = "Tokyo"  # 東京を英語表記に変換
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
            return f"{city}の天気は晴れです！\n気温は{temp}℃、とてもいい天気ですね☀️お出かけ日和です！"
        elif "cloud" in weather:
            return f"{city}の天気は曇りです。\n気温は{temp}℃、少し曇りですが、お散歩にちょうど良い感じですね🌥"
        elif "rain" in weather or "小雨" in weather:  # 雨と小雨は同じメッセージを送る
            return f"{city}の天気は雨（または小雨）です🌧️\n気温は{temp}℃、お出かけの際は傘を忘れずに！☂️"
        elif "snow" in weather:
            return f"{city}の天気は雪です！❄️\n気温は{temp}℃、寒いので暖かくしてね💖"
        else:
            return f"{city}の天気は「{weather}」です。\n気温は{temp}℃。今日も元気に頑張りましょうね！"
    else:
        return "天気情報の取得に失敗しました。もう一度お試しくださいね😢"

# LINEに返信メッセージを送信する関数
def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="  # あなたのLINEのアクセストークンをここに挿入
    }
    body = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    print(f"LINE API status: {response.status_code}")
    print(f"LINE API response: {response.text}")
