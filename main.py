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

user_mode = {}     # ユーザーの現在のモード（天気・支出など）
expenses = {}      # 支出記録

# 都市マッピングの読み込み
def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

city_mapping = load_city_mapping()

# LINEへテキストを返信
def send_line_reply(token, message):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

# じゃんけんボタン表示
def send_janken_buttons(token):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "replyToken": token,
        "messages": [{
            "type": "template",
            "altText": "じゃんけん！どれを出す？",
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
        return "天気情報の取得に失敗しました。都市名が正しいか確認してね。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

def format_weather_message(weather, temp):
    messages = {
        "Clear": f"晴れだよ！☀️ 気温は{temp}℃。",
        "Clouds": f"くもりだよ☁️ 気温は{temp}℃。",
        "Rain": f"雨が降ってるよ🌧️ 気温は{temp}℃。",
        "Snow": f"雪が降ってるよ❄️ 気温は{temp}℃。",
        "Thunderstorm": f"雷が鳴ってるよ⚡️ 気温は{temp}℃。",
        "Drizzle": f"小雨が降ってるよ🌦️ 気温は{temp}℃。",
        "Mist": f"霧が出てるよ🌫️ 気温は{temp}℃。"
    }
    return messages.get(weather, f"現在の天気は「{weather}」、気温は{temp}℃くらいだよ。")

# 支出登録
def handle_expense(user_id, text):
    text = text.strip()
    match_add = re.match(r"(.+?)[\s　]+(\d+)(円)?$", text)
    match_del = re.match(r"(.+?)[\s　]+(\d+)(円)?[\s　]*削除$", text)

    if match_add:
        category = match_add.group(1).strip()
        amount = int(match_add.group(2))
        expenses.setdefault(user_id, {})
        expenses[user_id][category] = expenses[user_id].get(category, 0) + amount
        return f"{category}に{amount}円を追加しました。"

    elif match_del:
        category = match_del.group(1).strip()
        amount = int(match_del.group(2))
        if user_id in expenses and category in expenses[user_id]:
            if expenses[user_id][category] >= amount:
                expenses[user_id][category] -= amount
                if expenses[user_id][category] == 0:
                    del expenses[user_id][category]
                return f"{category}から{amount}円を削除しました。"
            else:
                return f"{category}の金額が足りません。"
        else:
            return f"{category}は記録されていません。"

    return "形式が違います。「食費 1000」や「交通費 500 削除」のように入力してね。"

# 支出レポート
def generate_report(user_id):
    if user_id not in expenses or not expenses[user_id]:
        return "今月の支出はありません。"
    report = "今月の支出:\n"
    total = 0
    for cat, amt in expenses[user_id].items():
        report += f"{cat}: {amt}円\n"
        total += amt
    report += f"合計: {total}円"
    return report

# Webhook
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンク検出
            if "paypay.ne.jp" in text:
                send_line_reply(reply_token, "現在この機能は開発中です。完成までお待ちください。")
                return {"status": "ok"}

            # じゃんけん
            if text == "じゃんけん":
                send_janken_buttons(reply_token)
                return {"status": "ok"}

            # 天気
            if text == "天気":
                user_mode[user_id] = "awaiting_city"
                send_line_reply(reply_token, "都市名を送ってね（例：東京・ホーチミン）")
                return {"status": "ok"}

            if user_mode.get(user_id) == "awaiting_city":
                city = text
                city_name = city_mapping.get(city, city)
                weather = get_weather_by_city(city_name)
                send_line_reply(reply_token, weather)
                user_mode[user_id] = None
                return {"status": "ok"}

            # 支出
            if text == "支出":
                user_mode[user_id] = "awaiting_expense"
                send_line_reply(reply_token, "「食費 1000」みたいに入力してね。")
                return {"status": "ok"}

            if user_mode.get(user_id) == "awaiting_expense":
                result = handle_expense(user_id, text)
                send_line_reply(reply_token, result)
                user_mode[user_id] = None
                return {"status": "ok"}

            if text == "レポート":
                result = generate_report(user_id)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

        # Postback（じゃんけん）
        elif event["type"] == "postback":
            hand = event["postback"]["data"]
            bot = random.choice(["グー", "チョキ", "パー"])
            result = judge_janken(hand, bot)
            message = f"あなた: {hand}\nBot: {bot}\n結果: {result}"
            send_line_reply(reply_token, message)
            if result == "あいこ！もう一度！":
                send_janken_buttons(reply_token)

    return {"status": "ok"}
