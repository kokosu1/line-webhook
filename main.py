import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# OpenWeatherMap APIキー（自分のAPIキーに置き換えてください）
API_KEY = 'dd9f6e2b4116d6c124be61d261da444e'

class WebhookData(BaseModel):
    type: str
    text: str

@app.post("/webhook")
async def webhook(data: WebhookData):
    user_message = data.text.strip()  # ユーザーから送られたメッセージを取得

    if "天気" in user_message:
        # ユーザーが「天気」と言った場合、天気情報を取得
        city = "Tokyo"  # デフォルトで東京を設定（必要に応じて変更）
        weather_info = get_weather(city)
        return {"status": "success", "weather": weather_info}
    else:
        return {"status": "failure", "message": "天気情報をリクエストしてください。"}

def get_weather(city: str):
    # OpenWeatherMap APIを使って天気情報を取得
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        # 天気情報が正常に取得できた場合
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"現在の天気は {weather} で、気温は {temp}°C です。"
    else:
        return "天気情報の取得に失敗しました。"
