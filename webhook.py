import json
import httpx
from fastapi import FastAPI, Request

app = FastAPI()

# LINEのアクセストークン（これを自分のチャネルのアクセストークンに変更）
CHANNEL_ACCESS_TOKEN = 'lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU='

# Webhook URLで受け取ったメッセージに対して返信をする
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("Received body:", body)  # ログに受信したデータを出力

    # ユーザーからのメッセージ
    user_message = body['events'][0]['message']['text']
    reply_token = body['events'][0]['replyToken']
    print(f"User message: {user_message}")  # ユーザーからのメッセージを表示

    # 天気のメッセージに返信する
    if user_message == "天気":
        message = "今日は晴れです！"
    else:
        message = "ごめんなさい、そのリクエストには対応できません。"

    # LINEのAPIに返信メッセージを送信
    reply_url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }

    # メッセージを送信
    async with httpx.AsyncClient() as client:
        response = await client.post(reply_url, headers=headers, json=payload)

    # レスポンスのステータスコードを表示（200が正常）
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    return {"status": "ok"}
