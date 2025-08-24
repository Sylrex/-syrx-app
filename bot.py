import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL')  # يجب أن يكون: https://syrx.onrender.com/SYRXApp

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(
        text="Open SYRX Mini App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    markup.add(web_app_button)
    bot.send_message(message.chat.id, "اضغط لفتح التطبيق:", reply_markup=markup)

bot.polling(none_stop=True)
