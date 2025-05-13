import requests
from fastapi import FastAPI, Request
import openai

app = FastAPI()

# OpenAI APIキー
openai.api_key = "import requests
from fastapi import FastAPI, Request
import openai

app = FastAPI()

# OpenAI APIキー
openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# LINE設定
LINE_CHANNEL_ACCESS_TOKEN = "lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="

# ユーザーモード記録
user_mode = {}

# 天気API設定
WEATHER_API_KEY = "dd9f6e2b4116d6c124be61d261da444e"

# 市名変換
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
                user_mode[user_id] = "weather"
                city = detect_city(text)
                weather_message = get_weather(city)
                send_line_reply(reply_token, weather_message)
            elif user_mode.get(user_id) == "chatgpt":
                answer = ask_chatgpt(text)
                send_line_reply(reply_token, answer)
            else:
                send_line_reply(reply_token, "「天気」または「ChatGPT」と送ってね！")

    return {"status": "ok"}

def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Tokyo"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])

    if weather in ["Clear"]:
        msg = f"今日は晴れだよ！{temp}℃くらい。良い一日を！☀️"
    elif weather in ["Clouds"]:
        msg = f"今日はくもりかな〜。気温は{temp}℃くらいだよ。☁️"
    elif weather in ["Rain", "Drizzle"]:
        msg = f"今日は雨っぽいよ。{temp}℃くらいだから傘忘れずにね！☔"
    elif weather in ["Snow"]:
        msg = f"今日は雪が降ってるみたい！寒いから気をつけてね〜 {temp}℃だよ。❄️"
    else:
        msg = f"{temp}℃で天気は{weather}ってなってるよ！"
    return msg

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
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)"

# LINE設定
LINE_CHANNEL_ACCESS_TOKEN = "あなたのLINEアクセストークン"

# ユーザーモード記録
user_mode = {}

# 天気API設定
WEATHER_API_KEY = "dd9f6e2b4116d6c124be61d261da444e"

# 市名変換
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
                user_mode[user_id] = "weather"
                city = detect_city(text)
                weather_message = get_weather(city)
                send_line_reply(reply_token, weather_message)
            elif user_mode.get(user_id) == "chatgpt":
                answer = ask_chatgpt(text)
                send_line_reply(reply_token, answer)
            else:
                send_line_reply(reply_token, "「天気」または「ChatGPT」と送ってね！")

    return {"status": "ok"}

def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Tokyo"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code != 200:
        return "天気情報の取得に失敗しました。"
    data = res.json()
    weather = data["weather"][0]["main"]
    temp = round(data["main"]["temp"])

    if weather in ["Clear"]:
        msg = f"今日は晴れだよ！{temp}℃くらい。良い一日を！☀️"
    elif weather in ["Clouds"]:
        msg = f"今日はくもりかな〜。気温は{temp}℃くらいだよ。☁️"
    elif weather in ["Rain", "Drizzle"]:
        msg = f"今日は雨っぽいよ。{temp}℃くらいだから傘忘れずにね！☔"
    elif weather in ["Snow"]:
        msg = f"今日は雪が降ってるみたい！寒いから気をつけてね〜 {temp}℃だよ。❄️"
    else:
        msg = f"{temp}℃で天気は{weather}ってなってるよ！"
    return msg

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
