import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
BACKEND_URL = 'https://your-backend.onrender.com/api'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or 'User'

    try:
        response = requests.get(f'{BACKEND_URL}/points/{user_id}')
        data = response.json()
        points = data.get('points', 0)
    except Exception as e:
        logger.error(f'Error fetching points: {e}')
        points = 0

    mini_app_url = 'https://your-mini-app.vercel.app'
    keyboard = [
        [InlineKeyboardButton("فتح التطبيق المصغر", web_app={'url': mini_app_url})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"مرحبًا {user_name}!\nمعرفك: {user_id}\nنقاطك: {points}\nاضغط لفتح التطبيق المصغر.",
        reply_markup=reply_markup
    )

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.run_polling()

if __name__ == '__main__':
    main()
