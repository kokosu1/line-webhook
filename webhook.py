# Save the full code into a single file for user download
code = '''
import os
import re
import json
import random
import uuid
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
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
        print(f"Error sending reply: {res.status_code} - {res.text}")

def send_push_message(user_id, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body)
    if res.status_code != 200:
        print(f"Error sending push message: {res.status_code} - {res.text}")

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
                    {"type": "message", "label": "グー ✊", "text": "グー"},
                    {"type": "message", "label": "チョキ ✌️", "text": "チョキ"},
                    {"type": "message", "label": "パー ✋", "text": "パー"}
                ]
            }
        }]
    }
    res = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    if res.status_code != 200:
        print(f"Error sending janken buttons: {res.status_code} - {res.text}")

def judge_janken(user, bot):
    hands = {"グー": 0, "チョキ": 1, "パー": 2}
    result = (hands[user] - hands[bot]) % 3
    if result == 0:
        return "あいこ！もう一度！"
    elif result == 1:
        return "あなたの負け！"
    else:
        return "あなたの勝ち！"

def get_weather_by_city(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return "天気情報の取得に失敗しました。"
        data = res.json()
        weather = data["weather"][0]["main"]
        temp = round(data["main"]["temp"])
        return format_weather_message(weather, temp)
    except Exception as e:
        print(f"Error getting weather: {e}")
        return "天気情報の取得に失敗しました。"

def format_weather_message(weather, temp):
    messages = {
        "Clear": f"晴れだよ！☀️気温は{temp}℃。お出かけ日和だね！",
        "Clouds": f"くもり空🌤️気温は{temp}℃。今日も一日頑張ろう！",
        "Rain": f"雨が降ってるよ🌧️気温は{temp}℃。傘を忘れずにね！",
        "Snow": f"雪が降ってるよ！🌨️気温は{temp}℃、あったかくしてね。",
        "Thunderstorm": f"雷が鳴ってるかも！⛈️気温は{temp}℃、気をつけて！",
        "Drizzle": f"小雨が降ってるよ🌦️気温は{temp}℃。傘が必要かもね！",
        "Mist": f"🌫️霧が出てるよ。気温は{temp}℃。運転には注意してね！"
    }
    return messages.get(weather, f"現在の天気は「{weather}」、気温は{temp}℃くらいだよ。")

def get_paypay_link_details(link_key):
    url = f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PSendMoneyLink/{link_key}"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.paypay.ne.jp",
        "Referer": f"https://www.paypay.ne.jp/app/p2p/{link_key}",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"token={PAYPAY_TOKEN}"
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            order_id = data.get("data", {}).get("orderId")
            verification_code = data.get("data", {}).get("verificationCode")
            return order_id, verification_code
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def accept_paypay_link(link_key):
    order_id, verification_code = get_paypay_link_details(link_key)
    if not order_id or not verification_code:
        return False
    url = "https://www.paypay.ne.jp/app/v2/p2p-api/acceptP2PSendMoneyLink"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.paypay.ne.jp",
        "Referer": f"https://www.paypay.ne.jp/app/p2p/{link_key}",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"token={PAYPAY_TOKEN}"
    }
    data = {
        "orderId": order_id,
        "verificationCode": verification_code,
        "requestId": str(uuid.uuid4()),
        "senderMessageId": str(uuid.uuid4()),
        "senderChannelUrl": str(uuid.uuid4()),
        "client_uuid": str(uuid.uuid4())
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        return res.status_code == 200 and res.json().get("header", {}).get("resultCode") == "S0000"
    except Exception as e:
        print(f"Exception: {e}")
        return False

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event.get("replyToken")
        user_id = event.get("source", {}).get("userId")

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            if text == "終了" and user_id in anonymous_waiting:
                anonymous_waiting.remove(user_id)
                send_line_reply(reply_token, "匿名チャットの待機をキャンセルしました。")
                return {"status": "ok"}
            if user_id in anonymous_rooms:
                partner_id = anonymous_rooms[user_id]
                if text == "終了":
                    send_push_message(user_id, "匿名チャットを終了しました。")
                    send_push_message(partner_id, "相手がチャットを終了しました。")
                    anonymous_rooms.pop(user_id, None)
                    anonymous_rooms.pop(partner_id, None)
                else:
                    send_push_message(partner_id, f"匿名相手: {text}")
                return {"status": "ok"}
            if text == "匿名チャット":
                if user_id in anonymous_waiting:
                    send_line_reply(reply_token, "すでに待機中です。")
                elif anonymous_waiting:
                    partner = anonymous_waiting.pop()
                    anonymous_rooms[user_id] = partner
                    anonymous_rooms[partner] = user_id
                    send_line_reply(reply_token, "匿名チャットが開始されました。")
                    send_push_message(partner, "匿名チャットが開始されました。")
                else:
                    anonymous_waiting.add(user_id)
                    send_line_reply(reply_token, "匿名チャットの相手を待っています。終了したいときは「終了」と送ってください。")
                return {"status": "ok"}

            if text == "じゃんけん":
                user_mode[user_id] = "janken"
                send_janken_buttons(reply_token)
                return {"status": "ok"}
            if user_mode.get(user_id) == "janken":
                if text in ["グー", "チョキ", "パー"]:
                    bot_hand = random.choice(["グー", "チョキ", "パー"])
                    result = judge_janken(text, bot_hand)
                    send_line_reply(reply_token, f"あなた: {text}\nBot: {bot_hand}\n{result}")
                    if not result.startswith("あいこ"):
                        user_mode.pop(user_id)
                else:
                    send_line_reply(reply_token, "「グー」「チョキ」「パー」から選んでね！")
                return {"status": "ok"}

            if text == "天気":
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "都市名を送ってください（例：東京）")
                return {"status": "ok"}
            if user_mode.get(user_id) == "weather":
                city = text
                if city in city_mapping:
                    msg = get_weather_by_city(city)
                    send_line_reply(reply_token, msg)
                    user_mode.pop(user_id)
                else:
                    send_line_reply(reply_token, f"{city} は対応していません。")
                return {"status": "ok"}

            match = re.search(r"https://pay\\.paypay\\.ne\\.jp/([A-Za-z0-9]+)", text)
            if match:
                link_key = match.group(1)
                if accept_paypay_link(link_key):
                    send_line_reply(reply_token, "PayPay送金リンクの受け取りが完了しました。")
                else:
                    send_line_reply(reply_token, "PayPay送金リンクの受け取りに失敗しました。\n有効なリンクか、すでに受け取っていないか確認してください。")
                return {"status": "ok"}

            send_line_reply(reply_token, f"すみません、「{text}」には対応していません。")

    return {"status": "ok"}
'''

path = "/mnt/data/main.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

path