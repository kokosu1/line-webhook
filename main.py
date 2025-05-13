import os
import random 
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# .envファイルから秘密情報を読み込む
load_dotenv()

# 環境変数からキーを取り出す
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

# ユーザーが「ChatGPT」か「天気」か記録する辞書
user_mode = {}

# 日本語の市名 → API用英語名
city_mapping = {
    city_mapping = {
    "府中市": "Fuchu",
    "東京": "Tokyo",
    "札幌": "Sapporo",
    "大阪": "Osaka",
    "名古屋": "Nagoya",
    "北海道": "Hokkaido",
    "青森県": "Aomori",
    "岩手県": "Iwate",
    "宮城県": "Miyagi",
    "秋田県": "Akita",
    "山形県": "Yamagata",
    "福島県": "Fukushima",
    "茨城県": "Ibaraki",
    "栃木県": "Tochigi",
    "群馬県": "Gunma",
    "埼玉県": "Saitama",
    "千葉県": "Chiba",
    "東京都": "Tokyo",
    "神奈川県": "Kanagawa",
    "新潟県": "Niigata",
    "富山県": "Toyama",
    "石川県": "Ishikawa",
    "福井県": "Fukui",
    "山梨県": "Yamanashi",
    "長野県": "Nagano",
    "岐阜県": "Gifu",
    "静岡県": "Shizuoka",
    "愛知県": "Aichi",
    "三重県": "Mie",
    "滋賀県": "Shiga",
    "京都府": "Kyoto",
    "大阪府": "Osaka",
    "兵庫県": "Hyogo",
    "奈良県": "Nara",
    "和歌山県": "Wakayama",
    "鳥取県": "Tottori",
    "島根県": "Shimane",
    "岡山県": "Okayama",
    "広島県": "Hiroshima",
    "山口県": "Yamaguchi",
    "徳島県": "Tokushima",
    "香川県": "Kagawa",
    "愛媛県": "Ehime",
    "高知県": "Kochi",
    "福岡県": "Fukuoka",
    "佐賀県": "Saga",
    "長崎県": "Nagasaki",
    "熊本県": "Kumamoto",
    "大分県": "Oita",
    "宮崎県": "Miyazaki",
    "鹿児島県": "Kagoshima",
    "沖縄県": "Okinawa",
    
    # ベトナムの都市
    "ホーチミン市": "Ho Chi Minh City",
    "ハノイ": "Hanoi",
    "ダナン": "Da Nang",
    "ホイアン": "Hoi An",
    "ハイフォン": "Hai Phong",
    "ニンビン": "Ninh Binh",
    "フエ": "Hue",
    "ビンディン": "Vinh Dien",
    "カントー": "Can Tho",
    "クイニョン": "Quy Nhon",
    "ニャチャン": "Nha Trang"
}
}

# じゃんけんのボタンテンプレート
def send_rock_paper_scissors(reply_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "template",
                "altText": "じゃんけんを選んでね",
                "template": {
                    "type": "buttons",
                    "title": "じゃんけん",
                    "text": "どれを出す？",
                    "actions": [
                        {
                            "type": "message",
                            "label": "グー",
                            "text": "グー"
                        },
                        {
                            "type": "message",
                            "label": "チョキ",
                            "text": "チョキ"
                        },
                        {
                            "type": "message",
                            "label": "パー",
                            "text": "パー"
                        }
                    ]
                }
            }
        ]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

# じゃんけんの結果を判定
def judge_rps(user_hand):
    hands = ["グー", "チョキ", "パー"]
    computer_hand = random.choice(hands)

    if user_hand == computer_hand:
        result = "引き分け！"
    elif (user_hand == "グー" and computer_hand == "チョキ") or \
         (user_hand == "チョキ" and computer_hand == "パー") or \
         (user_hand == "パー" and computer_hand == "グー"):
        result = f"あなたの「{user_hand}」が勝ち！コンピュータは「{computer_hand}」でした！"
    else:
        result = f"あなたの「{user_hand}」が負け！コンピュータは「{computer_hand}」でした！"
    
    return result

# 天気情報を取得
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

# おみくじ
def omikuji():
    fortunes = [
        "大吉！素晴らしい一年が待っているよ！",
        "中吉！よいことがありそうだよ！",
        "小吉！まあまあの一年になるかもね。",
        "凶！少し注意が必要かも。気をつけて！"
    ]
    return random.choice(fortunes)

# 都道府県クイズ
def prefecture_quiz():
    prefectures = ["東京", "大阪", "京都", "北海道", "沖縄"]
    answer = random.choice(prefectures)
    return answer

# LINEに返信を送る関数
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

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            # モードの切り替え
            if text == "じゃんけん":
                user_mode[user_id] = "rps"
                send_rock_paper_scissors(reply_token)

            elif text == "天気":
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気を知りたいですか？例: 東京、名古屋、札幌 など")

            elif text == "おみくじ":
                user_mode[user_id] = "omikuji"
                fortune = omikuji()
                send_line_reply(reply_token, fortune)

            elif text == "クイズ":
                user_mode[user_id] = "quiz"
                prefecture = prefecture_quiz()
                send_line_reply(reply_token, f"次の都道府県はどこでしょうか？\n{prefecture}の位置を答えてね！")

            # 天気情報
            elif user_mode.get(user_id) == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "指定された都市の天気情報が見つかりませんでした。別の都市を試してみてください。")
                else:
                    weather_message = get_weather(city)
                    send_line_reply(reply_token, weather_message)
                user_mode[user_id] = None  # モードリセット

            # じゃんけんモード
            elif user_mode.get(user_id) == "rps":
                result_message = judge_rps(text)
                send_line_reply(reply_token, result_message)
                user_mode[user_id] = None  # モードリセット

            # クイズの答え
            elif user_mode.get(user_id) == "quiz":
                # ここに都道府県クイズの答え処理を追加することも可能
                send_line_reply(reply_token, f"答えは{prefecture_quiz()}でした！")
                user_mode[user_id] = None  # モードリセット

            else:
                send_line_reply(reply_token, "「じゃんけん」「天気」「おみくじ」「クイズ」などと送ってね！")

    return {"status": "ok"}

# ユーザーが送ったテキストから都市名を検出
def detect_city(text):
    for jp_name in city_mapping:
        if jp_name in text:
            return city_mapping[jp_name]
    return "Unknown"  # 都市が見つからなかった場合は「Unknown」を返す
