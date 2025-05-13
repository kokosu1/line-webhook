import os
import re
import json
import random
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

user_mode = {}
expenses = {}

def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

city_mapping = load_city_mapping()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]

        if event["type"] == "message":
            msg = event["message"]
            if msg["type"] == "text":
                text = msg["text"].strip()

                # PayPayリンク
                if "paypay.ne.jp" in text:
                    send_line_reply(reply_token, "製作中です。完成までお待ちください")
                    return {"status": "ok"}

                # じゃんけん開始
                if text == "じゃんけん":
                    send_janken_quick_reply(reply_token)
                    return {"status": "ok"}

                # じゃんけん手が送られたら判定
                if text in ["グー", "チョキ", "パー"]:
                    bot = random.choice(["グー", "チョキ", "パー"])
                    result = judge_janken(text, bot)
                    send_line_reply(reply_token, f"あなた: {text}\nBot: {bot}\n結果: {result}")
                    return {"status": "ok"}

                # 支出モード
                if text == "支出":
                    send_line_reply(reply_token, "支出を記録するには「支出 食費 1000円」や「支出 食費 1000円 削除」と入力してください。\n集計は「レポート」と送ってね。")
                    return {"status": "ok"}

                if text.startswith("支出"):
                    result = handle_expense(user_id, text)
                    send_line_reply(reply_token, result)
                    return {"status": "ok"}

                if text == "レポート":
                    result = generate_report(user_id)
                    send_line_reply(reply_token, result)
                    return {"status": "ok"}

                # 天気
                if text == "天気":
                    user_mode[user_id] = "waiting_city"
                    send_line_reply(reply_token, "どの都市の天気を知りたいですか？例えば「東京」や「大阪」など、都市名を送ってください。")
                    return {"status": "ok"}

                if user_mode.get(user_id) == "waiting_city":
                    city = text
                    if city in city_mapping:
                        lat, lon = city_mapping[city]
                        message = get_weather_from_coordinates(lat, lon)
                        send_line_reply(reply_token, message)
                    else:
                        send_line_reply(reply_token, f"都市「{city}」が見つかりませんでした。")
                    user_mode[user_id] = None
                    return {"status": "ok"}

                # デフォルト
                send_line_reply(reply_token, "「天気」「じゃんけん」「支出」などのコマンドを送ってみてね！")

            elif msg["type"] == "location":
                lat = msg["latitude"]
                lon = msg["longitude"]
                message = get_weather_from_coordinates(lat, lon)
                send_line_reply(reply_token, message)

    return {"status": "ok"}

def judge_janken(user, bot):
    hands = {"グー": 0, "チョキ": 1, "パー": 2}
    result = (hands[user] - hands[bot]) % 3
    if result == 0:
        return "あいこだよ！"
    elif result == 1:
        return "あなたの負け！"
    else:
        return "あなたの勝ち！"

def send_janken_quick_reply(reply_token):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL
