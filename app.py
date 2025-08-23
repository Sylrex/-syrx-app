import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import requests

# إعداد التسجيل (logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# استبدل هذا برمز API Token الخاص بك من BotFather
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'

# رابط الخادم الخلفي (Backend API)
BACKEND_URL = 'https://your-backend.onrender.com/api'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or 'User'

    # جلب النقاط من الخادم
    try:
        response = requests.get(f'{BACKEND_URL}/points/{user_id}')
        data = response.json()
        points = data.get('points', 0)
    except Exception as e:
        logger.error(f'Error fetching points: {e}')
        points = 0

    # إنشاء رابط التطبيق المصغر
    mini_app_url = f'https://your-mini-app-url.com'  # استبدل برابط التطبيق المصغر الخاص بك
    
    # إنشاء لوحة مفاتيح مع زر لفتح التطبيق المصغر
    keyboard = [
        [InlineKeyboardButton("فتح التطبيق المصغر", web_app={'url': mini_app_url})],
        [InlineKeyboardButton("عرض المهام", callback_data='tasks')],
        [InlineKeyboardButton("رابط الإحالة", callback_data='referrals')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # إرسال رسالة ترحيب
    await update.message.reply_text(
        f"مرحبًا {user_name}!\nمعرفك: {user_id}\nنقاطك: {points}\nاضغط لفتح التطبيق المصغر أو اختر أمرًا.",
        reply_markup=reply_markup
    )

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    # جلب حالة تسجيل الدخول اليومي
    try:
        response = requests.get(f'{BACKEND_URL}/daily-login/{user_id}')
        data = response.json()
        daily_login_text = "تسجيل الدخول اليومي: تم" if not data.get('can_login', True) else "تسجيل الدخول اليومي: متاح (+10 نقاط)"
    except Exception as e:
        logger.error(f'Error checking daily login: {e}')
        daily_login_text = "تسجيل الدخول اليومي: متاح (+10 نقاط)"

    # قائمة المهام
    tasks_text = (
        "📋 المهام المتاحة:\n"
        "1. متابعة حساب X: +5 نقاط\n"
        "2. متابعة صفحة فيسبوك: +5 نقاط\n"
        "3. متابعة قناة يوتيوب 1: +5 نقاط\n"
        "4. متابعة قناة يوتيوب 2: +5 نقاط\n"
        f"5. {daily_login_text}\n"
        "6. ربط محفظة TON: +10 نقاط"
    )
    await update.message.reply_text(tasks_text)

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    # جلب لوحة المتصدرين
    try:
        response = requests.get(f'{BACKEND_URL}/leaderboard')
        data = response.json()
        leaderboard = "\n".join([f"#{i+1} User{item['user_id']} - {item['points']} نقاط" for i, item in enumerate(data[:5])])
    except Exception as e:
        logger.error(f'Error fetching leaderboard: {e}')
        leaderboard = "غير متاح حاليًا"

    await update.message.reply_text(
        f"🔗 رابط الإحالة الخاص بك:\n{ref_link}\n\n🏆 أفضل 5 متصدرين:\n{leaderboard}"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'tasks':
        await tasks(update, context)
    elif query.data == 'referrals':
        await referrals(update, context)

def main() -> None:
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('tasks', tasks))
    application.add_handler(CommandHandler('referrals', referrals))
    application.add_handler(CallbackQueryHandler(button_callback))

    # بدء البوت
    application.run_polling()

if __name__ == '__main__':
    main()
