import requests
from fastapi import FastAPI, Request

app = FastAPI()

API_KEY = 'dd9f6e2b4116d6c124be61d261da444e'

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            message_text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            if "天気" in message_text:
                city = "東京"  # 基本的に東京の天気を取得
                weather_message, sticker_package, sticker_id = get_weather(city)
                send_line_reply(reply_token, weather_message, sticker_package, sticker_id)

    return {"status": "ok"}

def get_weather(city: str):
    # 日本語の都市名を対応する英名に変換
    city_map = {
        "東京": "Tokyo",
        "大阪": "Osaka",
        "名古屋": "Nagoya",
        "福岡": "Fukuoka",
        "札幌": "Sapporo",
        "横浜": "Yokohama"
    }

    # 指定された都市を対応する英名に変換
    for jp, en in city_map.items():
        if jp in city:
            city = en
            break

    # OpenWeatherMap APIを使って天気情報を取得
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    res = requests.get(url)

    if res.status_code == 200:
        data = res.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        # 天気に応じたメッセージとスタンプ
        if "晴" in weather or "sun" in weather:
            message = f"{city}は晴れています！気温は{temp:.1f}℃です♪\nお出かけ日和ですね！"
            sticker = ("11537", "52002734")  # 晴れのスタンプ
        elif "曇" in weather or "cloud" in weather:
            message = f"{city}は曇りです。気温は{temp:.1f}℃です。\nちょっと暗いけど元気出してね！"
            sticker = ("11537", "52002740")  # 曇りのスタンプ
        elif "雨" in weather or "rain" in weather:
            message = f"{city}は雨です。気温は{temp:.1f}℃です！\n傘を忘れずにね☂️"
            sticker = ("11537", "52002745")  # 雨のスタンプ
        elif "雪" in weather or "snow" in weather:
            message = f"{city}は雪です。気温は{temp:.1f}℃です！\n寒いので暖かくしてね！"
            sticker = ("11537", "52002750")  # 雪のスタンプ
        else:
            message = f"{city}の天気は「{weather}」、気温は{temp:.1f}℃です。"
            sticker = (None, None)

        return message, sticker[0], sticker[1]
    else:
        return "天気情報が取得できませんでした。少し待ってから再試行してください。", None, None

def send_line_reply(reply_token, message, sticker_package, sticker_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="  # 必ず自分のChannel Access Tokenに置き換えてください
    }
    body = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }

    if sticker_package and sticker_id:
        body["messages"].append({
            "type": "sticker",
            "packageId": sticker_package,
            "stickerId": sticker_id
        })

    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
   
    print(f"LINE API status: {res.status_code}")
    print(f"LINE API response: {res.text}")
    return response
