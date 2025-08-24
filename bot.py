import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = 'YOUR_BOT_TOKEN'  # استبدل بتوكن البوت من @BotFather
WEB_APP_URL = 'YOUR_WEB_APP_URL'  # استبدل بعنوان الويب أب (مثل https://your-app.onrender.com)
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(text="Open Mini App", web_app=WebAppInfo(url=WEB_APP_URL))
    markup.add(web_app_button)
    bot.send_message(message.chat.id, "Welcome! Click below to open the Mini App.", reply_markup=markup)

if __name__ == '__main__':
    bot.polling(none_stop=True)
