def get_weather(city: str):
    city_map = {
        "東京": "Tokyo",
        "大阪": "Osaka",
        "名古屋": "Nagoya",
        "福岡": "Fukuoka",
        "札幌": "Sapporo",
        "横浜": "Yokohama"
    }

    for jp, en in city_map.items():
        if jp in city:
            city = en
            break

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    res = requests.get(url)

    if res.status_code == 200:
        data = res.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        # 判定して変える
        if "晴" in weather or "sun" in weather:
            message = f"{city}は晴れてるよ！気温は{temp}℃だよ♪\nいいお天気〜おでかけしよう！"
            sticker = ("11537", "52002734")
        elif "曇" in weather or "cloud" in weather:
            message = f"{city}はくもりだよ〜！気温は{temp}℃。\nちょっと暗いけど元気出してねっ！"
            sticker = ("11537", "52002740")
        elif "雨" in weather or "rain" in weather:
            message = f"{city}は雨だよ…気温は{temp}℃！\n傘忘れないでね☂️"
            sticker = ("11537", "52002745")
        elif "雪" in weather or "snow" in weather:
            message = f"{city}は雪が降ってるみたい！気温は{temp}℃だよ〜！\nあったかくしてね！"
            sticker = ("11537", "52002750")
        else:
            message = f"{city}の天気は「{weather}」、気温は{temp}℃だよ！"
            sticker = (None, None)

        return message, sticker[0], sticker[1]
    else:
        return "天気情報が見つからなかったみたい…ごめんね！", None, None
