import os
import json
import random
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

user_mode = {}  # ユーザーごとのモード管理
expenses = {}   # 支出管理

# 都市マッピングの読み込み
def load_city_mapping():
    try:
        with open("city_mapping.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

city_mapping = load_city_mapping()

# LINEへのテキスト返信
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
        "Clear": f" 晴れだよ！☀️気温は{temp}℃。お出かけ日和だね！",
        "Clouds": f" くもり空🌤️️だよ。気温は{temp}℃。今日も一日頑張ろう！",
        "Rain": f" 雨が降ってるよ🌧️気温は{temp}℃。傘を忘れずにね！",
        "Snow": f" 雪が降ってるよ！🌨️気温は{temp}℃、あったかくしてね。",
        "Thunderstorm": f" 雷が鳴ってるかも！⛈️気温は{temp}℃、気をつけて！",
        "Drizzle": f" 小雨が降ってるよ🌦️気温は{temp}℃。傘が必要かもね！",
        "Mist": f"🌫️ 霧が出てるよ。気温は{temp}℃。運転には注意してね！"
    }
    return messages.get(weather, f"現在の天気は「{weather}」で、気温は{temp}℃くらいだよ。")

# Webhookエンドポイント
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        # メッセージタイプがテキストの場合
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンクの検出
            if "paypay.ne.jp" in text:
                send_line_reply(reply_token, "現在この機能は開発中です。完成までお待ちください。")
                return {"status": "ok"}

            # じゃんけんの場合
            if text == "じゃんけん":
                send_line_reply(reply_token, "じゃんけんを選んでね！")
                return {"status": "ok"}

            # 天気のリクエスト
            if text == "天気":
                user_mode[user_id] = "awaiting_city"  # 天気モードに変更
                send_line_reply(reply_token, "どの都市の天気を知りたいですか？例えば「東京」や「大阪」など、都市名を送ってください。")
                return {"status": "ok"}

            # 都市名が送られたら天気情報を返す
            if user_mode.get(user_id) == "awaiting_city":
                city = text
                city_name = city_mapping.get(city, city)  # マッピングの確認
                weather_message = get_weather_by_city(city_name)
                send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None  # 天気モードを終了
                return {"status": "ok"}

            # 支出の場合
            if text == "支出":
                send_line_reply(reply_token, "「支出 食費 1000円」や「支出 食費 1000円 削除」で記録できます。集計は「レポート」と送ってね。")
                return {"status": "ok"}

            # 支出金額の追加/削除
            if text.startswith("支出"):
                result = handle_expense(user_id, text)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

            # 支出レポート
            if text == "レポート":
                result = generate_report(user_id)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

        # じゃんけんの場合
        elif event["type"] == "postback":
            data = event["postback"]["data"]
            if data in ["グー", "チョキ", "パー"]:
                bot = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(data, bot)
                message = f"あなた: {data}\nBot: {bot}\n結果: {result}"
                send_line_reply(reply_token, message)

    return {"status": "ok"}
