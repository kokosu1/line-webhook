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

user_mode = {}
expenses = {}

# 都市マッピングの読み込み
def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

city_mapping = load_city_mapping()

# LINEへの返信送信
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

# じゃんけんボタン送信
def send_janken_buttons(token):
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

# じゃんけん勝敗
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
        "Clear": f"☀️ 晴れだよ！気温は{temp}℃。お出かけ日和だね！",
        "Clouds": f"☁️ くもり空だよ。気温は{temp}℃。今日も一日頑張ろう！",
        "Rain": f"🌧️ 雨が降ってるよ。気温は{temp}℃。傘を忘れずにね！",
        "Snow": f"❄️ 雪が降ってるよ！気温は{temp}℃、あったかくしてね。",
        "Thunderstorm": f"⛈️ 雷が鳴ってるかも！気温は{temp}℃、気をつけて！",
        "Drizzle": f"🌦️ 小雨が降ってるよ。気温は{temp}℃。傘が必要かもね！",
        "Mist": f"🌫️ 霧が出てるよ。気温は{temp}℃。運転には注意してね！"
    }
    return messages.get(weather, f"現在の天気は「{weather}」で、気温は{temp}℃くらいだよ。")

# 支出記録
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
    return "形式が違います。例: 支出 食費 1000円 または 支出 食費 1000円 削除"

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

# Webhookエンドポイント
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        # テキストメッセージ
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンク検出
            if "https://pay.paypay.ne.jp/" in text:
                send_line_reply(reply_token, "\n現在この機能は開発中です。完成までお待ちください。")
                return {"status": "ok"}

            # じゃんけん開始
            if text == "じゃんけん":
                send_janken_buttons(reply_token)
                return {"status": "ok"}

            # 天気モード開始
            if text == "天気":
                user_mode[user_id] = "awaiting_city"
                send_line_reply(reply_token, "どの都市の天気を知りたいですか？例えば「東京」や「大阪」など、都市名を送ってください。")
                return {"status": "ok"}

            # 天気モード中
            if user_mode.get(user_id) == "awaiting_city":
                city = text
                city_name = city_mapping.get(city, city)
                weather_message = get_weather_by_city(city_name)
                send_line_reply(reply_token, weather_message)
                return {"status": "ok"}

            # 支出機能
            if text == "支出":
                send_line_reply(reply_token, "「支出 食費 1000円」や「支出 食費 1000円 削除」で記録できます。集計は「レポート」と送ってね。")
                return {"status": "ok"}

            if text.startswith("支出"):
                result = handle_expense(user_id, text)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

            if text == "レポート":
                result = generate_report(user_id)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

        # Postback（じゃんけん）
        elif event["type"] == "postback":
            data = event["postback"]["data"]
            if data in ["グー", "チョキ", "パー"]:
                bot = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(data, bot)
                message = f"あなた: {data}\nBot: {bot}\n結果: {result}"
                send_line_reply(reply_token, message)

    return {"status": "ok"}
