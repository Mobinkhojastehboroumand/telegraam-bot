import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os
import json
from datetime import datetime
import random
import jdatetime

# لاگ فقط برای خطاها
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)

# تنظیمات اولیه
TOKEN = "7964544115:AAGIbjFICKrlNy2zAdWhM32hsSg6k2exOtA"
ADMIN_ID = "@Mobinkhojastehboroumand"
STATS_FILE = "bot_stats.txt"
USERS_FILE = "users.json"

# پیام‌ها و داده‌ها
BUSINESS_TIPS = {
    "fa": [
        "✨ هر روز یه قدم کوچک به سمت موفقیت بردار!",
        "💎 بیزینس موفق با برنامه‌ریزی شروع می‌شه!",
        "👑 مشتری‌هات رو مثل طلا نگه دار!",
        "🌟 یه ایده جدید امروز امتحان کن!",
        "💡 نظم و خلاقیت، رمز برنده‌هاست!",
        "✨ از شکست نترس، درس بگیر!",
        "💎 فروش بیشتر با ارتباط بهتر!",
        "👑 امروز بهترین روز برای شروع یه پروژه جدیده!",
        "🌟 کیفیت کارتو بالا ببر، مشتری خودش میاد!",
        "💡 یه لبخند به مشتری، یه فروش بیشتر!"
    ],
    "en": [
        "✨ Take one small step toward success every day!",
        "💎 A successful business starts with planning!",
        "👑 Treat your customers like gold!",
        "🌟 Try a new idea today!",
        "💡 Order and creativity are the keys to winning!",
        "✨ Don’t fear failure, learn from it!",
        "💎 Better connections, more sales!",
        "👑 Today’s the best day to start a new project!",
        "🌟 Raise your work quality, customers will follow!",
        "💡 A smile to a customer, one more sale!"
    ]
}

