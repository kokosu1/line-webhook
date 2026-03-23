# paypay.py
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

PAYPAY_AUTHORIZATION = os.getenv("PAYPAY_AUTHORIZATION")
PAYPAY_TOKEN = os.getenv("PAYPAY_TOKEN")

def accept_paypay_link(order_id, verification_code):
    url = "https://www.paypay.ne.jp/app/v2/p2p-api/acceptP2PSendMoneyLink"
    headers = {
        "Authorization": PAYPAY_AUTHORIZATION,
        "Content-Type": "application/json",
        "Origin": "https://www.paypay.ne.jp",
        "Referer": "https://www.paypay.ne.jp/app/p2p/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Cookie": f"token={PAYPAY_TOKEN}"
    }
    body = {
        "orderId": order_id,
        "verificationCode": verification_code,
        "deviceType": "WEB"
    }
    try:
        res = requests.post(url, headers=headers, json=body)
        print("PayPay response:", res.status_code, res.text)
        return res.status_code == 200 and res.json().get("resultStatus") == "SUCCESS"
    except Exception as e:
        print("PayPay error:", e)
        return False

def handle_paypay(text):
    # URLが含まれているか確認
    url_match = re.search(r'https://pay\.paypay\.ne\.jp\S+', text)

    if url_match:
        url = url_match.group(0)
        try:
            # リダイレクト先のURLを取得
            res = requests.get(url, allow_redirects=True)
            final_url = res.url

            # URLからorderId・verificationCodeを抽出
            order_id_match = re.search(r'orderId=([^&]+)', final_url)
            verification_match = re.search(r'verificationCode=([^&]+)', final_url)

            if order_id_match and verification_match:
                order_id = order_id_match.group(1)
                verification_code = verification_match.group(1)
                success = accept_paypay_link(order_id, verification_code)
                return "PayPay受け取り成功！💰" if success else "受け取り失敗しました。"
        except Exception as e:
            print("PayPay URL処理エラー:", e)
            return "PayPayリンクの処理に失敗しました。"

    # 旧形式（JSON）にも対応
    if "orderId" in text and "verificationCode" in text:
        try:
            order_id_match = re.search(r'"orderId"\s*:\s*"(\d+)"', text)
            verification_match = re.search(r'"verificationCode"\s*:\s*"([A-Za-z0-9]+)"', text)
            if order_id_match and verification_match:
                order_id = order_id_match.group(1)
                verification_code = verification_match.group(1)
                success = accept_paypay_link(order_id, verification_code)
                return "PayPay受け取り成功！💰" if success else "受け取り失敗しました。"
        except Exception as e:
            print("PayPay JSON処理エラー:", e)

    return None
