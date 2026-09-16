import os
from threading import Thread
import google.generativeai as genai
from flask import Flask
import telebot
from telebot import types

# خواندن توکن‌ها از متغیرهای محیطی رندر
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = 8920570131  # آیدی ادمین شما

# تنظیمات هوش مصنوعی جمینای
if GEMINI_KEY:
  genai.configure(api_key=GEMINI_KEY)
  generation_model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TOKEN)

# وب‌سرور کوچک Flask برای زنده نگه داشتن بات روی رندر
app = Flask("")


@app.route("/")
def home():
  return "Uncle Butcher Bot is active 24/7! 🗿🚬"


def run_web():
  app.run(host="0.0.0.0", port=10000)


# دستور استارت بات
@bot.message_handler(commands=["start"])
def send_welcome(message):
  # اگر خودت (ادمین) بودی، پیام مخصوص ادمین رو بده
  if message.from_user.id == ADMIN_ID:
    bot.reply_to(
        message,
        "سلام داداش، خودِ ادمینی! ربات روی سرور رندر روشنه و داره مثل ساعت کار"
        " می‌کنه 🗿🚬🔥",
    )
  else:
    # اگر کاربر عادی بود، دکمه خرید اشتراک رو نشون بده
    markup = types.InlineKeyboardMarkup()
    sub_btn = types.InlineKeyboardButton(
        " خرید اشتراک گروه (۵۰ هزار تومان)", url="https://t.me/Az_Jaster"
    )
    markup.add(sub_btn)

    welcome_text = (
        "سلام! عمو بوچر هستم.. از خودت برام بگو 🗿🚬\n\nبرای فعال‌سازی و استفاده"
        " از امکانات ربات در گروه‌ها، می‌تونی اشتراک تهیه کنی."
    )
    bot.reply_to(message, welcome_text, reply_markup=markup)


# مدیریت پیام‌ها و هوش مصنوعی
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
  try:
    if generation_model and message.text:
      response = generation_model.generate_content(message.text)
      bot.reply_to(message, response.text)
  except Exception as e:
    print(f"Error: {e}")


if __name__ == "__main__":
  # راه‌اندازی سرور وب در پس‌زمینه
  t = Thread(target=run_web)
  t.start()

  # شروع به کار ربات تلگرام
  print("Uncle Butcher bot is polling...")
  bot.infinity_polling()