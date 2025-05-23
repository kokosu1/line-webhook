import os
import re
import json
import random
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")  # PayPay API用のAuthorizationヘッダー値
PAYPAY_TOKEN = os.getenv("PAYPAY_TOKEN")  # PayPay API用Cookieのtoken

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
                    {"type": "postback", "label": "グー ✊", "data": "グー"},
                    {"type": "postback", "label": "チョキ ✌️", "data": "チョキ"},
                    {"type": "postback", "label": "パー ✋", "data": "パー"}
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
            print(f"Error fetching weather data: {res.status_code} - {res.text}")
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

def accept_paypay_link(link_key):
    url = "https://www.paypay.ne.jp/app/v2/p2p-api/acceptP2PSendMoneyLink"
    headers = {
        "Authorization": PAYPAY_AUTHORIZATION,
        "Content-Type": "application/json",
        "Origin": "https://www.paypay.ne.jp",
        "Referer": f"https://www.paypay.ne.jp/app/p2p/{link_key}",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Cookie": f"token={PAYPAY_TOKEN}"
    }
    data = {
        "linkKey": link_key
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200 and response.json().get("resultStatus") == "SUCCESS":
            return True
        else:
            print(f"PayPay link accept failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error accepting PayPay link: {e}")
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

            # 匿名チャット待機キャンセル
            if text == "終了" and user_id in anonymous_waiting:
                anonymous_waiting.remove(user_id)
                send_line_reply(reply_token, "匿名チャットの待機をキャンセルしました。")
                return {"status": "ok"}

            # 匿名チャット中のやり取り・終了
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

            # 匿名チャット開始
            if text == "匿名チャット":
                if user_id in anonymous_waiting:
                    send_line_reply(reply_token, "マッチングを待機中です。")
                    return {"status": "ok"}
                if anonymous_waiting:
                    partner_id = anonymous_waiting.pop()
                    anonymous_rooms[user_id] = partner_id
                    anonymous_rooms[partner_id] = user_id
                    send_push_message(user_id, "匿名チャットが開始されました。終了したい場合は「終了」と送信してください。")
                    send_push_message(partner_id, "匿名チャットが開始されました。終了したい場合は「終了」と送信してください。")
                else:
                    anonymous_waiting.add(user_id)
                    send_line_reply(reply_token, "マッチング相手を探しています。しばらくお待ちください。")
                return {"status": "ok"}

            # PayPayリンク検出
            match = re.search(r"https://pay\.paypay\.ne\.jp/\S+", text)
            if match:
                link_key = text.split("/")[-1]
                if accept_paypay_link(link_key):
                    send_line_reply(reply_token, "PayPayリンクを受け取りました！")
                else:
                    send_line_reply(reply_token, "リンクから情報を取得できませんでした。")
                return {"status": "ok"}

            # じゃんけん
            if text == "じゃんけん":
                send_janken_buttons(reply_token)
                return {"status": "ok"}

            # 天気モード
            if user_mode.get(user_id) == "awaiting_city":
                city = text
                city_name = city_mapping.get(city, city)
                weather_message = get_weather_by_city(city_name)
                send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None
                return {"status": "ok"}

            if text == "天気":
                user_mode[user_id] = "awaiting_city"
                send_line_reply(reply_token, "どの都市の天気を知りたいですか？例：「東京」「大阪」など")
                return {"status": "ok"}

        elif event["type"] == "postback":
            data = event["postback"]["data"]
            if data in ["グー", "チョキ", "パー"]:
                bot = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(data, bot)
                send_line_reply(reply_token, f"あなた: {data}\nBot: {bot}\n結果: {result}")
                return {"status": "ok"}

    return {"status": "ok"}