# bot.py
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import httpx
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")              # من BotFather
WEBAPP_URL = os.getenv("WEBAPP_URL")            # رابط تطبيقك: https://<backend>.onrender.com/
BACKEND_API = os.getenv("BACKEND_API", WEBAPP_URL.rstrip("/"))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# حفظ إحالة في الخادم عندما يدخل المستخدم من /start ref_XXXX
async def save_referral(referrer_id: int, referred_id: int):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(f"{BACKEND_API}/api/referral/{referrer_id}",
                              json={"referred_id": referred_id})
    except Exception as e:
        log.warning("referral save failed: %s", e)

def build_open_app_kb() -> ReplyKeyboardMarkup:
    btn = KeyboardButton(
        text="افتح تطبيق SYRX",
        web_app=WebAppInfo(url=WEBAPP_URL)  # Telegram WebApp
    )
    return ReplyKeyboardMarkup([[btn]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = "مرحباً! هذا هو تطبيق SYRX المصغّر.\nاضغط الزر بالأسفل لفتح التطبيق."
    kb = build_open_app_kb()

    # دعم الإحالة عبر start payload: /start ref_12345
    if context.args:
        payload = " ".join(context.args)
        m = re.match(r"ref_(\d+)", payload)
        if m and
