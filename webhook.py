import requests
import json
from flask import Flask, request, abort

app = Flask(__name__)

# OpenWeatherMap APIキーと都市名
API_KEY = 'dd9f6e2b4116d6c124be61d261da444e'  # OpenWeatherMapで取得したAPIキー
CITY = 'Tokyo'  # 任意の都市名（例: 東京）

# LINEの設定
LINE_API_URL = 'https://api.line.me/v2/bot/message/reply'
LINE_CHANNEL_ACCESS_TOKEN = 'lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '7e03c4249375d47fca0367c22689c165'

# 天気情報を取得する関数
def get_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&lang=ja&units=metric'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        main_weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"現在の{CITY}の天気は {main_weather} で、気温は {temp}°C です。"
    else:
        return "天気情報の取得に失敗しました。"

# LINE Botの応答処理
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']

    # 署名の検証（LINE SDKを使うと簡単にできます）
    if not is_valid_signature(body, signature):
        abort(400)

    events = json.loads(body)['events']
    
    for event in events:
        if event['type'] == 'message' and event['message']['text'] == '天気':
            reply_token = event['replyToken']
            weather_info = get_weather()
            send_reply_message(reply_token, weather_info)

    return 'OK'

# LINE Botへ返信メッセージを送る関数
def send_reply_message(reply_token, message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
    }

    payload = {
        'replyToken': reply_token,
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }

    requests.post(LINE_API_URL, headers=headers, data=json.dumps(payload))

# Webhook用の署名を検証する関数
def is_valid_signature(body, signature):
    # チャネルシークレットを使って署名を検証する処理を記述
    # この部分はLINE SDKを利用すると自動で検証できます
    return True  # 簡略化のため常にTrueを返しています

if __name__ == "__main__":
    app.run(debug=True)
