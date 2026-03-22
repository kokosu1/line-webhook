from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction
import os
from datetime import datetime

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))

# グループIDまたはユーザーID（LINEで送信先）
LINE_GROUP_ID = os.environ.get("LINE_GROUP_ID")

# LIFFのURL
LIFF_URL = os.environ.get("LIFF_URL")  # 例: https://liff.line.me/xxxxxxxxxx-xxxxxxxx


def send_shift_request(period: str):
    """シフト希望提出のメッセージを送信"""
    now = datetime.now()

    if period == "first":
        # 前半（1〜15日）：翌月分を送信
        if now.month == 12:
            target_year = now.year + 1
            target_month = 1
        else:
            target_year = now.year
            target_month = now.month + 1
        period_label = "前半（1〜15日）"
        liff_url = f"{LIFF_URL}?period=first&year={target_year}&month={target_month}"
    else:
        # 後半（16〜末日）：当月分を送信
        target_year = now.year
        target_month = now.month
        period_label = f"後半（16〜末日）"
        liff_url = f"{LIFF_URL}?period=second&year={target_year}&month={target_month}"

    message = TemplateSendMessage(
        alt_text=f"{target_year}年{target_month}月 {period_label} シフト希望提出",
        template=ButtonsTemplate(
            title=f"{target_month}月 シフト希望提出",
            text=f"{period_label}のシフト希望を入力してください！\n締め切りまでに送信をお願いします。",
            actions=[
                URIAction(
                    label="シフトを入力する",
                    uri=liff_url
                )
            ]
        )
    )

    line_bot_api.push_message(LINE_GROUP_ID, message)
    print(f"[Scheduler] {period_label} シフト提出リクエスト送信完了")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Tokyo")

    # 毎月22日 → 翌月前半（1〜15日）のシフト希望収集
    scheduler.add_job(
        lambda: send_shift_request("first"),
        CronTrigger(day=22, hour=9, minute=0),
        id="shift_first_half"
    )

    # 毎月8日 → 当月後半（16〜末日）のシフト希望収集
    scheduler.add_job(
        lambda: send_shift_request("second"),
        CronTrigger(day=8, hour=9, minute=0),
        id="shift_second_half"
    )

    scheduler.start()
    print("[Scheduler] 起動完了（22日・8日 午前9時に自動送信）")
    return scheduler
