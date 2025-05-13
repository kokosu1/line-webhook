import os
import re
import requests
import json
import random
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

user_mode = {}
expenses = {}

# 都市マッピング読み込み
def load_city_mapping():
    try:
        with open('city_mapping.json', 'r', encoding='utf-8') as f:
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

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンク検出
            if "paypay.ne.jp" in text:
                send_line_reply(reply_token, "製作中です。完成までお待ちください")
                return {"status": "ok"}

            # じゃんけんの開始
            if text == "じゃんけん":
                send_janken_buttons(reply_token)
                return {"status": "ok"}

            # 支出関連
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

            # その他
            send_line_reply(reply_token, "「支出」や「じゃんけん」などのコマンドを送ってみてね！")

        elif event["type"] == "message" and event["message"]["type"] == "location":
            lat = event["message"]["latitude"]
            lon = event["message"]["longitude"]
            message = get_weather_from_coordinates(lat, lon)
            send_line_reply(reply_token, message)

        elif event["type"] == "postback":
            data = event["postback"]["data"]
            if data in ["グー", "チョキ", "パー"]:
                bot_hand = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(data, bot_hand)
                send_line_reply(reply_token, f"あなた: {data}\nBot: {bot_hand}\n結果: {result}")
                return {"status": "ok"}

    return {"status": "ok"}

def send_janken_buttons(reply_token):
    buttons = {
        "type": "template",
        "altText": "じゃんけんを選んでください。",
        "template": {
            "type": "buttons",
            "text": "じゃんけんを選んでください。",
            "actions": [
                {
                    "type": "postback",
                    "label": "グー",
                    "data": "グー"
                },
                {
                    "type": "postback",
                    "label": "チョキ",
                    "data": "チョキ"
                },
                {
                    "type": "postback",
                    "label": "パー",
                    "data": "パー"
                }
            ]
        }
    }
    payload = {
        "replyToken": reply_token,
        "messages": [buttons]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)

def judge_janken(user, bot):
    hands = {"グー": 0, "チョキ": 1, "パー": 2}
    if user not in hands:
        return "「グー」「チョキ」「パー」で入力してね。"
    result = (hands[user] - hands[bot]) % 3
    if result == 0:
        return "あいこだよ！"
    elif result == 1:
        return "あなたの負け！"
    else:
        return "あなたの勝ち！"

def handle_expense(user_id, text):
    match_add = re.match(r"支出 (\S+) (\d+)円$", text)
    match_del = re.match(r"支出 (\S+) (\d+)円 削除$", text)

    if match_add:
        category = match_add.group(1)
        amount = int(match_add.group(2))
        expenses.setdefault(user_id, {})
        expenses[user_id][category] = expenses[user_id].get(category, 0) + amount
        return f"{category}に{amount}円を追加しました。"

    elif match_del:
        category = match_del.group(1)
        amount = int(match_del.group(2))
        if user_id in expenses and category in expenses[user_id]:
            if expenses[user_id][category] >= amount:
                expenses[user_id][category] -= amount
                if expenses[user_id][category] == 0:
                    del expenses[user_id][category]
                return f"{category}から{amount}円を削除しました。"
            else:
                return f"{category}の金額が足りません。削除できません。"
        else:
            return f"{category}は記録されていません。"
    return "入力フォーマットが違います。例: 支出 食費 1000円 または 支出 食費 1000円 削除"

def generate_report(user_id):
    if user_id not in expenses or not expenses[user_id]:
        return "今月の支出はありません。"
    report = "今月の支出:\n"
    total = 0
    for category, amount in expenses[user_id].items():
        report += f"{category}: {amount}円\n"
        total += amount
    report += f"合計: {total}円"
    return report

def get_weather_from_coordinates(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

def get_weather(city):
    city_english = city_mapping.get(city, city)  # city_mapping を使用して都市名を英語に変換
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_english}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

def format_weather_message(weather, temp):
    messages = {
        "Clear": f"今日は晴れ！気温は{temp}℃くらい。お出かけ日和だね！",
        "Clouds": f"今日はくもり。気温は{temp}℃くらい。",
        "Rain": f"今日は雨。気温は{temp}℃くらい。傘を忘れずに！",
        "Snow": f"雪が降ってるよ！気温は{temp}℃、暖かくしてね。",
    }
    return messages.get(weather, f"今の天気は{weather}、気温は{temp}℃くらいだよ。")

def send_line_reply(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=payload)
