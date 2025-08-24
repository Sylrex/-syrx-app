import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
import os

# جلب المتغيرات من البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL')

if not BOT_TOKEN or not WEB_APP_URL:
    raise ValueError("BOT_TOKEN or WEB_APP_URL not set in environment variables")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(text="Open Mini App", web_app=WebAppInfo(url=WEB_APP_URL))
    markup.add(web_app_button)
    bot.send_message(message.chat.id, "Welcome! Click below to open the Mini App.", reply_markup=markup)

if __name__ == '__main__':
    bot.polling(none_stop=True)
