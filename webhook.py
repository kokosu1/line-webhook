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

app = FastAPI()

user_mode = {}  # 例: {"Uxxxxxxxxxx": "awaiting_city"}
chat_pairs = {}  # 例: {"Uxxxx1": "Uxxxx2", "Uxxxx2": "Uxxxx1"}
waiting_user = None

# 都市名マッピングをロード
def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

city_mapping = load_city_mapping()

# LINEにテキスト返信
def send_line_reply(token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

# LINEにPUSH送信（匿名チャット）
def send_line_push(to, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": to,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body)

# じゃんけんUI送信
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

# じゃんけん勝敗判定
def judge_janken(user, bot):
    hands = {"グー": 0, "チョキ": 1, "パー": 2}
    result = (hands[user] - hands[bot]) % 3
    if result == 0:
        return "あいこ！もう一度！"
    elif result == 1:
        return "あなたの負け！"
    else:
        return "あなたの勝ち！"

# 天気取得
def get_weather_by_city(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

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

@app.post("/webhook")
async def webhook(request: Request):
    global waiting_user
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        # メッセージ処理
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンク検出
            if re.search(r"https://pay\.paypay\.ne\.jp/\S+", text):
                send_line_reply(reply_token, "現在この機能は開発中です。完成までお待ちください。")
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

            # 匿名チャット
            if text == "匿名チャット":
                if user_id in chat_pairs:
                    send_line_reply(reply_token, "すでに誰かとチャット中です。「終了」と送るとやめられます。")
                elif waiting_user and waiting_user != user_id:
                    partner = waiting_user
                    chat_pairs[user_id] = partner
                    chat_pairs[partner] = user_id
                    send_line_push(partner, "誰かと匿名チャットが始まりました。")
                    send_line_reply(reply_token, "誰かと匿名チャットが始まりました。")
                    waiting_user = None
                else:
                    waiting_user = user_id
                    send_line_reply(reply_token, "相手を探しています…")
                return {"status": "ok"}

            if text == "終了":
                if user_id in chat_pairs:
                    partner = chat_pairs.pop(user_id)
                    chat_pairs.pop(partner, None)
                    send_line_push(partner, "相手がチャットを終了しました。")
                    send_line_reply(reply_token, "チャットを終了しました。")
                elif waiting_user == user_id:
                    waiting_user = None
                    send_line_reply(reply_token, "待機をキャンセルしました。")
                else:
                    send_line_reply(reply_token, "現在チャットしていません。")
                return {"status": "ok"}

            # 匿名チャット中の会話
            if user_id in chat_pairs:
                partner = chat_pairs[user_id]
                send_line_push(partner, text)
                return {"status": "ok"}

        # じゃんけんのPostback
        elif event["type"] == "postback":
            data = event["postback"]["data"]
            if data in ["グー", "チョキ", "パー"]:
                bot = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(data, bot)
                send_line_reply(reply_token, f"あなた: {data}\nBot: {bot}\n結果: {result}")
                return {"status": "ok"}

    return {"status": "ok"}
