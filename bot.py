import os
from threading import Thread
import google.generativeai as genai
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = 8920570131

if GEMINI_KEY:
  genai.configure(api_key=GEMINI_KEY)
  # استفاده از نام مدل استاندارد و پایدار
  generation_model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TOKEN)
app = Flask("")


@app.route("/")
def home():
  return "Uncle Butcher Bot is active 24/7! 🗿🚬"


def run_web():
  app.run(host="0.0.0.0", port=10000)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  if message.from_user.id == ADMIN_ID:
    bot.reply_to(
        message,
        "سلام داداش، خودِ ادمینی! ربات روی سرور رندر روشنه و داره مثل ساعت کار"
        " می‌کنه 🗿🚬🔥",
    )
  else:
    markup = types.InlineKeyboardMarkup()
    sub_btn = types.InlineKeyboardButton(
        " خرید اشتراک گروه (۵۰ هزار تومان)", url="https://t.me/Az_Jaster"
    )
    markup.add(sub_btn)
    bot.reply_to(
        message,
        "سلام! عمو بوچر هستم.. از خودت برام بگو 🗿🚬",
        reply_markup=sub_btn,
    )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
  try:
    if generation_model and message.text:
      response = generation_model.generate_content(message.text)
      bot.reply_to(message, response.text)
  except Exception as e:
    bot.reply_to(message, f"❌ خطای هوش مصنوعی:\n{e}")


if __name__ == "__main__":
  t = Thread(target=run_web)
  t.start()
  bot.infinity_polling()