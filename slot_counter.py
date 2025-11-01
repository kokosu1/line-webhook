import json
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# --- プレイヤーデータ保存 ---
users = {}

# --- LINE返信関数 ---
def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(data))

# --- 仮の設定推測関数（あとで強化可） ---
def estimate_setting(total, big, reg):
    if total == 0:
        return "データ不足"
    reg_rate = total / reg if reg > 0 else 9999
    if reg_rate < 300:
        return "設定6の可能性が高い"
    elif reg_rate < 400:
        return "設定4〜5の可能性あり"
    else:
        return "低設定の可能性大"

# --- LINEメッセージ受信 ---
@app.post("/callback")
async def callback(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        if event["type"] != "message":
            continue
        text = event["message"]["text"]
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        # --- 新規ユーザー初期化 ---
        if user_id not in users:
            users[user_id] = {"mode": None, "data": {}}

        user = users[user_id]

        # --- スタート ---
        if text.lower() in ["スタート", "start"]:
            user["mode"] = "input_machine"
            user["data"] = {}
            reply_message(reply_token, "🎰 何の台ですか？（例：マイジャグラーV、アイムジャグラーなど）")
            continue

        # --- 台名入力 ---
        if user["mode"] == "input_machine":
            user["data"]["machine"] = text
            user["mode"] = "input_stats"
            reply_message(reply_token, f"📝 台名：{text}\n今の総回転数、BIG回数、REG回数をカンマ区切りで送ってください。\n例：3500,10,12")
            continue

        # --- 台データ入力 ---
        if user["mode"] == "input_stats":
            try:
                total, big, reg = map(int, text.split(","))
                user["data"].update({"total": total, "big": big, "reg": reg})
                setting_estimate = estimate_setting(total, big, reg)
                user["data"]["setting_estimate"] = setting_estimate
                user["mode"] = "confirm_start"
                reply_message(reply_token, (
                    f"📊 台情報\n"
                    f"機種：{user['data']['machine']}\n"
                    f"総回転数：{total}\n"
                    f"BIG：{big}　REG：{reg}\n"
                    f"推測：{setting_estimate}\n\n"
                    "この台でスタートしますか？（はい / いいえ）"
                ))
            except:
                reply_message(reply_token, "⚠️ 入力形式が正しくありません。\n例：3500,10,12 のように送ってください。")
            continue

        # --- 確認後の処理 ---
        if user["mode"] == "confirm_start":
            if text == "はい":
                user["mode"] = "counting"
                reply_message(reply_token, "🕹 カウント開始！\nぶどう / BIG / REG / ハズレ などを送ると記録します。")
            elif text == "いいえ":
                user["mode"] = "input_machine"
                reply_message(reply_token, "❌ 台情報をもう一度入力します。\n何の台ですか？")
            else:
                reply_message(reply_token, "「はい」か「いいえ」で答えてください。")
            continue

        # --- カウントモード ---
        if user["mode"] == "counting":
            data = user["data"]
            data["total"] = data.get("total", 0) + 1

            if text == "ぶどう":
                data["grape"] = data.get("grape", 0) + 1
            elif text.upper() == "BIG":
                data["big"] += 1
            elif text.upper() == "REG":
                data["reg"] += 1
            elif text == "ハズレ":
                data["miss"] = data.get("miss", 0) + 1

            grape_rate = data["total"] / data.get("grape", 1)
            reply_message(reply_token, (
                f"🎯 現在のデータ\n"
                f"総G数：{data['total']}\n"
                f"ぶどう：{data.get('grape', 0)}（確率 {grape_rate:.1f}）\n"
                f"BIG：{data['big']}　REG：{data['reg']}"
            ))
            continue

        # --- それ以外の入力 ---
        reply_message(reply_token, "❓ コマンドがわかりません。「スタート」と送って新しく始められます。")

    return {"status": "ok"}