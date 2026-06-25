from datetime import datetime
import os
import random
import time
from flask import Flask, request
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, LabeledPrice

from bot.ai import ask_ai
from bot.clients import BOT_INFO, bot, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
from bot.rate_limit import is_rate_limited

# 1. Ստեղծում ենք Flask հավելվածը
app = Flask(__name__)

# 2. Սահմանում ենք գաղտնի տոկեն Webhook-ի անվտանգության համար
WEBHOOK_SECRET = os.environ.get("BOT_TOKEN", "my_secret_token")
WEBHOOK_URL = f"https://Garegin704.pythonanywhere.com/{WEBHOOK_SECRET}"

# 📢 ՏԵԼԵԳՐԱՄ ԱԼԻՔԻ ID (Փոխիր քո ալիքի username-ով)
CHANNEL_ID = "@your_channel_username"

# Ստուգում ենք առողջությունը (Health Check)
@app.route("/api/health")
def health():
    return {"status": "ok"}

# 3. Webhook-ի հիմնական Route-ը, որտեղ Telegram-ը ուղարկելու է նամակները
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

# ==========================
# ԲՈՏԻ ՏԵՔՍՏԵՐԸ ԵՎ ՄԵՆՅՈՒՆ
# ==========================
START_TEXTS = [
    "🎉 Բարի գալուստ, {name} 🙂",
    "👋 Հեյ {name}, արի սկսենք 😄",
    "✨ Ողջույն {name}, պատրաստ եմ օգնել քեզ",
    "🚀 Բարի գալուստ {name}, ինչով սկսենք?",
]

HELP_TEXTS = [
    "📖 Օգնություն այստեղ է 🙂 ինչ ուզում ես հարցրու",
    "ℹ️ Կարող ես ինձ գրել ցանկացած բան 😄",
    "🧠 Ես կօգնեմ քեզ ինչ հարց էլ լինի",
    "💬 Գրիր ու կպատասխանեմ բնական ձևով",
]

MENU_BUTTONS = {
    "🎬 Բացել Mini App", "🤖 AI", "👤 Իմ պրոֆիլը", "⭐ Premium",
    "❤️ Ընտրյալներ", "🎁 Բոնուսներ", "🎮 Խաղեր", "📺 Նորություններ",
    "📥 Ներբեռնումներ", "📂 Պատմություն", "💳 Վճարումներ", "🔔 Ծանուցումներ",
    "🌙 Գիշերային ռեժիմ", "🌐 Լեզու", "⚙️ Կարգավորումներ", "📢 Մեր ալիքը",
    "📞 Կապ", "ℹ️ Օգնություն", "💳 Գնել Premium", "⬅️ Հետ",
    "1", "2", "3", "4", "5", "6", "💰 Հաշվի մնացորդ",
    "👤 My Profile", "💰 Balance", "🎁 Bonuses", "🎮 Games", "📺 News", "📂 History", "💳 Payments", "🌐 Language", "⚙️ Settings", "ℹ️ Help", "⬅️ Back",
    "👤 Мой профиль", "💰 Баланс", "🎁 Бонусы", "🎮 Игры", "📺 Новости", "📂 История", "💳 Платежи", "🌐 Язык", "⚙️ Настройки", "ℹ️ Помощь", "⬅️ Назад"
}

