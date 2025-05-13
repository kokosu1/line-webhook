import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import openai

# .envファイルから秘密情報を読み込む
load_dotenv()

# 環境変数からキーを取り出す
openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

# ユーザーが「ChatGPT」か「天気」か記録する辞書
user_mode = {}

# 日本語の市名 → API用英語名
city_mapping = {
    "府中市": "Fuchu",
    "東京": "Tokyo",
    "札幌": "Sapporo",
    "大阪": "Osaka",
    "名古屋": "Nagoya"
}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            if text.lower() == "chatgpt":
                user_mode[user_id] = "chatgpt"
                send_line_reply(reply_token, "ChatGPTモードに切り替えたよ！質問してね。")
            elif "天気" in text:
                # ユーザーにどこの天気を知りたいかを尋ねる
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気を知りたいですか？例: 東京、名古屋、札幌 など")
            elif user_mode.get(user_id) == "weather":
                # ユーザーが都市名を送信したら天気情報を送る
                city = detect_city(text)
                if city == "Tokyo":  # 都市が見つからなかった場合の処理
                    send_line_reply(reply_token, "指定された都市の天気情報が見つかりませんでした。別の都市を試してみてください。")
                else:
                    weather_message = get_weather(city)
                    send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None  # 天気情報を送った後、モードをリセット
            elif user_mode.get(user_id) == "chatgpt":
                answer = ask_chatgpt(text)
                send_line_reply(reply_token, answer)
            else:
                send_line_reply(reply_token, "「天気」または「ChatGPT」と送ってね！")

    return {"status": "ok"}

def detect_city(text):
    # ユーザーが送ったテキストから都市名を検出
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Tokyo"  # 都市が見つからなかった場合はデフォルトで東京を返す

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
        return f"{temp}℃で天気は{weather}ってなってるよ！"

def ask_chatgpt(question):
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return res.choices[0].message["content"].strip()
    except Exception:
        return "ChatGPTとの通信に失敗しました。"

def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
