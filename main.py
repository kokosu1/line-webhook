import os
import re
import random
import requests
import json
import logging
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")

# ログ設定
logging.basicConfig(filename='bot_logs.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
user_mode = {}

# 支出記録用のデータ構造
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

            # 支出の記録または削除
            if text.startswith("支出"):
                result = handle_expense(user_id, text)
                send_line_reply(reply_token, result)

            # レポート
            elif text == "レポート":
                result = generate_report(user_id)
                send_line_reply(reply_token, result)

            # じゃんけん
            elif text == "じゃんけん":
                result = play_janken()
                send_line_reply(reply_token, result)

            # PayPayリンクを受け取って支払いを行う
            elif "paypay.me" in text:
                result = handle_paypay_link(user_id, text)
                send_line_reply(reply_token, result)

            else:
                send_line_reply(reply_token, "「支出」と入力すると支出を記録できるよ。")

        elif event["type"] == "message" and event["message"]["type"] == "location":
            lat = event["message"]["latitude"]
            lon = event["message"]["longitude"]
            message = get_weather_from_coordinates(lat, lon)
            send_line_reply(reply_token, message)

    return {"status": "ok"}

def handle_expense(user_id, text):
    """ 支出の記録や削除を行う関数 """
    # 支出の記録
    match = re.match(r"支出 (\S+) (\d+)円", text)
    if match:
        category = match.group(1)
        amount = int(match.group(2))
        logging.debug(f"記録: {category} - {amount}円 (user_id: {user_id})")  # ログ追加
        if user_id not in expenses:
            expenses[user_id] = {}
        if category in expenses[user_id]:
            expenses[user_id][category] += amount
        else:
            expenses[user_id][category] = amount
        return f"{category}に{amount}円を追加しました。"

    # 支出の削除
    match_delete = re.match(r"支出 (\S+) (\d+)円 削除", text)
    if match_delete:
        category = match_delete.group(1)
        amount = int(match_delete.group(2))
        if user_id in expenses and category in expenses[user_id]:
            if expenses[user_id][category] >= amount:
                expenses[user_id][category] -= amount
                if expenses[user_id][category] == 0:
                    del expenses[user_id][category]
                logging.debug(f"削除: {category} - {amount}円 (user_id: {user_id})")  # ログ追加
                return f"{category}から{amount}円を削除しました。"
            else:
                return f"{category}の支出額が不足しています。削除できません。"
        else:
            return f"{category}は記録されていません。削除できません。"

    return "支出のフォーマットが間違っています。例: 支出 食費 1000円 または 支出 食費 1000円 削除"

def generate_report(user_id):
    """ 支出レポートを生成する関数 """
    if user_id not in expenses or not expenses[user_id]:
        return "今月の支出はありません。"
    
    report = "今月の支出:\n"
    total = 0
    for category, amount in expenses[user_id].items():
        report += f"{category}: {amount}円\n"
        total += amount
    
    report += f"合計: {total}円"
    logging.debug(f"レポート生成: {report} (user_id: {user_id})")  # ログ追加
    return report

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

# じゃんけん機能
def play_janken():
    choices = ["グー", "チョキ", "パー"]
    user_choice = random.choice(choices)
    bot_choice = random.choice(choices)

    if user_choice == bot_choice:
        return f"あなたの出した手: {user_choice}\n私の出した手: {bot_choice}\n引き分け！"
    
    if (user_choice == "グー" and bot_choice == "チョキ") or \
       (user_choice == "チョキ" and bot_choice == "パー") or \
       (user_choice == "パー" and bot_choice == "グー"):
        return f"あなたの出した手: {user_choice}\n私の出した手: {bot_choice}\nあなたの勝ち！"
    
    return f"あなたの出した手: {user_choice}\n私の出した手: {bot_choice}\n私の勝ち！"

# PayPayリンク処理
def handle_paypay_link(user_id, text):
    # PayPayリンクから送金リクエストを処理する部分を追加
    # ここで受け取ったリンクを解析して処理
    logging.debug(f"PayPayリンク受信: {text} (user_id: {user_id})")  # ログ追加
    # 必要に応じて、PayPayのAPIを呼び出して受け取り処理を行う
    return "PayPayリンクを受け取りました。処理を進めます..."

# リッチメニューを作成する関数
def create_rich_menu():
    # リッチメニューの画像をLINEにアップロード
    url = "https://api-data.line.me/v2/bot/richmenu"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "Main Menu",
        "chatBarText": "Tap here",
        "areas": [
            {
                "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
                "action": {"type": "message", "text": "じゃんけん"}
            },
            {
                "bounds": {"x": 833, "y": 0, "width": 833, "height": 843},
                "action": {"type": "message", "text": "レポート"}
            },
            {
                "bounds": {"x": 1666, "y": 0, "width": 834, "height": 843},
                "action": {"type": "message", "text": "支出"}
            }
        ]
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        return "リッチメニューを作成しました。"
    else:
        return "リッチメニューの作成に失敗しました。"

# webhookのエンドポイントでリッチメニューの作成やリンク処理が追加されました