# ==========================
# ԲԱԶՄԱԼԵԶՈՒ ՏԵՔՍՏԵՐԻ ԲԱՌԱՐԱՆ
# ==========================
LOCALES = {
    "am": {
        "news": "📺 <b>Կինո նորություններ</b>\n\n🔥 <i>«Ավատար 3»</i>-ի նոր թրեյլերը ռեկորդներ է սահմանում:\n🎬 Հայկական նոր սիթքոմը կլինի էկրաններին հաջորդ ամիս:\n🍿 Այս շաբաթվա ամենադիտված սերիալը դարձել է «Stranger Things»-ի նոր սեզոնը:",
        "history": "📂 <b>Դիտումների Պատմություն</b>\n\n🎬 Դուք վերջերս դիտել եք՝\n1. «Անտուրաժ» (Սերիալ) - 5-րդ սերիա\n2. «Ինտերստելար» (Ֆիլմ) - Ավարտված",
        "payments": "💳 <b>Վճարումների Պատմություն</b>\n\n📥 Ստացված բոնուս՝ +50 ֏ (Ալիքի բաժանորդագրություն)\n📤 Ելք՝ -100 Telegram Stars (Premium 30 օր)",
        "balance": "💳 <b>Հաշվի Մնացորդ</b>\n\n💰 Ձեր հաշվեկշիռը՝ <b>{balance} դրամ</b>",
        "settings": "⚙️ <b>Կարգավորումներ</b>\n\n🛠️ <b>Անձնական տվյալներ:</b> Կառավարեք ձեր պրոֆիլը:\n🔔 <b>Ծանուցումներ:</b> Միացրեք/Անջատեք նոր ֆիլմերի ազդանշանները:\n🗑️ <b>Հիշողություն:</b> Օգտագործեք /reset հրամանը AI-ի հիշողությունը մաքրելու համար:",
        "bonus_ok": "🎁 <b>Բոնուս!</b>\n\nՇնորհակալություն ալիքին բաժանորդագրվելու համար: Ձեր հաշվին ավելացավ <b>50 դրամ</b>!",
        "bonus_already": "❌ Դուք արդեն ստացել եք ձեր 50 դրամ բոնուսը:",
        "bonus_fail": "📢 Բոնուսը ստանալու համար նախ պետք է բաժանորդագրվեք մեր ալիքին: \n👉 {channel}",
        "lang_select": "🌐 Ընտրեք լեզուն / Select Language / Выберите язык:",
        "back": "⬅️ Հետ"
    },
    "en": {
        "news": "📺 <b>Movie News</b>\n\n🔥 <i>Avatar 3</i> trailer breaks records!\n🎬 New episodes of top series are available tonight.\n🍿 'Stranger Things' remains the most-watched show this week.",
        "history": "📂 <b>Watch History</b>\n\n🎬 Recently watched:\n1. 'Entourage' (Series) - Ep. 5\n2. 'Interstellar' (Movie) - Completed",
        "payments": "💳 <b>Payment History</b>\n\n📥 Bonus received: +50 AMD (Channel sub)\n📤 Spent: -100 Telegram Stars (Premium 30 days)",
        "balance": "💳 <b>Account Balance</b>\n\n💰 Your balance: <b>{balance} AMD</b>",
        "settings": "⚙️ <b>Settings</b>\n\n🛠️ <b>Profile:</b> Manage your personal data.\n🔔 <b>Notifications:</b> Toggle movie alerts.\n🗑️ <b>Memory:</b> Use /reset to clear AI chat history.",
        "bonus_ok": "🎁 <b>Bonus!</b>\n\nThank you for subscribing! <b>50 AMD</b> has been added to your account!",
        "bonus_already": "❌ You have already claimed this 50 AMD bonus.",
        "bonus_fail": "📢 To claim the bonus, you must first subscribe to our channel: \n👉 {channel}",
        "lang_select": "🌐 Choose your language:",
        "back": "⬅️ Back"
    },
    "ru": {
        "news": "📺 <b>Новости кино</b>\n\n🔥 Трейлер <i>«Аватар 3»</i> бьет рекорды!\n🎬 Новый сезон популярного сериала выходит уже в следующем месяце.\n🍿 «Очень странные дела» стал самым просматриваемым сериалом недели.",
        "history": "📂 <b>История просмотров</b>\n\n🎬 Недавно смотрели:\n1. «Антураж» (Сериал) - 5 серия\n2. «Интерстеллар» (Фильм) - Завершено",
        "payments": "💳 <b>История платежей</b>\n\n📥 Бонус: +50 драм (Подписка)\n📤 Списано: -100 Telegram Stars (Premium 30 дней)",
        "balance": "💳 <b>Баланс аккаунта</b>\n\n💰 Ваш баланс: <b>{balance} драм</b>",
        "settings": "⚙️ <b>Настройки</b>\n\n🛠️ <b>Профиль:</b> Управление личными данными.\n🔔 <b>Уведомления:</b> Включение/выключение пушей.\n🗑️ <b>Память:</b> Используйте /reset для очистки памяти AI.",
        "bonus_ok": "🎁 <b>Бонус!</b>\n\nСпасибо за подписку! <b>50 драм</b> зачислены на ваш счет!",
        "bonus_already": "❌ Вы уже получили этот бонус в 50 драм.",
        "bonus_fail": "📢 Чтобы получить бонус, сначала подпишитесь на наш канал: \n👉 {channel}",
        "lang_select": "🌐 Выберите язык:",
        "back": "⬅️ Назад"
    }
}

