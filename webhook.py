import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ユーザーごとのモード管理
user_mode = {}

# 都市名と天気の取得処理（例: OpenWeatherMap APIを使う場合）
def get_weather_by_city(city):
    # OpenWeatherMap APIのキーとエンドポイント
    api_key = "YOUR_API_KEY"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',  # 摂氏温度
        'lang': 'ja'
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{city}の天気は {weather} で、気温は {temp}°C です。"
    else:
        return "天気情報の取得に失敗しました。都市名が正しいか確認してください。"

# PayPayリンク自動検出
def detect_paypay_link(text):
    if "paypay.ne.jp" in text:
        return True
    return False

# 支出の管理（簡易版）
expense_data = {}

def handle_expense(user_id, text):
    parts = text.split(" ")
    if len(parts) < 3:
        return "支出の形式が不正です。例:「支出 食費 1000円」"

    category = parts[1]
    amount = parts[2]

    # 支出データの保存
    if user_id not in expense_data:
        expense_data[user_id] = []
    expense_data[user_id].append({'category': category, 'amount': amount})

    return f"{category} に {amount} 円を支出として記録しました。"

def generate_report(user_id):
    if user_id not in expense_data or not expense_data[user_id]:
        return "まだ支出が記録されていません。"
    
    report = "支出レポート:\n"
    total = 0
    for expense in expense_data[user_id]:
        report += f"{expense['category']}: {expense['amount']}円\n"
        total += int(expense['amount'].replace('円', ''))

    report += f"\n合計: {total}円"
    return report

# LINE APIにメッセージを送信
def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_CHANNEL_ACCESS_TOKEN"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(payload))

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]
        text = event["message"]["text"].strip()

        # PayPayリンクの自動検出
        if detect_paypay_link(text):
            send_line_reply(reply_token, "現在この機能は開発中です。完成までお待ちください。")
            continue

        # じゃんけんボタン
        if text == "じゃんけん":
            send_line_reply(reply_token, "じゃんけんボタンを押してね！")
            continue

        # 「天気」のリクエスト
        if text == "天気":
            user_mode[user_id] = "awaiting_city"  # モードを「都市待機」に設定
            send_line_reply(reply_token, "どの都市の天気を知りたいですか？例:「東京」や「大阪」などの都市名を送ってください。")
            continue

        # 天気モードで都市名を受け取る
        if user_mode.get(user_id) == "awaiting_city":
            city = text
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
            city_name = city_mapping.get(city, city)
            weather_message = get_weather_by_city(city_name)
            send_line_reply(reply_token, weather_message)
            user_mode[user_id] = None  # 天気モード終了後はモードリセット
            continue

        # 支出機能
        if text == "支出":
            send_line_reply(reply_token, "支出を記録します。例: 「支出 食費 1000円」")
            continue

        # 支出の記録
        if text.startswith("支出"):
            result = handle_expense(user_id, text)
            send_line_reply(reply_token, result)
            continue

        # 支出レポート
        if text == "レポート":
            result = generate_report(user_id)
            send_line_reply(reply_token, result)
            continue

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
