import os
import re
import json
import random
import asyncio
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")
PAYPAY_TOKEN = os.getenv("PAYPAY_TOKEN")

app = FastAPI()

user_mode = {}
anonymous_waiting = set()
anonymous_rooms = {}

def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading city_mapping.json: {e}")
        return {}

city_mapping = load_city_mapping()

def send_line_reply(token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    if res.status_code != 200:
        print(f"Reply error: {res.status_code} - {res.text}")

async def send_push_message(user_id, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: requests.post(
        "https://api.line.me/v2/bot/message/push", headers=headers, json=body))

def send_janken_buttons(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": token,
        "messages": [{
            "type": "template",
            "altText": "じゃんけんを選んでね",
            "template": {
                "type": "buttons",
                "text": "じゃんけん！どれを出す？",
                "actions": [
                    {"type": "postback", "label": "グー ✊", "data": "グー"},
                    {"type": "postback", "label": "チョキ ✌️", "data": "チョキ"},
                    {"type": "postback", "label": "パー ✋", "data": "パー"}
                ]
            }
        }]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

def judge_janken(user, bot):
    hands = {"グー": 0, "チョキ": 1, "パー": 2}
    result = (hands[user] - hands[bot]) % 3
    return ["あいこ！もう一度！", "あなたの負け！", "あなたの勝ち！"][result]

def get_weather_by_city(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Weather API error: {res.status_code} - {res.text}")
            return "天気情報の取得に失敗しました。"
        data = res.json()
        weather = data["weather"][0]["main"]
        temp = round(data["main"]["temp"])
        return format_weather_message(weather, temp)
    except Exception as e:
        print(f"Weather fetch exception: {e}")
        return "天気情報の取得に失敗しました。"

def format_weather_message(weather, temp):
    weather_map = {
        "Clear": "晴れ☀️", "Clouds": "くもり🌤️", "Rain": "雨🌧️",
        "Snow": "雪🌨️", "Thunderstorm": "雷⛈️", "Drizzle": "小雨🌦️",
        "Mist": "霧🌫️"
    }
    condition = weather_map.get(weather, weather)
    return f"現在の天気は「{condition}」、気温は{temp}℃だよ！"

def accept_paypay_link(order_id, verification_code):
    url = "https://www.paypay.ne.jp/app/v2/p2p-api/acceptP2PSendMoneyLink"
    headers = {
        "Authorization": PAYPAY_AUTHORIZATION,
        "Content-Type": "application/json",
        "Origin": "https://www.paypay.ne.jp",
        "Referer": "https://www.paypay.ne.jp/app/p2p/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Cookie": f"token={PAYPAY_TOKEN}"
    }
    body = {
        "orderId": order_id,
        "verificationCode": verification_code,
        "deviceType": "WEB"
    }
    try:
        res = requests.post(url, headers=headers, json=body)
        print("PayPay response:", res.status_code, res.text)
        return res.status_code == 200 and res.json().get("resultStatus") == "SUCCESS"
    except Exception as e:
        print("PayPay error:", e)
        return False

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event.get("replyToken")
        user_id = event["source"].get("userId")

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # 匿名チャット終了（チャット中）
            if text.lower() == "終了":
                if user_id in anonymous_rooms:
                    partner_id = anonymous_rooms.pop(user_id)
                    anonymous_rooms.pop(partner_id, None)
                    await send_push_message(user_id, "匿名チャットを終了しました。")
                    await send_push_message(partner_id, "相手がチャットを終了しました。")
                    return {"status": "ok"}
                elif user_id in anonymous_waiting:
                    anonymous_waiting.discard(user_id)
                    send_line_reply(reply_token, "匿名チャットの待機をキャンセルしました。")
                    return {"status": "ok"}

            # 匿名チャット中のメッセージ転送
            if user_id in anonymous_rooms:
                partner_id = anonymous_rooms.get(user_id)
                if partner_id:
                    asyncio.create_task(send_push_message(partner_id, f"匿名相手: {text}"))
                return {"status": "ok"}

            # 匿名チャット開始
            if text == "匿名チャット":
                if user_id in anonymous_waiting:
                    send_line_reply(reply_token, "既にマッチング待機中です。")
                    return {"status": "ok"}
                if anonymous_waiting:
                    partner_id = anonymous_waiting.pop()
                    anonymous_rooms[user_id] = partner_id
                    anonymous_rooms[partner_id] = user_id
                    await send_push_message(user_id, "匿名チャットが開始されました。終了したい場合は「終了」と送信してください。")
                    await send_push_message(partner_id, "匿名チャットが開始されました。終了したい場合は「終了」と送信してください。")
                else:
                    anonymous_waiting.add(user_id)
                    send_line_reply(reply_token, "マッチング相手を探しています。しばらくお待ちください。")
                return {"status": "ok"}

            # PayPayリンク自動受け取り（orderId + verificationCode抽出）
            if "orderId" in text and "verificationCode" in text:
                try:
                    order_id_match = re.search(r'"orderId"\s*:\s*"(\d+)"', text)
                    verification_match = re.search(r'"verificationCode"\s*:\s*"([A-Za-z0-9]+)"', text)
                    if order_id_match and verification_match:
                        order_id = order_id_match.group(1)
                        verification_code = verification_match.group(1)
                        success = accept_paypay_link(order_id, verification_code)
                        send_line_reply(reply_token, "PayPay受け取り成功！" if success else "受け取り失敗しました。")
                        return {"status": "ok"}
                except Exception as e:
                    print("Error extracting PayPay data:", e)

            # じゃんけん
            if text == "じゃんけん":
                send_janken_buttons(reply_token)
                return {"status": "ok"}

            # 天気
            if user_mode.get(user_id) == "awaiting_city":
                city_name = city_mapping.get(text, text)
                weather_msg = get_weather_by_city(city_name)
                send_line_reply(reply_token, weather_msg)
                user_mode[user_id] = None
                return {"status": "ok"}
            if text == "天気":
                user_mode[user_id] = "awaiting_city"
                send_line_reply(reply_token, "都市名を教えてください（例：東京、大阪）")
                return {"status": "ok"}

        # じゃんけんのポストバック処理
        elif event["type"] == "postback":
            hand = event["postback"]["data"]
            if hand in ["グー", "チョキ", "パー"]:
                bot_hand = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(hand, bot_hand)
                send_line_reply(reply_token, f"あなた: {hand}\nBot: {bot_hand}\n結果: {result}")
                return {"status": "ok"}

    return {"status": "ok"}