def get_user_lang(user_id):
    return store.get(f"lang:{user_id}") or "am"

def get_back_keyboard(user_id):
    lang = get_user_lang(user_id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(LOCALES[lang]["back"]))
    return markup

# ==========================
# COMMAND HANDLERS
# ==========================

@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):
    random_help = random.choice(HELP_TEXTS)
    bot.send_message(
        message.chat.id,
        f"{random_help}\n\n📖 <b>Օգնություն</b>\n\n🟢 /start - Գլխավոր էջ\n♻️ /reset - Մաքրել հիշողությունը\nℹ️ /about - Տեղեկություն բոտի մասին\n⚙️ /model - AI մոդելի ընտրություն\n/quote - ✨ Ոգեշնչող միտք\n/joke - 😂 Զվարճալի անեկդոտ\n\n📞 Հարցերի դեպքում գրեք մեզ։",
        parse_mode="HTML",
    )

@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
    # Մաքրում ենք խաղի ընթացիկ վիճակը գլխավոր էջ վերադառնալիս
    store.delete(f"game_status:{message.from_user.id}")

    random_start = random.choice(START_TEXTS).format(name=message.from_user.first_name)
    
    lang = get_user_lang(message.from_user.id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(text="🎬 Բացել Mini App", web_app=WebAppInfo("https://garegin704.pythonanywhere.com/")))
    
    if lang == "am":
        markup.add(KeyboardButton("🤖 AI"), KeyboardButton("👤 Իմ պրոֆիլը"))
        markup.add(KeyboardButton("⭐ Premium"), KeyboardButton("💰 Հաշվի մնացորդ"))
        markup.add(KeyboardButton("🎁 Բոնուսներ"), KeyboardButton("🎮 Խաղեր"))
        markup.add(KeyboardButton("📺 Նորություններ"), KeyboardButton("📂 Պատմություն"))
        markup.add(KeyboardButton("💳 Վճարումներ"), KeyboardButton("🔔 Ծանուցումներ"))
        markup.add(KeyboardButton("🌐 Լեզու"), KeyboardButton("⚙️ Կարգավորումներ"))
        markup.add(KeyboardButton("📢 Մեր ալիքը"), KeyboardButton("📞 Կապ"))
        markup.add(KeyboardButton("ℹ️ Օգնություն"))
    elif lang == "en":
        markup.add(KeyboardButton("🤖 AI"), KeyboardButton("👤 My Profile"))
        markup.add(KeyboardButton("⭐ Premium"), KeyboardButton("💰 Balance"))
        markup.add(KeyboardButton("🎁 Bonuses"), KeyboardButton("🎮 Games"))
        markup.add(KeyboardButton("📺 News"), KeyboardButton("📂 History"))
        markup.add(KeyboardButton("💳 Payments"), KeyboardButton("🔔 Notifications"))
        markup.add(KeyboardButton("🌐 Language"), KeyboardButton("⚙️ Settings"))
        markup.add(KeyboardButton("📢 Our Channel"), KeyboardButton("📞 Contact"))
        markup.add(KeyboardButton("ℹ️ Help"))
    else:
        markup.add(KeyboardButton("🤖 AI"), KeyboardButton("👤 Мой профиль"))
        markup.add(KeyboardButton("⭐ Premium"), KeyboardButton("💰 Баланс"))
        markup.add(KeyboardButton("🎁 Бонусы"), KeyboardButton("🎮 Игры"))
        markup.add(KeyboardButton("📺 Новости"), KeyboardButton("📂 История"))
        markup.add(KeyboardButton("💳 Платежи"), KeyboardButton("🔔 Уведомления"))
        markup.add(KeyboardButton("🌐 Язык"), KeyboardButton("⚙️ Настройки"))
        markup.add(KeyboardButton("📢 Наш канал"), KeyboardButton("📞 Связь"))
        markup.add(KeyboardButton("ℹ️ Помощь"))

    bot.send_message(
        message.chat.id,
        f"{random_start}\n\n🤖 AI Օգնական\n🎬 Mini App\n⭐ Premium\n❤️ Ընտրյալներ\n📺 Նորություններ\n🎁 Բոնուսներ\n\n👇 Ընտրեք ցանկալի բաժինը։",
        parse_mode="HTML",
        reply_markup=markup,
    )

