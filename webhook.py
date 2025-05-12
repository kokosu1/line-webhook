from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

CHANNEL_ACCESS_TOKEN = "lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("Webhook received!")
    print(body)

    events = body.get("events", [])
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]
            user_id = event["source"]["userId"]

            if "天気" in user_message:
                # 天気予報取得（例として東京）
                async with httpx.AsyncClient() as client:
                    res = await client.get("https://weather.tsukumijima.net/api/forecast/city/130010")  # 東京の天気
                    weather_data = res.json()
                    forecast = weather_data["forecasts"][0]
                    message = f"{forecast['dateLabel']}の{forecast['telop']}です。"
            else:
                message = f"「{user_message}」って言ったね！"

            # LINEに返信
            reply_url = "https://api.line.me/v2/bot/message/reply"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
            }
            payload = {
                "replyToken"6aa790db01534e50a3d7d1d95a88f758
                "messages": [{"type": "text", "text": message}]
            }
            await client.post(reply_url, headers=headers, json=payload)

    return {"status": "ok"}
