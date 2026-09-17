import io
import os
import time
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


# تنظیم روی مدل جدید و بهینه gemini-3.5-flash
if GEMINI_KEY:
  genai.configure(api_key=GEMINI_KEY)
  chat_model = genai.GenerativeModel("gemini-3.5-flash")
else:
  chat_model = None

bot = telebot.TeleBot(TOKEN) if TOKEN else None

# لیست گروه‌هایی که برای آن‌ها اشتراک رایگان فعال شده است
AUTHORIZED_GROUPS = set()

if bot:

  @bot.message_handler(commands=["start"])
  def send_welcome(message):
    if message.chat.type == "private":
      if message.from_user.id == ADMIN_ID:
        bot.reply_to(
            message,
            "سلام داداش، ادمین بزرگ! ربات با مدل gemini-3.5-flash و تمام"
            " قابلیت‌های مدیریتی روشنه 🗿🚬🔥\n\nدستورات ادمین در پیوی:\n/free"
            " <آیدی_گروه> - رایگان کردن گروه\n/leave <آیدی_گروه> - خروج ربات از"
            " گروه",
        )
      else:
        markup = types.InlineKeyboardMarkup()
        sub_btn = types.InlineKeyboardButton(
            " خرید اشتراک گروه (۵۰ هزار تومان)", url="https://t.me/Az_Jaster"
        )
        markup.add(sub_btn)
        bot.reply_to(
            message,
            "سلام! عمو بوچر هستم.. برای استفاده از ربات در گروه باید اشتراک"
            " تهیه کنید 🗿🚬",
            reply_markup=markup,
        )
    else:
      bot.reply_to(
          message,
          "عمو بوچر تو این گروه فعاله! 🗿🚬\nبرای ساخت عکس /draw رو بزن.",
      )

  # --- کنترل گروه‌ها از طریق پیوی ادمین ---
  @bot.message_handler(
      commands=["free"],
      func=lambda m: m.chat.type == "private" and m.from_user.id == ADMIN_ID,
  )
  def make_group_free(message):
    parts = message.text.split()
    if len(parts) < 2:
      bot.reply_to(
          message,
          "لطفاً آیدی عددی گروه را وارد کن!\nمثال: `/free -100123456789`",
          parse_mode="Markdown",
      )
      return
    try:
      chat_id = int(parts[1])
      AUTHORIZED_GROUPS.add(chat_id)
      bot.reply_to(
          message,
          f"✅ گروه با آیدی `{chat_id}` رایگان شد و ربات خدمات می‌دهد!",
          parse_mode="Markdown",
      )
    except ValueError:
      bot.reply_to(message, "❌ آیدی گروه باید یک عدد صحیح باشد.")

  @bot.message_handler(
      commands=["leave", "حذف"],
      func=lambda m: m.chat.type == "private" and m.from_user.id == ADMIN_ID,
  )
  def leave_group(message):
    parts = message.text.split()
    if len(parts) < 2:
      bot.reply_to(
          message,
          "لطفاً آیدی عددی گروه را وارد کن!\nمثال: `/leave -100123456789`",
          parse_mode="Markdown",
      )
      return
    try:
      chat_id = int(parts[1])
      bot.leave_chat(chat_id)
      AUTHORIZED_GROUPS.discard(chat_id)
      bot.reply_to(
          message, f"🏃‍♂️ ربات با موفقیت از گروه `{chat_id}` لف داد!", parse_mode="Markdown"
      )
    except Exception as e:
      bot.reply_to(message, f"❌ خطا در خروج از گروه:\n{e}")

  # --- دستورات مدیریت گروه (ریم زدن، بن، میوت) ---
  def is_user_admin(message):
    if message.from_user.id == ADMIN_ID:
      return True
    if message.chat.type in ["group", "supergroup"]:
      try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ["administrator", "creator"]
      except Exception:
        return False
    return False

  @bot.message_handler(commands=["kick"])
  def kick_user(message):
    if message.chat.type not in ["group", "supergroup"]:
      return
    if not is_user_admin(message):
      bot.reply_to(message, "❌ این دستور فقط مخصوص ادمین‌هاست!")
      return
    if not message.reply_to_message:
      bot.reply_to(message, "لطفاً روی پیام کاربری که می‌خواهی کیک کنی ریپلای بزن!")
      return

    user_id = message.reply_to_message.from_user.id
    try:
      bot.ban_chat_member(message.chat.id, user_id, until_date=time.time() + 30)
      bot.reply_to(
          message,
          f"👢 کاربر {message.reply_to_message.from_user.first_name} از گروه"
          " کیک شد!",
      )
    except Exception as e:
      bot.reply_to(message, f"❌ خطا در کیک کردن: {e}")

  @bot.message_handler(commands=["ban"])
  def ban_user(message):
    if message.chat.type not in ["group", "supergroup"]:
      return
    if not is_user_admin(message):
      bot.reply_to(message, "❌ این دستور فقط مخصوص ادمین‌هاست!")
      return
    if not message.reply_to_message:
      bot.reply_to(message, "لطفاً روی پیام کاربری که می‌خواهی بن کنی ریپلای بزن!")
      return

    user_id = message.reply_to_message.from_user.id
    try:
      bot.ban_chat_member(message.chat.id, user_id)
      bot.reply_to(
          message,
          f"🔨 کاربر {message.reply_to_message.from_user.first_name} بن شد!",
      )
    except Exception as e:
      bot.reply_to(message, f"❌ خطا در بن کردن: {e}")

  @bot.message_handler(commands=["mute"])
  def mute_user(message):
    if message.chat.type not in ["group", "supergroup"]:
      return
    if not is_user_admin(message):
      bot.reply_to(message, "❌ این دستور فقط مخصوص ادمین‌هاست!")
      return
    if not message.reply_to_message:
      bot.reply_to(
          message, "لطفاً روی پیام کاربری که می‌خواهی میوت کنی ریپلای بزن!"
      )
      return

    user_id = message.reply_to_message.from_user.id
    try:
      bot.restrict_chat_member(
          message.chat.id,
          user_id,
          can_send_messages=False,
          until_date=time.time() + 3600,
      )
      bot.reply_to(
          message,
          f"🔇 کاربر {message.reply_to_message.from_user.first_name} برای یک"
          " ساعت میوت شد!",
      )
    except Exception as e:
      bot.reply_to(message, f"❌ خطا در میوت کردن: {e}")

  # --- ساخت تصویر با دستور /draw ---
  @bot.message_handler(commands=["draw", "img", "photo"])
  def make_image(message):
    if message.chat.type in ["group", "supergroup"]:
      if (
          message.from_user.id != ADMIN_ID
          and message.chat.id not in AUTHORIZED_GROUPS
      ):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                " خرید اشتراک گروه (۵۰ هزار تومان)", url="https://t.me/Az_Jaster"
            )
        )
        bot.reply_to(
            message,
            "⚠️ این گروه اشتراک فعال ندارد!\nبرای استفاده از ربات در گروه باید"
            " اشتراک تهیه کنید.",
            reply_markup=markup,
        )
        return

    prompt = (
        message.text.replace("/draw", "")
        .replace("/img", "")
        .replace("/photo", "")
        .strip()
    )
    if not prompt:
      bot.reply_to(
          message,
          "لطفاً توصیف عکس را بنویس:\nمثال: `/draw a cyber cat`",
          parse_mode="Markdown",
      )
      return

    status_msg = bot.reply_to(
        message, "🎨 عمو بوچر داره عکس رو می‌کشه... چند لحظه!"
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

  # --- چت هوش مصنوعی ---
  @bot.message_handler(func=lambda message: True)
  def handle_messages(message):
    if message.chat.type in ["group", "supergroup"]:
      if (
          message.from_user.id != ADMIN_ID
          and message.chat.id not in AUTHORIZED_GROUPS
      ):
        return  # در گروه‌های غیرمجاز برای جلوگیری از اسپم پاسخ نمی‌دهد

    try:
      if chat_model and message.text:
        response = chat_model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
      if "429" in str(e) or "ResourceExhausted" in str(e):
        bot.reply_to(
            message,
            "عصبانی نشو داداش! سهمیه مدل موقتاً پر شد، چند ثانیه صبر کن دوباره"
            " پیام بده 🗿🚬",
        )
      else:
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

    print("Uncle Butcher bot started successfully with gemini-3.5-flash!")
    bot.infinity_polling()