import os
import re
import requests
import json
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")

app = FastAPI()
user_mode = {}
expenses = {}

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

            # 支出の処理
            elif '支出' in text:
                handle_expenses(user_id, text, reply_token)

            elif '支出削除' in text:
                handle_expenses(user_id, text, reply_token)

            # レポート表示
            elif 'レポート' in text:
                if user_id in expenses and expenses[user_id]:
                    report = "\n".join([f"{category}: {amount}円" for category, amount in expenses[user_id].items()])
                    send_line_reply(reply_token, f"今月の支出:\n{report}")
                else:
                    send_line_reply(reply_token, "支出記録がありません。")

            else:
                send_line_reply(reply_token, "「天気」や PayPay 受け取りリンクを送ってみてね！")

        elif event["type"] == "message" and event["message"]["type"] == "location":
            lat = event["message"]["latitude"]
            lon = event["message"]["longitude"]
            message = get_weather_from_coordinates(lat, lon)
            send_line_reply(reply_token, message)

    return {"status": "ok"}

# 支出の処理
def handle_expenses(user_id, text, reply_token):
    if '支出' in text:
        # 支出記録の処理
        match = re.match(r'支出 (\w+) (\d+)円', text)
        if match:
            category = match.group(1)
            amount = int(match.group(2))

            # 支出記録を保存
            if user_id not in expenses:
                expenses[user_id] = {}
            if category not in expenses[user_id]:
                expenses[user_id][category] = 0
            expenses[user_id][category] += amount

            send_line_reply(reply_token, f"{category}に{amount}円を追加しました！")

        # 支出削除
        elif '支出削除' in text:
            match_delete = re.match(r'支出削除 (\w+) (\d+)円', text)
            if match_delete:
                category = match_delete.group(1)
                amount = int(match_delete.group(2))

                # 削除する支出が存在するか確認
                if user_id in expenses and category in expenses[user_id]:
                    current_amount = expenses[user_id][category]

                    if current_amount >= amount:
                        expenses[user_id][category] -= amount
                        if expenses[user_id][category] == 0:
                            del expenses[user_id][category]
                        send_line_reply(reply_token, f"{category}から{amount}円を削除しました！")
                    else:
                        send_line_reply(reply_token, f"{category}の金額が不足しています。現在の金額は{current_amount}円です。")
                else:
                    send_line_reply(reply_token, "指定された支出が見つかりません。")

# 都市名の検出
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

# 天気の取得
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

# 位置情報から天気を取得
def get_weather_from_coordinates(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])
    return format_weather_message(weather, temp)

# 天気メッセージのフォーマット
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

# PayPayの受け取り
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
            return "順次準備中です。完成までお待ちください。"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# LINEへの返信
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
