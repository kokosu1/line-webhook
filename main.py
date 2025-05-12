import httpx
from fastapi import FastAPI, Request

app = FastAPI()

# あなたのLINEチャネルアクセストークンをここに貼ってください
CHANNEL_ACCESS_TOKEN = "lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="

# あなたのOpenWeatherMap APIキーをここに貼ってください
OPENWEATHERMAP_API_KEY = "dd9f6e2b4116d6c124be61d261da444e"

# 天気を取得する関数
async def get_weather(city: str) -> str:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
        "lang": "ja"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{city}の天気は{weather}、気温は{temp}°Cです。"
    else:
        return f"{city}の天気情報を取得できませんでした。"

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("Received:", body)

    event = body["events"][0]
    user_message = event["message"]["text"]
    reply_token = event["replyToken"]

    if user_message.startswith("天気"):
        city = user_message[2:].strip()
        if city:
            reply_text = await get_weather(city)
        else:
            reply_text = "「天気 ○○」の形式で送ってください。例:天気 東京"
    else:
        reply_text = "天気を知りたい場合は「天気 東京」のように送ってください。"

    reply_url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": reply_text}]
    }

    async with httpx.AsyncClient() as client:
        await client.post(reply_url, headers=headers, json=payload)

    return {"status": "ok"}

# オプション:GET / アクセス用
@app.get("/")
def root():
    return {"message": "LINE天気Bot動作中"}
