import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import os
import requests

# متغيرات البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL')  # مثال: https://syrx.onrender.com

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    # قراءة معلمة start إذا كانت موجودة
    start_payload = message.text.split()
    referrer_id = None
    if len(start_payload) > 1 and start_payload[1].startswith("ref_"):
        referrer_id = start_payload[1][4:]  # إزالة "ref_" للحصول على ID المحيل

    # تسجيل الإحالة على السيرفر
    if referrer_id and referrer_id != str(message.from_user.id):
        payload = {
            "referrer_id": referrer_id,
            "referred_id": str(message.from_user.id),
            "referred_name": message.from_user.first_name,
            "points": 0
        }
        try:
            resp = requests.post(f"{WEB_APP_URL}/referral", json=payload)
            print(f"Referral response: {resp.text}")
        except Exception as e:
            print(f"Error sending referral: {e}")

    # زر فتح التطبيق المصغر
    markup = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(
        text="Open SYRX Mini App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    markup.add(web_app_button)

    bot.send_message(
        chat_id=message.chat.id,
        text="اضغط لفتح التطبيق:",
        reply_markup=markup
    )

# تشغيل البوت
bot.polling(none_stop=True)
