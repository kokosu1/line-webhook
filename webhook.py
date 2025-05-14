import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

user_mode = {}

# OpenWeatherMap APIで天気取得
def get_weather_by_city(city):
    api_key = "YOUR_API_KEY"  # あなたのAPIキーに置き換えてください
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ja'
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{city}の天気は {weather}、気温は {temp}℃です。"
    else:
        return "天気情報の取得に失敗しました。都市名が正しいか確認してください。"

# PayPayリンク検出
def detect_paypay_link(text):
    return "paypay.ne.jp" in text

def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_CHANNEL_ACCESS_TOKEN"  # あなたのトークンに置き換え
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(payload))

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]
        text = event["message"]["text"].strip()

        # PayPayリンク
        if detect_paypay_link(text):
            send_line_reply(reply_token, "現在この機能は開発中です。完成までお待ちください。")
            continue

        # じゃんけん
        if text == "じゃんけん":
            send_line_reply(reply_token, "じゃんけんボタンを押してね！")
            continue

        # 天気リクエスト
        if text == "天気":
            user_mode[user_id] = "awaiting_city"
            send_line_reply(reply_token, "どの都市の天気を知りたいですか？ 例：「東京」「大阪」など")
            continue

        # 天気モード：都市名受け取り
        if user_mode.get(user_id) == "awaiting_city":
            city_mapping = {
                "北海道": "Hokkaido", "青森": "Aomori", "岩手": "Iwate", "宮城": "Miyagi", "秋田": "Akita",
                "山形": "Yamagata", "福島": "Fukushima", "茨城": "Ibaraki", "栃木": "Tochigi", "群馬": "Gunma",
                "埼玉": "Saitama", "千葉": "Chiba", "東京": "Tokyo", "神奈川": "Kanagawa", "新潟": "Niigata",
                "富山": "Toyama", "石川": "Ishikawa", "福井": "Fukui", "山梨": "Yamanashi", "長野": "Nagano",
                "岐阜": "Gifu", "静岡": "Shizuoka", "愛知": "Aichi", "三重": "Mie", "滋賀": "Shiga", "京都": "Kyoto",
                "大阪": "Osaka", "兵庫": "Hyogo", "奈良": "Nara", "和歌山": "Wakayama", "鳥取": "Tottori",
                "島根": "Shimane", "岡山": "Okayama", "広島": "Hiroshima", "山口": "Yamaguchi", "徳島": "Tokushima",
                "香川": "Kagawa", "愛媛": "Ehime", "高知": "Kochi", "福岡": "Fukuoka", "佐賀": "Saga", "長崎": "Nagasaki",
                "熊本": "Kumamoto", "大分": "Oita", "宮崎": "Miyazaki", "鹿児島": "Kagoshima", "沖縄": "Okinawa"
            }
            city_name = city_mapping.get(text, text)
            weather = get_weather_by_city(city_name)
            send_line_reply(reply_token, weather)
            user_mode[user_id] = None
            continue

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
