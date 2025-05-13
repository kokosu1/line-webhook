import os
import re
import requests
import json
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")

app = FastAPI()
user_mode = {}
user_expenses = {}  # ユーザーごとの支出を記録

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

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # 支出情報の解析
            if "円" in text:
                try:
                    category, amount = parse_expense(text)
                    if category:
                        if user_id not in user_expenses:
                            user_expenses[user_id] = {}
                        if category not in user_expenses[user_id]:
                            user_expenses[user_id][category] = 0
                        
                        user_expenses[user_id][category] += amount
                        save_expenses()
                        send_line_reply(reply_token, f"{category}に{amount}円を記録しました！")
                    else:
                        send_line_reply(reply_token, "支出の形式が正しくありません。例: 食費500円")
                except Exception as e:
                    send_line_reply(reply_token, f"エラーが発生しました: {str(e)}")
                continue

            # レポート要求
            elif "レポート" in text or "支出レポート" in text:
                report_message = generate_report(user_id)
                send_line_reply(reply_token, report_message)
                continue

            # PayPayリンクの自動検出
            link = detect_paypay_link(text)
            if link:
                result = auto_receive_paypay()
                send_line_reply(reply_token, result)
                continue

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

            else:
                send_line_reply(reply_token, "「天気」や PayPay 受け取りリンクを送ってみてね！")

        elif event["type"] == "message" and event["message"]["type"] == "location":
            lat = event["message"]["latitude"]
            lon = event["message"]["longitude"]
            message = get_weather_from_coordinates(lat, lon)
            send_line_reply(reply_token, message)

    return {"status": "ok"}

# 支出解析
def parse_expense(text):
    match = re.match(r"([^\d]+)(\d+)円", text)
    if match:
        category = match.group(1).strip()
        amount = int(match.group(2))
        return category, amount
    return None, None

# レポートの生成
def generate_report(user_id):
    if user_id not in user_expenses or not user_expenses[user_id]:
        return "まだ支出の記録がありません。支出を記録してから、レポートを送ることができます。"

    expenses = user_expenses[user_id]
    total_expenses = {}
    for category, amount in expenses.items():
        total_expenses[category] = amount

    # レポートメッセージ作成
    message = "現在の支出レポートです:\n"
    for category, amount in total_expenses.items():
        message += f"{category}: {amount}円\n"

    return message

# 支出の保存
def save_expenses():
    with open('user_expenses.json', 'w', encoding='utf-8') as f:
        json.dump(user_expenses, f, ensure_ascii=False, indent=4)

# 都市検出
def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"

# PayPayリンクの検出
def detect_paypay_link(text):
    pattern = r'https://.*paypay\.ne\.jp/\w+'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# 天気情報取得
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

# 緯度経度から天気情報取得
def get_weather_from_coordinates(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

# 天気メッセージの整形
def format_weather_message(weather, temp):
    messages = {
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
    return messages.get(weather, f"今の天気は{weather}で、気温は{temp}℃くらいだよ！")

# PayPay受け取り自動処理
def auto_receive_paypay():
    headers = {
        "Authorization": PAYPAY_AUTHORIZATION,
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "PayPay/5.3.0 (jp.ne.paypay.iosapp)",
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
