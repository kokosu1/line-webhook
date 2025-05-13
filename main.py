import os
import random
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# .envファイルから秘密情報を読み込む
load_dotenv()

# 環境変数からキーを取り出す
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

app = FastAPI()

# ユーザーが「ChatGPT」か「天気」か記録する辞書
user_mode = {}

# ボタンテンプレートでじゃんけんモードを選ばせる
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

# ユーザーが選んだ手とコンピュータの手を比べて結果を返す
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

# webhookで受けたメッセージを処理
@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            text = event["message"]["text"].strip()
            reply_token = event["replyToken"]

            # 「じゃんけん」と送られた場合
            if "じゃんけん" in text:
                user_mode[user_id] = "rps"  # じゃんけんモードに切り替え
                send_rock_paper_scissors(reply_token)  # ボタンテンプレートで表示

            # じゃんけんモードの場合
            elif user_mode.get(user_id) == "rps":
                result_message = judge_rps(text)  # じゃんけんの結果を判定
                send_line_reply(reply_token, result_message)  # 結果を返信
                user_mode[user_id] = None  # モードリセット

            # モードが設定されていない場合
            else:
                send_line_reply(reply_token, "「じゃんけん」と送ってね！")

    return {"status": "ok"}

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
