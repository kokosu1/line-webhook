import os
import requests
import json
import random
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

# 都市マッピング読み込み
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

        # ポストバック処理（じゃんけんのボタン）
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

        # テキストメッセージの処理
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            if "天気" in text:
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気を知りたいですか？ 例: 東京、札幌、沖縄 など")

            elif user_mode.get(user_id) == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "指定された都市が見つかりませんでした。他の都市名を試してね！")
                else:
                    message = get_weather(city)
                    send_line_reply(reply_token, message)
                user_mode[user_id] = None

            elif "おみくじ" in text:
                result = random.choice(["大吉", "中吉", "小吉", "末吉", "凶", "大凶"])
                send_line_reply(reply_token, f"おみくじの結果は…「{result}」でした！")

            elif "クイズ" in text:
                user_mode[user_id] = "quiz_answer"
                user_mode[user_id + "_answer"] = "栃木"
                quiz = "次のうち、実際の都道府県はどれ？\n1. 高砂\n2. 豊橋\n3. 栃木\n4. 福岡"
                send_line_reply(reply_token, quiz)

            elif user_mode.get(user_id) == "quiz_answer":
                correct = user_mode.get(user_id + "_answer")
                if text.strip() == correct:
                    send_line_reply(reply_token, "正解だよ！すごい！")
                else:
                    send_line_reply(reply_token, "不正解…また挑戦してみてね！")
                user_mode[user_id] = None
                user_mode.pop(user_id + "_answer", None)

            elif "じゃんけん" in text:
                user_mode[user_id] = "janken"
                buttons = [
                    {"type": "postback", "label": "✊ グー", "data": "グー"},
                    {"type": "postback", "label": "✌️ チョキ", "data": "チョキ"},
                    {"type": "postback", "label": "🖐️ パー", "data": "パー"}
                ]
                send_line_buttons_reply(reply_token, "じゃんけんするよ〜！どれを出す？", buttons)

            else:
                send_line_reply(reply_token, "「天気」「おみくじ」「クイズ」「じゃんけん」って言ってみてね！")

        # 位置情報メッセージの処理
        if event["type"] == "message" and event["message"]["type"] == "location":
            latitude = event["message"]["latitude"]
            longitude = event["message"]["longitude"]
            weather_message = get_weather_from_coordinates(latitude, longitude)
            send_line_reply(reply_token, weather_message)

    return {"status": "ok"}

# 都市名を検出
def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"

# 緯度経度から天気を取得
def get_weather_from_coordinates(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

# 都市名から天気を取得
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

# 天気をかわいい日本語メッセージに変換
def format_weather_message(weather, temp):
    weather_dict = {
        "Clear": f"今日は晴れだよ！気温は{temp}℃くらい。おでかけ日和だね〜☀️",
        "Clouds": f"今日はくもりかな〜。気温は{temp}℃くらいだよ。のんびり過ごそう☁️",
        "Rain": f"今日は雨っぽいよ…{temp}℃くらい。傘持ってってね☔",
        "Drizzle": f"小雨が降ってるみたい！気温は{temp}℃くらい☂️",
        "Snow": f"今日は雪が降ってるみたい！寒いからあったかくしてね❄️ 気温は{temp}℃だよ。",
        "Thunderstorm": f"雷雨の予報だよ⚡ 気温は{temp}℃。おうちでゆっくりがいいかも。",
        "Fog": f"霧が出てるみたい。気温は{temp}℃だよ。車の運転気をつけてね〜",
        "Mist": f"もやがかかってるみたい。気温は{temp}℃だよ〜",
        "Haze": f"かすんでるかも。気温は{temp}℃！体調に気をつけてね。"
    }
    return weather_dict.get(weather, f"今の天気は{weather}で、気温は{temp}℃くらいだよ！")

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

# じゃんけん判定
def determine_janken_result(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "引き分け"
    elif (user_choice == "グー" and bot_choice == "チョキ") or \
         (user_choice == "チョキ" and bot_choice == "パー") or \
         (user_choice == "パー" and bot_choice == "グー"):
        return "あなたの勝ち！"
    else:
        return "あなたの負け…"
