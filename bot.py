import io
import os
from threading import Thread
from flask import Flask
import google.generativeai as genai
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = 8920570131

app = Flask("")


@app.route("/")
def home():
  return "Uncle Butcher Bot is active 24/7! 🗿🚬"


def run_web():
  app.run(host="0.0.0.0", port=10000)


# تنظیم مستقیم و تمیز جمینای
if GEMINI_KEY:
  genai.configure(api_key=GEMINI_KEY)
  chat_model = genai.GenerativeModel("gemini-1.5-flash")
else:
  chat_model = None

bot = telebot.TeleBot(TOKEN) if TOKEN else None

if bot:

  @bot.message_handler(commands=["start"])
  def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
      bot.reply_to(
          message,
          "سلام داداش، خودِ ادمینی! ربات با کلید سالم و مدل اصلی روشنه 🗿🚬🔥",
      )
    else:
      markup = types.InlineKeyboardMarkup()
      sub_btn = types.InlineKeyboardButton(
          " خرید اشتراک گروه (۵۰ هزار تومان)", url="https://t.me/Az_Jaster"
      )
      markup.add(sub_btn)
      bot.reply_to(
          message,
          "سلام! عمو بوچر هستم.. از خودت برام بگو 🗿🚬\n\nبرای ساخت عکس دستور"
          " /draw رو به همراه توصیفش بفرست.",
          reply_markup=markup,
      )

  # دستور ساخت عکس (/draw یا /img)
  @bot.message_handler(commands=["draw", "img", "photo"])
  def make_image(message):
    prompt = (
        message.text.replace("/draw", "")
        .replace("/img", "")
        .replace("/photo", "")
        .strip()
    )
    if not prompt:
      bot.reply_to(
          message,
          "لطفاً بعد از دستور /draw توصیف عکس رو بنویس!\nمثال: `/draw a"
          " realistic cyberpunk city`",
          parse_mode="Markdown",
      )
      return

    status_msg = bot.reply_to(
        message, "🎨 در حال ساخت عکس... چند لحظه صبر کن!"
    )
    try:
      result = genai.ImageGenerationModel("imagen-3.0-generate-002").generate_images(
          prompt=prompt, number_of_images=1, aspect_ratio="1:1"
      )
      for img in result.images:
        image_bytes = io.BytesIO()
        img._pil_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        bot.send_photo(
            message.chat.id,
            photo=image_bytes,
            caption=f"🖼 تصویر ساخته شده برای:\n`{prompt}`",
            reply_to_message_id=message.message_id,
            parse_mode="Markdown",
        )
        bot.delete_message(
            chat_id=message.chat.id, message_id=status_msg.message_id
        )
    except Exception as e:
      bot.edit_message_text(
          f"❌ خطای ساخت تصویر:\n{e}",
          chat_id=message.chat.id,
          message_id=status_msg.message_id,
      )

  # پاسخ به چت‌های متنی
  @bot.message_handler(func=lambda message: True)
  def handle_messages(message):
    try:
      if chat_model and message.text:
        response = chat_model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
      bot.reply_to(message, f"❌ خطای هوش مصنوعی:\n{e}")

if __name__ == "__main__":
  t = Thread(target=run_web)
  t.daemon = True
  t.start()

  if bot:
    try:
      bot.remove_webhook(drop_pending_updates=True)
    except Exception:
      pass

    print("Uncle Butcher bot started successfully!")
    bot.infinity_polling()