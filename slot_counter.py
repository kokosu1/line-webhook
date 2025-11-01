import math
from fastapi import FastAPI, Request

app = FastAPI()

# ===============================
# データ定義
# ===============================
stats = {
    "total": 0, "grape": 0, "big": 0, "reg": 0,
    "miss": 0, "replay": 0,
    "mode": "idle",     # idle / input_info / playing
    "machine": None,    # 機種名
    "setting_data": {}  # 設定ごとの確率表
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

    # --- スタート ---
    if text == "スタート":
        stats["mode"] = "input_info"
        reply_text = "🎰 打つ台の名前を教えてください（例：マイジャグラーV）"

    # --- 台情報入力モード ---
    elif stats["mode"] == "input_info":
        machine_name = text.replace("台", "").strip()
        if machine_name in machine_info:
            stats["machine"] = machine_name
            stats["setting_data"] = machine_info[machine_name]
            stats["mode"] = "playing"

            info_text = "📊 参考設定データ\n"
            for s, v in stats["setting_data"].items():
                info_text += f"{s}: 合算 1/{1/v['合算']:.1f} / ぶどう 1/{1/v['ぶどう']:.2f}\n"
            reply_text = f"✅ {machine_name} を選択しました！\n\n{info_text}\n\nカウント開始できます。"
        else:
            reply_text = "⚠️ その機種はデータがありません。『マイジャグラーV』などを入力してね。"

    # --- プレイ中（カウンター機能）---
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

        # 結果表示
        elif text in ["カウント", "結果", "計算"]:
            grape_rate = stats["total"]/stats["grape"] if stats["grape"] else None
            bonus_rate = stats["total"]/(stats["big"]+stats["reg"]) if (stats["big"]+stats["reg"]) else None
            miss_rate = stats["total"]/stats["miss"] if stats["miss"] else None

            # 設定推測ロジック
            setting_guess = "−"
            if grape_rate and bonus_rate and stats["setting_data"]:
                diffs = {}
                for s, v in stats["setting_data"].items():
                    diff = abs((1/v["合算"]) - (1/bonus_rate)) + abs((1/v["ぶどう"]) - (1/grape_rate))
                    diffs[s] = diff
                setting_guess = min(diffs, key=diffs.get)

            reply_text = (
                f"🎰 現在の集計（{stats['machine']}）\n"
                f"総回転数：{stats['total']}\n"
                f"🍇ぶどう確率：{'1/'+str(round(grape_rate,2)) if grape_rate else '−'}\n"
                f"❌ハズレ確率：{'1/'+str(round(miss_rate,2)) if miss_rate else '−'}\n"
                f"🎯ボーナス合算：{'1/'+str(round(bonus_rate,2)) if bonus_rate else '−'}\n"
                f"BIG：{stats['big']} / REG：{stats['reg']}\n\n"
                f"🔍推定設定：{setting_guess}"
            )

        elif text == "リセット":
            for key in ["total","grape","big","reg","miss","replay"]:
                stats[key] = 0
            reply_text = "🧹 データをリセットしました。"
        else:
            reply_text = (
                "🕹 コマンド一覧：\n"
                "ぶどう / ハズレ / リプレイ / BIG / REG\n"
                "カウント → 集計表示\n"
                "リセット → 全データ初期化"
            )

    # --- 何もしてない状態 ---
    else:
        reply_text = "💬『スタート』で台を選んでカウントを始めてください！"

    # 返信（LINE SDKのsend_messageに置き換えて）
    reply_message(reply_token, reply_text)
    return "OK"