MESSAGES = {
    "fa": {
        "welcome": "💎 درود {name} عزیز، به ربات هوشمند مبین خجسته برومند خوش آمدید! 👑\n\nشما حالا بخشی از دنیای خاص من هستید. آماده‌اید؟\n\nزبان خود را انتخاب کنید:",
        "menu_prompt": "💎 گزینه مورد نظر خود را از منوی زیر انتخاب کنید:",
        "option1": "✨ ثبت سفارش سایت + هدیه اپلیکیشن و سئو رایگان:\n🌐 https://proximainformatic.ir/form-2",
        "option2": "✨ مشاوره کسب‌وکار و خدمات ویژه:\n🌐 https://mobinkhojastehboroumand.ir/text-3/form-7",
        "option3": "👑 ارتباط با مبین خجسته برومند:\n📞 [09394448036](tel:09394448036)",
        "option4": "✨ اطلاعات بیشتر درباره مبین:\n🌐 وبگاه رسمی: https://mobinkhojastehboroumand.ir\n🌐 وبگاه کاری: https://proximainformatic.ir",
        "option5": "👑 صفحات رسمی مبین:\nاینستاگرام: https://instagram.com/mobin.khojaste.original\nآپارات: https://aparat.com/Mobinkhojastehboroumand\nویراستی: https://virasty.com/Mobinkhojastehboroumand\nتلگرام: https://t.me/Mobinkhojasteh\nیوتیوب: https://youtube.com/@mobinkhojastehboroumand\nایکس: https://x.com/Mobinkhojastehb?s=09",
        "option6": "💎 این قابلیت به‌زودی با شکوه اضافه می‌شود! 😉",
        "option_vip": "👑 خدمات VIP فقط برای اعضای ویژه:\nلطفاً با مبین تماس بگیرید!",
        "option_calendar": "📅 تقویم امروز:\nتاریخ میلادی: {gregorian_date} ({gregorian_day})\nتاریخ ایرانی: {jalali_date} ({jalali_day})\n✨ امروز روز موفقیت شماست!",
        "option_tip": "{tip}",
        "interactive": "💎 درود! چطور می‌تونم به شما خدمت کنم؟ سوال دارید یا از منو انتخاب کنید!",
        "error": "✨ اوه! یه خطای کوچک پیش اومد، لطفاً کمی صبر کنید یا دوباره تلاش کنید!",
        "profile": "👑 پروفایل شما {name} عزیز:\n💎 زبان: {lang}\n💎 عضویت: {join_date}\n💎 وضعیت: همیشه در اوج!",
        "vipcode_success": "🎉 تبریک! شما حالا عضو VIP هستید! منوی ویژه براتون باز شد!",
        "vipcode_fail": "✨ کد VIP اشتباه بود! لطفاً دوباره تلاش کنید یا با مبین تماس بگیرید!",
        "stats": "📊 آمار ربات برای {name}:\nبازدیدها: {users}\nکلیک‌ها:\n - ثبت سفارش سایت: {option1}\n - مشاوره کسب‌وکار: {option2}\n - تماس با مبین: {option3}\n - تارنما: {option4}\n - شبکه‌های اجتماعی: {option5}\n - قابلیت جدید: {option6}\nاعضای VIP: {vips}",
        "menu_list": "📋 فهرست امکانات ربات:\n\n1. ثبت سفارش سایت\n2. مشاوره کسب‌وکار\n3. تماس با مبین\n4. تارنما\n5. شبکه‌های اجتماعی\n6. قابلیت جدید\n7. تقویم\n8. نکته روزانه"
    },
    "en": {
        "welcome": "💎 Hello {name}, welcome to Mobin Khojasteh Boroumand's smart bot! 👑\n\nYou’re now part of my exclusive world. Ready?\n\nPlease select your language:",
        "menu_prompt": "💎 Pick an option from the menu below:",
        "option1": "✨ Order a website + free app and SEO:\n🌐 https://proximainformatic.ir/form-2",
        "option2": "✨ Business consultation and premium services:\n🌐 https://mobinkhojastehboroumand.ir/text-3/form-7",
        "option3": "👑 Contact Mobin Khojasteh Boroumand:\n📞 [09394448036](tel:09394448036)",
        "option4": "✨ More about Mobin:\n🌐 Official website: https://mobinkhojastehboroumand.ir\n🌐 Work website: https://proximainformatic.ir",
        "option5": "👑 Mobin’s official pages:\nInstagram: https://instagram.com/mobin.khojaste.original\nAparat: https://aparat.com/Mobinkhojastehboroumand\nVirasty: https://virasty.com/Mobinkhojastehboroumand\nTelegram: https://t.me/Mobinkhojasteh\nYouTube: https://youtube.com/@mobinkhojastehboroumand\nX: https://x.com/Mobinkhojastehb?s=09",
        "option6": "💎 This feature will soon shine brightly! 😉",
        "option_vip": "👑 VIP services for exclusive members:\nPlease contact Mobin!",
        "option_calendar": "📅 Today’s calendar:\nGregorian Date: {gregorian_date} ({gregorian_day})\nJalali Date: {jalali_date} ({jalali_day})\n✨ Today is your day to shine!",
        "option_tip": "{tip}",
        "interactive": "💎 Hello! How may I serve you? Ask me or choose from the menu!",
        "error": "✨ Oops! A slight glitch occurred, please wait or try again!",
        "profile": "👑 Your profile, dear {name}:\n💎 Language: {lang}\n💎 Joined: {join_date}\n💎 Status: Always at the top!",
        "vipcode_success": "🎉 Congrats! You’re now a VIP! Exclusive menu unlocked!",
        "vipcode_fail": "✨ Wrong VIP code! Please try again or contact Mobin!",
        "stats": "📊 Bot stats for {name}:\nVisits: {users}\nClicks:\n - Order Website: {option1}\n - Business Consultation: {option2}\n - Contact Mobin: {option3}\n - Websites: {option4}\n - Social Media: {option5}\n - New Feature: {option6}\nVIP Members: {vips}",
        "menu_list": "📋 Bot Features List:\n\n1. Order Website\n2. Business Consultation\n3. Contact Mobin\n4. Websites\n5. Social Media\n6. New Feature\n7. Calendar\n8. Daily Tip"
    }
}

