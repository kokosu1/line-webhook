@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    events = body.get("events", [])

    for event in events:
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]

        # ポストバック処理（じゃんけんのボタン）
        if event["type"] == "postback":
            data = event["postback"]["data"]
            if user_mode.get(user_id) == "janken":
                user_choice = data
                choices = ["グー", "チョキ", "パー"]
                while True:
                    bot_choice = random.choice(choices)
                    result = determine_janken_result(user_choice, bot_choice)
                    if result != "引き分け":
                        break
                send_line_reply(reply_token, f"あなたの選択: {user_choice}\nボットの選択: {bot_choice}\n結果: {result}")
                user_mode[user_id] = None
            return {"status": "ok"}

        # テキストメッセージの処理
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()

            # PayPayリンク処理
            if "https://pay.paypay.ne.jp/" in text:
                pay_code = text.split("https://pay.paypay.ne.jp/")[1].strip()
                response_message = process_paypay_link(pay_code)
                send_line_reply(reply_token, response_message)

            elif "天気" in text:
                user_mode[user_id] = "weather"
                send_line_reply(reply_token, "どこの天気を知りたいですか？ 例: 東京、札幌、沖縄 など")

            elif user_mode.get(user_id) == "weather":
                city = detect_city(text)
                if city == "Unknown":
                    send_line_reply(reply_token, "指定された都市が見つかりませんでした。他の都市名を試してね！")
                else:
                    message = get_weather(city)
                    send_line_reply(reply_token, message)
                user_mode[user_id] = None

            elif "おみくじ" in text:
                result = random.choice(["大吉", "中吉", "小吉", "末吉", "凶", "大凶"])
                send_line_reply(reply_token, f"おみくじの結果は…「{result}」でした！")

            elif "クイズ" in text:
                user_mode[user_id] = "quiz_answer"
                user_mode[user_id + "_answer"] = "栃木"
                quiz = "次のうち、実際の都道府県はどれ？\n1. 高砂\n2. 豊橋\n3. 栃木\n4. 福岡"
                send_line_reply(reply_token, quiz)

            elif user_mode.get(user_id) == "quiz_answer":
                correct = user_mode.get(user_id + "_answer")
                if text.strip() == correct:
                    send_line_reply(reply_token, "正解だよ！すごい！")
                else:
                    send_line_reply(reply_token, "不正解…また挑戦してみてね！")
                user_mode[user_id] = None
                user_mode.pop(user_id + "_answer", None)

            elif "じゃんけん" in text:
                user_mode[user_id] = "janken"
                buttons = [
                    {"type": "postback", "label": "✊ グー", "data": "グー"},
                    {"type": "postback", "label": "✌️ チョキ", "data": "チョキ"},
                    {"type": "postback", "label": "🖐️ パー", "data": "パー"}
                ]
                send_line_buttons_reply(reply_token, "じゃんけんするよ〜！どれを出す？", buttons)

            else:
                send_line_reply(reply_token, "「天気」「おみくじ」「クイズ」「じゃんけん」って言ってみてね！")

        # 位置情報メッセージの処理
        if event["type"] == "message" and event["message"]["type"] == "location":
            latitude = event["message"]["latitude"]
            longitude = event["message"]["longitude"]
            weather_message = get_weather_from_coordinates(latitude, longitude)
            send_line_reply(reply_token, weather_message)

    return {"status": "ok"}

# PayPayリンクの処理
def process_paypay_link(pay_code):
    headers = {"Authorization": f"Bearer {os.getenv('PAYPAY_API_KEY')}"}
    params = {"payPayLang": "ja", "verificationCode": pay_code}
    url = "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo"

    response = requests.get(url, params=params, headers=headers).json()

    if response["header"]["resultCode"] == "S0000":
        status = response["payload"]["orderStatus"]
        if status == "SUCCESS":
            return "受け取り済みのリンクです"
        elif status == "PENDING":
            return "受け取り中のリンクです"
        else:
            return "未処理の状態です"
    else:
        return "エラーが発生しました"
