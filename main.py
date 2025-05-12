def send_line_reply(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lJvik2q3NiM1xeKywUqpIQto4FSQMPxgEgnOKz272jtk3ZBcux/7IOEjdgb4W12MDycIMoxnULp4xIHJ4xAbk4X7iSuvtKHFokmi4ZVaTwsN+SPHU8T+j9uXjYon6efMP68CjFi7fdVCbWOhV+8hPgdB04t89/1O/w1cDnyilFU="
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
