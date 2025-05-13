import os
import requests
import json
import random
import re
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

# 環境変数の読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")

app = FastAPI()
user_mode = {}

# 都市マッピング読み込み
def load_city_mapping():
    with open('city_mapping.json', 'r', encoding='utf-8') as f:
        return json.load(f)

city_mapping = load_city_mapping()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]

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

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンクの自動検出
            paypay_link = detect_paypay_link(text)
            if paypay_link:
                result = auto_receive_paypay(paypay_link)
                send_line_reply(reply_token, result)

            elif "天気" in text:
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

            elif "じゃんけん" in text:
                user_mode[user_id] = "janken"
                buttons = [
                    {"type": "postback", "label": "✊ グー", "data": "グー"},
                    {"type": "postback", "label": "✌️ チョキ", "data": "チョキ"},
                    {"type": "postback", "label": "🖐️ パー", "data": "パー"}
                ]
                send_line_buttons_reply(reply_token, "じゃんけんするよ〜！どれを出す？", buttons)

            else:
                send_line_reply(reply_token, "「天気」「じゃんけん」「PayPay」って言ってみてね！")

        elif event["type"] == "message" and event["message"]["type"] == "location":
            latitude = event["message"]["latitude"]
            longitude = event["message"]["longitude"]
            weather_message = get_weather_from_coordinates(latitude, longitude)
            send_line_reply(reply_token, weather_message)

    return {"status": "ok"}

# PayPayリンク自動検出
def detect_paypay_link(text):
    paypay_link_pattern = r'https://paypay.ne.jp/.*'
    match = re.search(paypay_link_pattern, text)
    if match:
        return match.group(0)
    return None

# 天気情報の取得
def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

def get_weather_from_coordinates(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

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

# じゃんけん結果判定
def determine_janken_result(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "引き分け"
    elif (user_choice == "グー" and bot_choice == "チョキ") or \
         (user_choice == "チョキ" and bot_choice == "パー") or \
         (user_choice == "パー" and bot_choice == "グー"):
        return "あなたの勝ち！"
    else:
        return "あなたの負け…"

# PayPay自動受け取り
def auto_receive_paypay(link):
    headers = {
        "Authorization": PAYPAY_AUTHORIZATION,
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "PayPay/5.3.0 (jp.ne.paypay.iosapp; build:xxxxx; iOS 18.4.1) Alamofire/5.8.1",
        "Client-Version": "5.3.0",
        "Client-OS-Version": "18.4.1",
        "Device-Name": "iPhone15,2",
        "Client-UUID": "c381c4fa-1c55-4cea-8b89-6f2d85e28552",
        "Device-UUID": "ccce2ff3-a9bd-4591-b0f2-ae069967a4bf",
        "Client-OS-Type": "IOS",
        "Timezone": "Asia/Tokyo",
        "System-Locale": "ja_JP",
        "Network-Status": "WIFI",
        "Client-Mode": "NORMAL",
        "Is-Emulator": "false",
        "Client-Type": "PAYPAYAPP"
    }

    try:
        response = requests.post("https://api.paypay.ne.jp/v2/sendMoney/receive", headers=headers)
        if response.status_code == 200:
            return "PayPay受け取り成功！"
        else:
            return f"PayPay受け取り失敗: {response.status_code}"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# LINEメッセージ送信
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

# LINEボタンメッセージ送信
def send_line_buttons_reply(reply_token, text, buttons):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}, {"type": "template", "altText": "選択してください", "template": {"type": "buttons", "actions": buttons}}]
    }
    requests.post(url, headers=headers, json=payload)
