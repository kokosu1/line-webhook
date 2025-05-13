import os
import requests
import json
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import random

# .envファイルから秘密情報を読み込む
load_dotenv()

# 環境変数からキーを取り出す
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

# city_mappingをJSONファイルから読み込む
def load_city_mapping():
    with open('city_mapping.json', 'r', encoding='utf-8') as f:
        return json.load(f)

city_mapping = load_city_mapping()
user_mode = {}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]

        # postback処理（ボタンが押されたとき）
        if event["type"] == "postback":
            data = event["postback"]["data"]
            if user_mode.get(user_id) == "janken":
                user_choice = data
                choices = ["グー", "チョキ", "パー"]

                while True:
                    bot_choice = random.choice(choices)
                    result = determine_janken_result(user_choice, bot_choice)
                    if result != "引き分け":
                        break

                send_line_reply(reply_token, f"あなたの選択: {user_choice}\nボットの選択: {bot_choice}\n結果: {result}")
                user_mode[user_id] = None
            return {"status": "ok"}

        # 通常のメッセージ処理
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # 「天気」モードに切り替え
            if "天気" in text:
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気を知りたいですか？例: 東京、名古屋、札幌 など")

            elif user_mode.get(user_id) == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "指定された都市の天気情報が見つかりませんでした。別の都市を試してみてください。")
                else:
                    weather_message = get_weather(city)
                    send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None

            elif "おみくじ" in text:
                result = random.choice(["大吉", "中吉", "小吉", "凶", "大凶"])
                send_line_reply(reply_token, f"おみくじの結果は「{result}」です！")

            elif "クイズ" in text:
                user_mode[user_id] = "quiz_answer"
                user_mode[user_id + "_answer"] = "栃木"
                question = "次のうち、実際の都道府県の名前はどれでしょう？\n1. 高砂\n2. 豊橋\n3. 栃木\n4. 福岡"
                send_line_reply(reply_token, question)

            elif user_mode.get(user_id) == "quiz_answer":
                correct = user_mode.get(user_id + "_answer")
                if text.strip() == correct:
                    send_line_reply(reply_token, "正解です！")
                else:
                    send_line_reply(reply_token, "不正解です。もう一度挑戦してね。")
                user_mode[user_id] = None
                user_mode.pop(user_id + "_answer", None)

            elif "じゃんけん" in text:
                user_mode[user_id] = "janken"
                buttons = [
                    {"type": "postback", "label": "✊ グー", "data": "グー"},
                    {"type": "postback", "label": "✌️ チョキ", "data": "チョキ"},
                    {"type": "postback", "label": "🖐️ パー", "data": "パー"}
                ]
                send_line_buttons_reply(reply_token, "じゃんけんをしましょう！グー、チョキ、パーのいずれかを選んでください。", buttons)

            else:
                send_line_reply(reply_token, "「天気」「おみくじ」「クイズ」「じゃんけん」から選んでください！")

    return {"status": "ok"}

# 都市名を検出
def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"

# 天気取得
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])

    if weather == "Clear":
        return f"今日は晴れだよ！{temp}℃くらい。良い一日を！☀️"
    elif weather == "Clouds":
        return f"今日はくもりかな〜。気温は{temp}℃くらいだよ。☁️"
    elif weather in ["Rain", "Drizzle"]:
        return f"今日は雨っぽいよ。{temp}℃くらいだから傘忘れずにね！☔"
    elif weather == "Snow":
        return f"今日は雪が降ってるみたい！寒いから気をつけてね〜 {temp}℃だよ。❄️"
    else:
        return f"{temp}℃の気温だよ。"

# テキストメッセージを送信
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

# ボタンメッセージを送信
def send_line_buttons_reply(reply_token, text, buttons):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "template",
                "altText": "Buttons template",
                "template": {
                    "type": "buttons",
                    "text": text,
                    "actions": buttons
                }
            }
        ]
    }
    requests.post(url, headers=headers, json=payload)

# じゃんけんの勝敗判定
def determine_janken_result(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "引き分け"
    elif (user_choice == "グー" and bot_choice == "チョキ") or \
         (user_choice == "チョキ" and bot_choice == "パー") or \
         (user_choice == "パー" and bot_choice == "グー"):
        return "あなたの勝ち！"
    else:
        return "あなたの負け…"
