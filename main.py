import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import random

# .envファイルから秘密情報を読み込む
load_dotenv()

# 環境変数からキーを取り出す
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

# ユーザーが「天気」「おみくじ」「クイズ」「じゃんけん」のモードを記録する辞書
user_mode = {}

# 日本の都道府県と市、ベトナムの都市
city_mapping = {
    # 日本の都道府県と市
    "北海道": "Hokkaido",
    "青森": "Aomori",
    "岩手": "Iwate",
    "宮城": "Miyagi",
    "秋田": "Akita",
    "山形": "Yamagata",
    "福島": "Fukushima",
    "茨城": "Ibaraki",
    "栃木": "Tochigi",
    "群馬": "Gunma",
    "埼玉": "Saitama",
    "千葉": "Chiba",
    "東京": "Tokyo",
    "神奈川": "Kanagawa",
    "新潟": "Niigata",
    "富山": "Toyama",
    "石川": "Ishikawa",
    "福井": "Fukui",
    "山梨": "Yamanashi",
    "長野": "Nagano",
    "岐阜": "Gifu",
    "静岡": "Shizuoka",
    "愛知": "Aichi",
    "三重": "Mie",
    "滋賀": "Shiga",
    "京都": "Kyoto",
    "大阪": "Osaka",
    "兵庫": "Hyogo",
    "奈良": "Nara",
    "和歌山": "Wakayama",
    "鳥取": "Tottori",
    "島根": "Shimane",
    "岡山": "Okayama",
    "広島": "Hiroshima",
    "山口": "Yamaguchi",
    "徳島": "Tokushima",
    "香川": "Kagawa",
    "愛媛": "Ehime",
    "高知": "Kochi",
    "福岡": "Fukuoka",
    "佐賀": "Saga",
    "長崎": "Nagasaki",
    "熊本": "Kumamoto",
    "大分": "Oita",
    "宮崎": "Miyazaki",
    "鹿児島": "Kagoshima",
    "沖縄": "Okinawa",
    "府中市": "Fuchu",
    "札幌": "Sapporo",
    "名古屋": "Nagoya",

    # ベトナムの都市
    "ハノイ": "Hanoi",
    "ホーチミン": "HoChiMinh",
    "ダナン": "DaNang",
    "フエ": "Hue",
    "ハイフォン": "HaiPhong",
    "カントー": "CanTho",
    "ビンズオン": "BinhDuong",
    "バクニン": "BacNinh",
    "ダラット": "DaLat",
    "ニャチャン": "NhaTrang",
    "ホイアン": "HoiAn",
    "ソクチャン": "SocTrang",
    "ロングアン": "LongAn",
    "カイラン": "CaMau"
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

            # 「天気」モードに切り替え
            if "天気" in text:
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気を知りたいですか？例: 東京、名古屋、札幌 など")
            
            # 天気情報の送信
            elif user_mode.get(user_id) == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "指定された都市の天気情報が見つかりませんでした。別の都市を試してみてください。")
                else:
                    weather_message = get_weather(city)
                    send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None  # 天気情報を送った後、モードをリセット

            # 「おみくじ」モード
            elif "おみくじ" in text:
                user_mode[user_id] = "omikuji"
                result = random.choice(["大吉", "中吉", "小吉", "凶", "大凶"])
                send_line_reply(reply_token, f"おみくじの結果は「{result}」です！")

            # 「都道府県クイズ」モード
            elif "クイズ" in text:
                user_mode[user_id] = "quiz"
                question = "次のうち、実際の都道府県の名前はどれでしょう？\n1. 高砂\n2. 豊橋\n3. 栃木\n4. 福岡"
                answer = "栃木"
                send_line_reply(reply_token, question)
                user_mode[user_id] = "quiz_answer"
                user_mode[user_id] = answer

            # 「じゃんけん」モード
            elif "じゃんけん" in text:
                user_mode[user_id] = "janken"
                send_line_reply(reply_token, "じゃんけんをしましょう！グー、チョキ、パーのいずれかを送ってください。")

            # じゃんけんの処理
            elif user_mode.get(user_id) == "janken":
                user_choice = text.strip()
                choices = ["グー", "チョキ", "パー"]
                bot_choice = random.choice(choices)
                result = determine_janken_result(user_choice, bot_choice)
                send_line_reply(reply_token, f"あなたの選択: {user_choice}\nボットの選択: {bot_choice}\n結果: {result}")
                user_mode[user_id] = None

            # クイズの答え合わせ
            elif user_mode.get(user_id) == "quiz_answer":
                if text.strip() == user_mode[user_id]:
                    send_line_reply(reply_token, "正解です！")
                else:
                    send_line_reply(reply_token, "不正解です。もう一度挑戦してね。")
                user_mode[user_id] = None

            # モードが設定されていない場合
            else:
                send_line_reply(reply_token, "「天気」「おみくじ」「クイズ」「じゃんけん」から選んでください！")

    return {"status": "ok"}

def detect_city(text):
    # ユーザーが送ったテキストから都市名を検出
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"  # 都市が見つからなかった場合は「Unknown」を返す

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

def determine_janken_result(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "あいこ"
    elif (user_choice == "グー" and bot_choice == "チョキ") or \
         (user_choice == "チョキ" and bot_choice == "パー") or \
         (user_choice == "パー" and bot_choice == "グー"):
        return "あなたの勝ち！"
    else:
        return "ボットの勝ち！"

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
