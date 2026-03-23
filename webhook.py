import os
import asyncio
import requests
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from sheets import write_shift
from sheet_image import sheet_to_image
from quiz import start_quiz, answer_quiz, is_in_quiz
from paypay import handle_paypay

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

app = FastAPI()

anonymous_waiting = set()
anonymous_rooms = {}

# ===== LINE送信系 =====

def send_line_reply(token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)
    if res.status_code != 200:
        print(f"Reply error: {res.status_code} - {res.text}")

async def send_push_message(user_id, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: requests.post(
        "https://api.line.me/v2/bot/message/push", headers=headers, json=body))

# ===== Webhook =====

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event.get("replyToken")
        user_id = event["source"].get("userId")
        group_id = event["source"].get("groupId")

        if group_id:
            print(f"👥 グループID: {group_id}")
        print(f"👤 ユーザーID: {user_id}")

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # ===== 匿名チャット =====
            if text.lower() == "終了":
                if user_id in anonymous_rooms:
                    partner_id = anonymous_rooms.pop(user_id)
                    anonymous_rooms.pop(partner_id, None)
                    await send_push_message(user_id, "匿名チャットを終了しました。")
                    await send_push_message(partner_id, "相手がチャットを終了しました。")
                    return {"status": "ok"}
                elif user_id in anonymous_waiting:
                    anonymous_waiting.discard(user_id)
                    send_line_reply(reply_token, "匿名チャットの待機をキャンセルしました。")
                    return {"status": "ok"}

            if user_id in anonymous_rooms:
                partner_id = anonymous_rooms.get(user_id)
                if partner_id:
                    asyncio.create_task(send_push_message(partner_id, f"匿名相手: {text}"))
                return {"status": "ok"}

            if text == "匿名チャット":
                if user_id in anonymous_waiting:
                    send_line_reply(reply_token, "既にマッチング待機中です。")
                    return {"status": "ok"}
                if anonymous_waiting:
                    partner_id = anonymous_waiting.pop()
                    anonymous_rooms[user_id] = partner_id
                    anonymous_rooms[partner_id] = user_id
                    await send_push_message(user_id, "匿名チャットが開始されました。終了したい場合は「終了」と送信してください。")
                    await send_push_message(partner_id, "匿名チャットが開始されました。終了したい場合は「終了」と送信してください。")
                else:
                    anonymous_waiting.add(user_id)
                    send_line_reply(reply_token, "マッチング相手を探しています。しばらくお待ちください。")
                return {"status": "ok"}
            
            # ===== PayPay =====
            paypay_result = handle_paypay(text)
            if paypay_result:
                send_line_reply(reply_token, paypay_result)
                return {"status": "ok"}

            # ===== 管理者コマンド =====
            if user_id == ADMIN_USER_ID:
                if text == "シフト送信 前半":
                    from scheduler import send_shift_request
                    send_shift_request("first")
                    send_line_reply(reply_token, "前半のシフト通知を送信しました！")
                    return {"status": "ok"}
                elif text == "シフト送信 後半":
                    from scheduler import send_shift_request
                    send_shift_request("second")
                    send_line_reply(reply_token, "後半のシフト通知を送信しました！")
                    return {"status": "ok"}
                elif text.startswith("名前追加 "):
                    new_name = text.replace("名前追加 ", "").strip()
                    if new_name:
                        from liff_names import add_name
                        add_name(new_name)
                        send_line_reply(reply_token, f"{new_name} を名前リストに追加しました！")
                    else:
                        send_line_reply(reply_token, "名前を入力してください。例：名前追加 田中")
                    return {"status": "ok"}
                elif text.startswith("名前削除 "):
                    del_name = text.replace("名前削除 ", "").strip()
                    if del_name:
                        from liff_names import remove_name
                        remove_name(del_name)
                        send_line_reply(reply_token, f"{del_name} を名前リストから削除しました！")
                    return {"status": "ok"}
                elif text == "名前一覧":
                    from liff_names import get_names
                    names = get_names()
                    send_line_reply(reply_token, "現在の名前リスト：\n" + "\n".join(names))
                    return {"status": "ok"}
                elif text.startswith("シフト画像 "):
                    sheet_name = text.replace("シフト画像 ", "").strip()
                    path = sheet_to_image(sheet_name, "/tmp/shift.png")
                    if path:
                        import cloudinary
                        import cloudinary.uploader
                        cloudinary.config(
                            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                            api_key=os.getenv("CLOUDINARY_API_KEY"),
                            api_secret=os.getenv("CLOUDINARY_API_SECRET")
                        )
                        result = cloudinary.uploader.upload(path)
                        image_url = result.get("secure_url")
                        push_headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
                        }
                        push_body = {
                            "to": os.getenv("LINE_GROUP_ID"),
                            "messages": [{
                                "type": "image",
                                "originalContentUrl": image_url,
                                "previewImageUrl": image_url
                            }]
                        }
                        requests.post("https://api.line.me/v2/bot/message/push", headers=push_headers, json=push_body)
                        send_line_reply(reply_token, f"「{sheet_name}」の画像を送信しました！")
                    else:
                        send_line_reply(reply_token, "シートが見つかりませんでした。")
                    return {"status": "ok"}

            # ===== 日本語クイズ =====
            if text in ["日本語クイズ", "クイズ"]:
                send_line_reply(reply_token, start_quiz(user_id))
                return {"status": "ok"}

            if is_in_quiz(user_id):
                send_line_reply(reply_token, answer_quiz(user_id, text))
                return {"status": "ok"}

        return {"status": "ok"}

# ===== シフト提出API =====

@app.post("/shift/submit")
async def shift_submit(request: Request):
    data = await request.json()
    name = data.get("name")
    dates = data.get("dates")
    period = data.get("period")
    year = int(data.get("year"))
    month = int(data.get("month"))

    if not all([name, dates, period, year, month]):
        return {"status": "error", "message": "パラメータ不足"}

    try:
        write_shift(name, dates, period, year, month)
        return {"status": "success"}
    except Exception as e:
        print(f"[Error] スプレッドシート書き込み失敗: {e}")
        return {"status": "error", "message": str(e)}

# ===== LIFF =====

@app.get("/liff")
async def liff_page():
    return FileResponse("liff/index.html")

@app.get("/staff-names")
async def staff_names():
    from liff_names import get_names
    names = get_names()
    return {"names": names}
