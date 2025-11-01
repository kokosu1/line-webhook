import math
from fastapi import FastAPI, Request

app = FastAPI()

# ===============================
# データ構造
# ===============================
stats = {
    "total": 0, "grape": 0, "big": 0, "reg": 0,
    "miss": 0, "replay": 0,
    "mode": "idle",     # 現在の会話状態
    "machine": None,    # 機種名
    "setting_data": {}, # 機種ごとの設定確率
}

# 機種データ例
machine_info = {
    "マイジャグラーv": {
        "設定1": {"合算": 1/172.5, "ぶどう": 1/6.35},
        "設定2": {"合算": 1/168.5, "ぶどう": 1/6.30},
        "設定3": {"合算": 1/164.5, "ぶどう": 1/6.25},
        "設定4": {"合算": 1/160.5, "ぶどう": 1/6.20},
        "設定5": {"合算": 1/156.5, "ぶどう": 1/6.15},
        "設定6": {"合算": 1/150.5, "ぶどう": 1/6.10},
    },
    "アイムジャグラー": {
        "設定1": {"合算": 1/176.2, "ぶどう": 1/6.49},
        "設定2": {"合算": 1/172.4, "ぶどう": 1/6.45},
        "設定3": {"合算": 1/168.5, "ぶどう": 1/6.40},
        "設定4": {"合算": 1/164.5, "ぶどう": 1/6.35},
        "設定5": {"合算": 1/160.5, "ぶどう": 1/6.30},
        "設定6": {"合算": 1/156.5, "ぶどう": 1/6.25},
    },
}

# ===============================
# LINE受信処理
# ===============================
@app.post("/callback")
async def callback(request: Request):
    body = await request.json()
    event = body["events"][0]
    text = event["message"]["text"].strip().lower()
    reply_token = event["replyToken"]

    reply_text = ""

    # --- スタート（リセットして台質問）---
    if text == "スタート":
        stats.update({
            "total": 0, "grape": 0, "big": 0, "reg": 0,
            "miss": 0, "replay": 0,
            "machine": None, "setting_data": {},
            "mode": "ask_machine"
        })
        reply_text = "🎰 なんの台ですか？（例：マイジャグラーV / アイムジャグラー）"

    # --- 台名入力 ---
    elif stats["mode"] == "ask_machine":
        if text in machine_info:
            stats["machine"] = text
            stats["setting_data"] = machine_info[text]
            stats["mode"] = "ask_total"
            reply_text = f"🧮 {text}ですね。総回転数を入力してください。"
        else:
            reply_text = "⚠️ その台データはまだ登録されていません。マイジャグラーV か アイムジャグラー で試してみてください。"

    # --- 総回転数入力 ---
    elif stats["mode"] == "ask_total":
        if text.isdigit():
            stats["total"] = int(text)
            stats["mode"] = "ask_big"
            reply_text = "🎯 BIG回数を入力してください。"
        else:
            reply_text = "⚠️ 数字で入力してください（例：2350）"

    # --- BIG入力 ---
    elif stats["mode"] == "ask_big":
        if text.isdigit():
            stats["big"] = int(text)
            stats["mode"] = "ask_reg"
            reply_text = "💡 REG回数を入力してください。"
        else:
            reply_text = "⚠️ 数字で入力してください。"

    # --- REG入力 ---
    elif stats["mode"] == "ask_reg":
        if text.isdigit():
            stats["reg"] = int(text)
            stats["mode"] = "confirm"

            total = stats["total"]
            big = stats["big"]
            reg = stats["reg"]
            combined = big + reg
            bonus_rate = total / combined if combined > 0 else 0

            # 設定推測
            guess = "−"
            diffs = {}
            for s, v in stats["setting_data"].items():
                diff = abs((1/v["合算"]) - (1/bonus_rate)) if bonus_rate else 999
                diffs[s] = diff
            guess = min(diffs, key=diffs.get)

            reply_text = (
                f"✅ 台データ確認\n"
                f"機種：{stats['machine']}\n"
                f"総回転数：{total}\n"
                f"BIG：{big} / REG：{reg}\n"
                f"推定設定：{guess}\n\n"
                f"この台でスタートしますか？（はい / いいえ）"
            )
        else:
            reply_text = "⚠️ 数字で入力してください。"

    # --- 確認 ---
    elif stats["mode"] == "confirm":
        if text == "はい":
            stats["mode"] = "playing"
            reply_text = (
                f"🎰 {stats['machine']}でカウント開始します！\n"
                f"『ぶどう』『BIG』『REG』『ハズレ』『リプレイ』など送ってください。"
            )
        else:
            stats["mode"] = "idle"
            reply_text = "キャンセルしました。『スタート』でやり直せます。"

    # --- カウントモード ---
    elif stats["mode"] == "playing":
        if text == "ぶどう":
            stats["grape"] += 1
            stats["total"] += 1
            reply_text = "🍇 ぶどうカウント！"
        elif text == "big":
            stats["big"] += 1
            stats["total"] += 1
            reply_text = "🎉 BIGカウント！"
        elif text == "reg":
            stats["reg"] += 1
            stats["total"] += 1
            reply_text = "💡 REGカウント！"
        elif text == "ハズレ":
            stats["miss"] += 1
            stats["total"] += 1
            reply_text = "❌ ハズレカウント！"
        elif text == "リプレイ":
            stats["replay"] += 1
            stats["total"] += 1
            reply_text = "🔁 リプレイカウント！"
        elif text in ["カウント", "結果"]:
            grape_rate = stats["total"]/stats["grape"] if stats["grape"] else None
            bonus_rate = stats["total"]/(stats["big"]+stats["reg"]) if (stats["big"]+stats["reg"]) else None

            guess = "−"
            if grape_rate and bonus_rate:
                diffs = {}
                for s, v in stats["setting_data"].items():
                    diff = abs((1/v["合算"]) - (1/bonus_rate)) + abs((1/v["ぶどう"]) - (1/grape_rate))
                    diffs[s] = diff
                guess = min(diffs, key=diffs.get)

            reply_text = (
                f"📊 現在の状況\n"
                f"総回転数：{stats['total']}\n"
                f"🍇ぶどう確率：{'1/'+str(round(grape_rate,2)) if grape_rate else '−'}\n"
                f"🎯ボーナス合算：{'1/'+str(round(bonus_rate,2)) if bonus_rate else '−'}\n"
                f"BIG：{stats['big']} / REG：{stats['reg']}\n"
                f"🔍推定設定：{guess}"
            )
        else:
            reply_text = "🕹 カウント中です。『カウント』で集計を表示します。"

    # --- 初期状態 ---
    else:
        reply_text = "💬 『スタート』で台選択から始められます！"

    # 返信関数呼び出し（あなたの環境用に）
    reply_message(reply_token, reply_text)
    return "OK"