# ==========================
# TEXT HANDLERS (MENU)
# ==========================

@bot.message_handler(func=lambda m: m.text in ["👤 Իմ պրոֆիլը", "👤 My Profile", "👤 Мой профиль"])
def profile(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"👤 <b>Իմ պրոֆիլը</b>\n\n🆔 ID\n<code>{message.from_user.id}</code>\n\n👤 Անուն\n{message.from_user.first_name}\n\n⭐ Premium\n❌ Չկա\n\n❤️ Ընտրյալներ\n0\n\n📺 Դիտվածներ\n0\n\n📅 Գրանցում\nԱյսօր", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))


@bot.message_handler(func=lambda m: m.text == "⭐ Premium")
def premium(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("💳 Գնել Premium"))
    markup.add(KeyboardButton(LOCALES[lang]["back"]))

    bot.send_message(
        message.chat.id,
        """
💎 <b>HayKino Premium</b>

✅ Առանց գովազդի
✅ Full HD դիտում
✅ Premium ֆիլմեր
✅ Արագ հասանելիություն

⭐ Գին՝ 100 Telegram Stars

Ընտրեք գործողությունը։
""",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "💳 Գնել Premium")
def buy_premium(message):
    bot.send_invoice(
        chat_id=message.chat.id,
        title="HayKino Premium",
        description="Premium 30 օր",
        invoice_payload="premium_30_days",
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="HayKino Premium 30 օր",
                amount=100
            )
        ]
    )

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=["successful_payment"])
def payment_success(message):
    bot.send_message(
        message.chat.id,
        """
🎉 Վճարումը հաջողվեց։

⭐ Ձեր HayKino Premium-ը ակտիվացված է։

Բացեք Mini App-ը և օգտվեք Premium բաժնից։
"""
    )


