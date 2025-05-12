def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer あなたのチャネルアクセストークン"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }

    # LINEにリクエストを送信
    res = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

    # ステータスコードとレスポンス内容をログ出力
    print(f"LINE API status: {res.status_code}")
    print(f"LINE API response: {res.text}")
