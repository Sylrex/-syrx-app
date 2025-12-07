import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")          # هتحطه في Environment Variables على Render
BOT_USERNAME = os.getenv("BOT_USERNAME")    # مثال: SYRXReferralBot  (بدون @)
CHANNEL_USERNAME = "@SYRX_Meme_Official"

bot = telebot.TeleBot(BOT_TOKEN)

# Database
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, referrals INTEGER DEFAULT 0, username TEXT)''')
conn.commit()

def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.full_name

    args = message.text.split()[1] if len(message.text.split()) > 1 else None
    referrer_id = int(args) if args and args.isdigit() else None

    # Add user if new
    c.execute("INSERT OR IGNORE INTO users (user_id, username, referrals) VALUES (?, ?, 0)", (user_id, username))
    conn.commit()

    # Count referral
    if referrer_id and referrer_id != user_id:
        c.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id = ?", (referrer_id,))
        conn.commit()

    # Check channel membership
    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel", url=f"https://t.me/SYRX_Meme_Official"))
        markup.add(InlineKeyboardButton("I Joined ✅", callback_data="check_join"))
        bot.send_message(message.chat.id,
                         "You must join the channel first to get your referral link!",
                         reply_markup=markup)
        return

    # User is member → give link
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    c.execute("SELECT referrals FROM users WHERE user_id = ?", (user_id,))
    refs = c.fetchone()[0]

    bot.send_message(message.chat.id,
                     f"Welcome!\n\n"
                     f"Your referral link:\n`{ref_link}`\n\n"
                     f"You have {refs} referrals\n"
                     f"Use /top to see leaderboard",
                     parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_member(call.from_user.id):
        ref_link = f"https://t.me/{BOT_USERNAME}?start={call.from_user.id}"
        c.execute("SELECT referrals FROM users WHERE user_id = ?", (call.from_user.id,))
        refs = c.fetchone()[0]
        bot.edit_message_text("Successfully verified!\n\n"
                              f"Your link:\n`{ref_link}`\n\n"
                              f"Referrals: {refs}\n"
                              f"Use /top for leaderboard",
                              call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "You are not in the channel yet!", show_alert=True)

@bot.message_handler(commands=['top'])
def top(message):
    c.execute("SELECT user_id, username, referrals FROM users ORDER BY referrals DESC LIMIT 10")
    rows = c.fetchall()
    if not rows:
        bot.send_message(message.chat.id, "No referrals yet.")
        return

    text = "*Top 10 Referrers*\n\n"
    for i, (uid, name, refs) in enumerate(rows, 1):
        text += f"{i}. {name or uid} → {refs} referrals\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

print("Bot is running...")
bot.polling(none_stop=True)