@bot.message_handler(func=lambda m: m.text in ["🎮 Խաղեր", "🎮 Games", "🎮 Игры"])
def games(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Ստուգում ենք օրական 1 անգամ խաղալու սահմանափակումը
    last_played = store.get(f"game_date:{user_id}")
    if last_played == today:
        bot.send_message(
            message.chat.id,
            "❌ Դուք այսօր արդեն փորձել եք ձեր բախտը։ Սպասեք հաջորդ օրվան։ 🔄",
            reply_markup=get_back_keyboard(user_id)
        )
        return

    # Գրանցում ենք, որ օգտատիրոջից սպասում ենք թիվ
    store.set(f"game_status:{user_id}", "waiting_num")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        KeyboardButton("1"), KeyboardButton("2"), KeyboardButton("3"),
        KeyboardButton("4"), KeyboardButton("5"), KeyboardButton("6")
    )
    markup.add(KeyboardButton(LOCALES[lang]["back"]))

    bot.send_message(
        message.chat.id,
        """
🎮 <b>Բախտի Զառ</b>

Ընտրեք կամ գրեք 1-ից 6 թվերից մեկը։
Եթե զառի թիվը համընկնի ձեր ընտրած թվի հետ, դուք կշահեք <b>Բոնուս Ֆիլմ Դրամ</b>։

⚠️ <i>Հնարավորությունն ընձեռվում է օրական ընդամենը 1 անգամ։</i>
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text in ["1", "2", "3", "4", "5", "6"])
def handle_dice_guess(message):
    user_id = message.from_user.id
    status = store.get(f"game_status:{user_id}")

    # Եթե խաղի կարգավիճակում չէ, փոխանցում ենք AI-ին
    if status != "waiting_num":
        return ai_chat(message)

    today = datetime.now().strftime("%Y-%m-%d")
    store.set(f"game_date:{user_id}", today) # Գրանցում ենք այսօրվա փորձը
    store.delete(f"game_status:{user_id}") # Ավարտում ենք խաղի սպասումը

    guess = int(message.text)
    
    # Ուղարկում ենք ինտերակտիվ զառը
    dice_msg = bot.send_dice(message.chat.id, emoji="🎲")
    dice_value = dice_msg.dice.value

    # Սպասում ենք 3 վայրկյան՝ մինչև անիմացիան ավարտվի
    time.sleep(3)

    if guess == dice_value:
        bot.send_message(
            message.chat.id,
            f"🎉 <b>Շնորհավորում ենք։</b>\nԴուք գուշակեցիք ճիշտ թիվը ({guess})։\n\n🎁 Դուք ստացաք ձեր օրական բոնուսը՝ <b>Ֆիլմ Դրամ</b>։",
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            f"😢 <b>Ափսոս, չհամընկավ։</b>\nԴուք ընտրել էիք {guess}, բայց նետվեց {dice_value}։\n\nՓորձեք վաղը։ 🤞",
            parse_mode="HTML"
        )


@bot.message_handler(func=lambda m: m.text == "❤️ Ընտրյալներ")
def favorites(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "❤️ <b>Ընտրյալներ</b>\n\nԴուք դեռ չունեք ընտրյալներ։", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["🎁 Բոնուսներ", "🎁 Bonuses", "🎁 Бонусы"])
def bonus(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    already_claimed = store.get(f"bonus_claimed:{user_id}")
    if already_claimed:
        bot.send_message(message.chat.id, LOCALES[lang]["bonus_already"], reply_markup=get_back_keyboard(user_id))
        return

    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            current_bal = int(store.get(f"balance:{user_id}") or 0)
            store.set(f"balance:{user_id}", str(current_bal + 50))
            store.set(f"bonus_claimed:{user_id}", "true")
            bot.send_message(message.chat.id, LOCALES[lang]["bonus_ok"], parse_mode="HTML", reply_markup=get_back_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, LOCALES[lang]["bonus_fail"].format(channel=CHANNEL_ID), reply_markup=get_back_keyboard(user_id))
    except Exception:
        bot.send_message(message.chat.id, "🎁 <b>Բոնուսներ</b>\n\n🎉 Ամեն օր ստացեք բոնուսներ։\n\n⭐ Premium օգտատերերը ստանում են կրկնակի բոնուս։\n\n(Ալիքի ստուգումը հասանելի չէ, խնդրում ենք ստուգել CHANNEL_ID-ն):", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["📺 Նորություններ", "📺 News", "📺 Новости"])
def news(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    bot.send_message(message.chat.id, LOCALES[lang]["news"], parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["⬅️ Հետ", "⬅️ Back", "⬅️ Назад"])
def back_menu(message):
    cmd_start(message)

@bot.message_handler(func=lambda m: m.text == "📥 Ներբեռնումներ")
def downloads(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "📥 <b>Ներբեռնումներ</b>\n\nԴուք դեռ ոչինչ չեք ներբեռնել։", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["📂 Պատմություն", "📂 History", "📂 История"])
def history(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    bot.send_message(message.chat.id, LOCALES[lang]["history"], parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["💳 Վճարումներ", "💳 Payments", "💳 Платежи"])
def payments(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    bot.send_message(message.chat.id, LOCALES[lang]["payments"], parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "🔔 Ծանուցումներ")
def notifications(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "🔔 <b>Ծանուցումներ</b>\n\n✅ Նոր սերիաներ\n✅ Նոր ֆիլմեր\n✅ Premium առաջարկներ", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "🌙 Գիշերային ռեժիմ")
def dark_mode(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "🌙 <b>Գիշերային ռեժիմ</b>\n\nՇուտով հասանելի կլինի։", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["💰 Հաշվի մնացորդ", "💰 Balance", "💰 Баланс"])
def account_balance(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    bal = store.get(f"balance:{user_id}") or "0"
    text = LOCALES[lang]["balance"].format(balance=bal)
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text in ["🌐 Լեզու", "🌐 Language", "🌐 Язык"])
def language(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(KeyboardButton("🇦🇲 Հայերեն"), KeyboardButton("🇬🇧 English"), KeyboardButton("🇷🇺 Русский"))
    markup.add(KeyboardButton(LOCALES[lang]["back"]))
    bot.send_message(message.chat.id, LOCALES[lang]["lang_select"], reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🇦🇲 Հայերեն", "🇬🇧 English", "🇷🇺 Русский"])
def change_lang(message):
    user_id = message.from_user.id
    if message.text == "🇦🇲 Հայերեն":
        store.set(f"lang:{user_id}", "am")
    elif message.text == "🇬🇧 English":
        store.set(f"lang:{user_id}", "en")
    elif message.text == "🇷🇺 Русский":
        store.set(f"lang:{user_id}", "ru")
        
    bot.send_message(message.chat.id, "✅ Done! / ✅ Հաջողությամբ փոխվեց!")
    cmd_start(message)

@bot.message_handler(func=lambda m: m.text in ["⚙️ Կարգավորումներ", "⚙️ Settings", "⚙️ Настройки"])
def settings(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    bot.send_message(message.chat.id, LOCALES[lang]["settings"], parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "📢 Մեր ալիքը")
def channel(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "📢 <b>Մեր ալիքը</b>\n\nԱյստեղ կարող եք տեղադրել ձեր Telegram Channel-ի հղումը։", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "📞 Կապ")
def contact(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "📞 <b>Կապ</b>\n\n📧 Email:\nsupport@example.com\n\n💬 Telegram:\n@username", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "ℹ️ Օգնություն")
def help_button(message):
    cmd_help(message)

@bot.message_handler(func=lambda m: m.text == "🤖 AI")
def ai_button(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "🤖 <b>AI Օգնական</b>\n\nԳրեք ձեր հարցը, և ես կպատասխանեմ։", parse_mode="HTML", reply_markup=get_back_keyboard(user_id))

# ==========================
# AI CHAT HANDLER
# ==========================
@bot.message_handler(commands=["remember"], func=is_allowed)
def cmd_remember(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.send_message(message.chat.id, "💡 Օգտագործում՝ /remember [ձեր տեքստը]")
        return
    note = parts[1].strip()
    store.set(f"note:{message.from_user.id}", note)
    bot.send_message(message.chat.id, "💾 Saved!")

@bot.message_handler(commands=["recall"], func=is_allowed)
def cmd_recall(message):
    key = f"note:{message.from_user.id}"
    note = store.get(key)
    if not note:
        bot.send_message(message.chat.id, "Nothing saved yet.")
        return
    bot.send_message(message.chat.id, f"🧠 Your note:\n{note}")
    
@bot.message_handler(commands=["quote"], func=is_allowed)
def cmd_quote(message):
    prompt = "Գրիր մեկ կարճ, ոգեշնչող մեջբերում հայերենով։ ✨\n\nՊահանջներ․\n- Ամեն անգամ նոր լինի․\n- 1-3 նախադասություն․\n- Օգտագործիր 1-3 համապատասխան emoji (✨💪🌟🔥😊)․\n- Մի մեջբերիր հայտնի մարդկանց․\n- Թող լինի օրիգինալ․\n- Մի գրիր բացատրություն կամ վերնագիր։"
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["joke"], func=is_allowed)
def cmd_joke(message):
    prompt = "Պատմիր մեկ կարճ, զվարճալի անեկդոտ հայերենով։ 😂\n\nՊահանջներ․\n- Ամեն անգամ նոր անեկդոտ․\n- 2-5 տող․\n- Օգտագործիր համապատասխան emoji-ներ 😊😂🤣😅🙃․\n- Թող լինի մաքուր ու ընտանեկան հումոր․\n- Մի գրիր բացատրություն կամ նախաբան, միայն անեկդոտը։"
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.text not in MENU_BUTTONS)
def ai_chat(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        reply = ask_ai(message.from_user.id, message.text)
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, "❌ AI սխալ: Փորձեք մի փոքր ուշ։")
        print(f"AI Error: {e}")

# 4. Ակտիվացնում ենք Webhook-ը հենց սերվերը սկսում է աշխատել
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)