MENU_BUTTONS = {
    "fa": [
        "💎 ثبت سفارش سایت", "✨ مشاوره کسب‌وکار", "👑 تماس با مبین",
        "🌐 تارنما", "📱 شبکه‌های اجتماعی", "💎 قابلیت جدید",
        "📅 تقویم", "💡 نکته روزانه"
    ],
    "en": [
        "💎 Order Website", "✨ Business Consultation", "👑 Contact Mobin",
        "🌐 Websites", "📱 Social Media", "💎 New Feature",
        "📅 Calendar", "💡 Daily Tip"
    ]
}

# توابع کمکی
def translate_message(message_key, lang, name="", **kwargs):
    if lang in MESSAGES:
        return MESSAGES[lang][message_key].format(name=name, **kwargs)
    return MESSAGES["fa"][message_key].format(name=name, **kwargs)  # پیش‌فرض فارسی

def format_message(text):
    return f"✨✨✨✨✨✨✨\n|    {text}    |\n✨✨✨✨✨✨✨"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False)

def update_stats(option=None):
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            f.write("Users: 0\nOption1: 0\nOption2: 0\nOption3: 0\nOption4: 0\nOption5: 0\nOption6: 0\nVIPs: 0\n")
    stats = {}
    with open(STATS_FILE, "r") as f:
        for line in f:
            key, value = line.strip().split(": ")
            stats[key] = int(value)
    if option:
        stats[option] += 1
    else:
        stats["Users"] += 1
    with open(STATS_FILE, "w") as f:
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
    return stats

# دستورات ربات
async def stats(update: Update, context) -> None:
    user = update.message.from_user.username
    if user != ADMIN_ID.replace("@", ""):
        await update.message.reply_text(format_message("✨ فقط ادمین می‌تونه آمار رو ببینه! 👑"))
        return
    stats = update_stats()
    message = translate_message("stats", "fa", name=ADMIN_ID, 
                               users=stats["Users"], option1=stats["Option1"], option2=stats["Option2"],
                               option3=stats["Option3"], option4=stats["Option4"], option5=stats["Option5"],
                               option6=stats["Option6"], vips=stats["VIPs"])
    await update.message.reply_text(format_message(message), parse_mode="Markdown")

async def profile(update: Update, context) -> None:
    user_id = str(update.message.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"lang": "fa", "join_date": "22 March 2025", "vip": False})
    lang_name = "فارسی" if user_data["lang"] == "fa" else "English"
    message = translate_message("profile", user_data["lang"], name=update.message.from_user.first_name,
                                lang=lang_name, join_date=user_data["join_date"])
    await update.message.reply_text(format_message(message))

async def vipcode(update: Update, context) -> None:
    user_id = str(update.message.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"lang": "fa", "join_date": "22 March 2025", "vip": False})
    code = " ".join(context.args).strip()
    if code == "mobinlux2025":
        user_data["vip"] = True
        users[user_id] = user_data
        save_users(users)
        update_stats("VIPs")
        await update.message.reply_text(format_message(translate_message("vipcode_success", user_data["lang"])))
    else:
        await update.message.reply_text(format_message(translate_message("vipcode_fail", user_data["lang"])))

async def start(update: Update, context) -> None:
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.first_name
    users = load_users()
    if user_id not in users:
        users[user_id] = {"lang": "fa", "join_date": datetime.now().strftime("%d %B %Y"), "vip": False, "last_tip_date": ""}
    save_users(users)
    update_stats()

    keyboard = [
        [InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa"), InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = translate_message("welcome", "fa", name=user_name)
    await update.message.reply_text(format_message(welcome_message), reply_markup=reply_markup)

async def menu(update: Update, context) -> None:
    user_id = str(update.message.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"lang": "fa", "join_date": "22 March 2025", "vip": False, "last_tip_date": ""})
    user_lang = user_data["lang"]
    
    # فهرست گزینه‌ها با شرط VIP
    message = translate_message("menu_list", user_lang)
    if user_data["vip"]:
        message += "\n9. " + ("خدمات VIP" if user_lang == "fa" else "VIP Services")
    
    # دکمه بازگشت
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو" if user_lang == "fa" else "🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(format_message(message), reply_markup=reply_markup)

async def interactive_response(update: Update, context) -> None:
    user_id = str(update.message.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"lang": "fa", "join_date": "22 March 2025", "vip": False, "last_tip_date": ""})
    message = translate_message("interactive", user_data["lang"])
    await update.message.reply_text(format_message(message))

