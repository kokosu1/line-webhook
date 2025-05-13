@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        reply_token = event["replyToken"]
        user_id = event["source"]["userId"]

        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # 都市入力待ちモード時
            if user_mode.get(user_id) == "awaiting_city":
                city = text
                city_name = city_mapping.get(city, city)
                weather_message = get_weather_by_city(city_name)
                send_line_reply(reply_token, weather_message)
                
                # 天気取得失敗したらまだモード維持
                if "天気情報の取得に失敗" in weather_message:
                    return {"status": "ok"}
                else:
                    user_mode[user_id] = None  # 正常取得でモード解除
                    return {"status": "ok"}

            # 通常のコマンド処理
            if "paypay.ne.jp" in text:
                result = handle_paypay_link(text)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

            if text == "じゃんけん":
                send_janken_buttons(reply_token)
                return {"status": "ok"}

            if text == "天気":
                user_mode[user_id] = "awaiting_city"
                send_line_reply(reply_token, "どの都市の天気を知りたいですか？例えば「東京」や「大阪」など、都市名を送ってください。")
                return {"status": "ok"}

            if text == "支出":
                send_line_reply(reply_token, "「支出 食費 1000円」や「支出 食費 1000円 削除」で記録できます。集計は「レポート」と送ってね。")
                return {"status": "ok"}

            if text.startswith("支出"):
                result = handle_expense(user_id, text)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

            if text == "レポート":
                result = generate_report(user_id)
                send_line_reply(reply_token, result)
                return {"status": "ok"}

            # 他の無効な入力
            send_line_reply(reply_token, "「じゃんけん」「天気」「支出」などを試してみてね！")

        elif event["type"] == "postback":
            data = event["postback"]["data"]
            if data in ["グー", "チョキ", "パー"]:
                bot = random.choice(["グー", "チョキ", "パー"])
                result = judge_janken(data, bot)
                message = f"あなた: {data}\nBot: {bot}\n結果: {result}"
                send_line_reply(reply_token, message)

    return {"status": "ok"}