async def main_menu(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"lang": "fa", "join_date": "22 March 2025", "vip": False, "last_tip_date": ""})
    user_lang = user_data["lang"]
    
    base_buttons = MENU_BUTTONS["fa"] if user_lang == "fa" else MENU_BUTTONS["en"]
    keyboard = [
        [InlineKeyboardButton(base_buttons[0], callback_data="option1")],
        [InlineKeyboardButton(base_buttons[1], callback_data="option2")],
        [InlineKeyboardButton(base_buttons[2], callback_data="option3")],
        [InlineKeyboardButton(base_buttons[3], callback_data="option4")],
        [InlineKeyboardButton(base_buttons[4], callback_data="option5")],
        [InlineKeyboardButton(base_buttons[5], callback_data="option6")],
        [InlineKeyboardButton(base_buttons[6], callback_data="option_calendar")],
        [InlineKeyboardButton(base_buttons[7], callback_data="option_tip")]
    ]
    if user_data["vip"]:
        keyboard.append([InlineKeyboardButton("👑 خدمات VIP", callback_data="option_vip")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    menu_prompt = translate_message("menu_prompt", user_lang)
    await query.edit_message_text(format_message(menu_prompt), reply_markup=reply_markup)

def back_button(user_lang):
    text = "🔙 بازگشت به منو" if user_lang == "fa" else "🔙 Back to Menu"
    return [InlineKeyboardButton(text, callback_data="menu")]

async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"lang": "fa", "join_date": "22 March 2025", "vip": False, "last_tip_date": ""})
    user_lang = user_data["lang"]

    if query.data.startswith("lang_"):
        lang = query.data.split("_")[1]
        user_data["lang"] = lang
        users[user_id] = user_data
        save_users(users)
        await main_menu(update, context)
        return

    if query.data == "menu":
        await main_menu(update, context)
        return

    option_map = {"option1": "Option1", "option2": "Option2", "option3": "Option3", 
                  "option4": "Option4", "option5": "Option5", "option6": "Option6"}
    if query.data in option_map:
        update_stats(option_map[query.data])

    if query.data == "option1":
        message = translate_message("option1", user_lang)
    elif query.data == "option2":
        message = translate_message("option2", user_lang)
    elif query.data == "option3":
        message = translate_message("option3", user_lang)
    elif query.data == "option4":
        message = translate_message("option4", user_lang)
    elif query.data == "option5":
        message = translate_message("option5", user_lang)
    elif query.data == "option6":
        message = translate_message("option6", user_lang)
    elif query.data == "option_vip":
        message = translate_message("option_vip", user_lang)
    elif query.data == "option_calendar":
        gregorian_date = datetime.now().strftime("%d %B %Y")
        gregorian_day = datetime.now().strftime("%A")
        jalali_date = jdatetime.datetime.now().strftime("%Y-%m-%d")
        jalali_day = jdatetime.datetime.now().strftime("%A")
        message = translate_message("option_calendar", user_lang, 
                                   gregorian_date=gregorian_date, gregorian_day=gregorian_day,
                                   jalali_date=jalali_date, jalali_day=jalali_day)
    elif query.data == "option_tip":
        today = datetime.now().strftime("%Y-%m-%d")
        if user_data["last_tip_date"] != today:
            user_data["last_tip_date"] = today
            users[user_id] = user_data
            save_users(users)
        tip = random.choice(BUSINESS_TIPS[user_lang if user_lang in BUSINESS_TIPS else "fa"])
        message = translate_message("option_tip", user_lang, tip=tip)

    keyboard = [back_button(user_lang)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(format_message(message), reply_markup=reply_markup, parse_mode="Markdown")

# تابع اصلی
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("vipcode", vipcode))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interactive_response))
    
    application.run_polling()

if __name__ == "__main__":
    main()
