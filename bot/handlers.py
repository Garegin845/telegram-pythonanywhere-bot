from datetime import datetime
import os
import random
import time
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

from bot.ai import ask_ai
from bot.clients import BOT_INFO, bot, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
from bot.rate_limit import is_rate_limited

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
    "🎬 Բացել Mini App",
    "🤖 AI",
    "👤 Իմ պրոֆիլը",
    "⭐ Premium",
    "❤️ Ընտրյալներ",
    "🎁 Բոնուսներ",
    "🎮 Խաղեր",
    "📺 Նորություններ",
    "📥 Ներբեռնումներ",
    "📂 Պատմություն",
    "💳 Վճարումներ",
    "🔔 Ծանուցումներ",
    "💰 Հաշվի մնացորդ",
    "🌐 Լեզու",
    "⚙️ Կարգավորումներ",
    "📢 Մեր ալիքը",
    "📞 Կապ",
    "ℹ️ Օգնություն",
    "⬅️ Հետ",
    "🇦🇲 Հայերեն", "🇷🇺 Русский", "🇬🇧 English",
    "1", "2", "3", "4", "5", "6"
}


# ==========================
# COMMAND HANDLERS
# ==========================

@bot.message_handler(func=lambda m: m.text == "⭐ Premium")
def premium(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("💳 Գնել Premium"))
    markup.add(KeyboardButton("⬅️ Հետ"))

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
    bot.answer_pre_checkout_query(
        query.id,
        ok=True
    )


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


@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):
    random_help = random.choice(HELP_TEXTS)
    
    bot.send_message(
        message.chat.id,
        f"""
{random_help}

📖 <b>Օգնություն</b>

🟢 /start - Գլխավոր էջ

♻️ /reset - Մաքրել հիշողությունը

ℹ️ /about - Տեղեկություն բոտի մասին

⚙️ /model - AI մոդելի ընտրություն

/quote - ✨ Ոգեշնչող միտք

/joke - 😂 Զվարճալի անեկդոտ

📞 Հարցերի դեպքում գրեք մեզ։
""",
        parse_mode="HTML",
    )


@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
    store.delete(f"game_status:{message.from_user.id}")
    
    random_start = random.choice(START_TEXTS).format(name=message.from_user.first_name)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
   
    markup.add(KeyboardButton("🤖 AI"), KeyboardButton("👤 Իմ պրոֆիլը"))
    markup.add(KeyboardButton("⭐ Premium"), KeyboardButton("❤️ Ընտրյալներ"))
    markup.add(KeyboardButton("🎁 Բոնուսներ"), KeyboardButton("🎮 Խաղեր"))
    markup.add(KeyboardButton("📺 Նորություններ"), KeyboardButton("📥 Ներբեռնումներ"))
    markup.add(KeyboardButton("📂 Պատմություն"), KeyboardButton("💳 Վճարումներ"))
    markup.add(KeyboardButton("🔔 Ծանուցումներ"), KeyboardButton("💰 Հաշվի մնացորդ"))
    markup.add(KeyboardButton("🌐 Լեզու"), KeyboardButton("⚙️ Կարգավորումներ"))
    markup.add(KeyboardButton("📢 Մեր ալիքը"), KeyboardButton("📞 Կապ"))
    markup.add(KeyboardButton("ℹ️ Օգնություն"))

    bot.send_message(
        message.chat.id,
        f"""
{random_start}

🤖 AI Օգնական
🎬 Mini App
⭐ Premium
❤️ Ընտրյալներ
📺 Նորություններ
🎁 Բոնուսներ

👇 Ընտրեք ցանկալի բաժինը։
""",
        parse_mode="HTML",
        reply_markup=markup,
    )


# ==========================
# TEXT HANDLERS (MENU)
# ==========================

@bot.message_handler(func=lambda m: m.text == "👤 Իմ պրոֆիլը")
def profile(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        f"""
👤 <b>Իմ պրոֆիլը</b>

🆔 ID
<code>{message.from_user.id}</code>

👤 Անուն
{message.from_user.first_name}

⭐ Premium
❌ Չկա

❤️ Ընտրյալներ
0

📺 Դիտվածներ
0

📅 Գրանցում
Այսօր
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🎮 Խաղեր")
def games(message):
    user_id = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")
    
    last_played = store.get(f"game_date:{user_id}")
    if last_played == today:
        bot.send_message(
            message.chat.id,
            "❌ Դուք այսօր արդեն փորձել եք ձեր բախտը։ Սպասեք հաջորդ օրվան։ 🔄"
        )
        return

    store.set(f"game_status:{user_id}", "waiting_num")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        KeyboardButton("1"), KeyboardButton("2"), KeyboardButton("3"),
        KeyboardButton("4"), KeyboardButton("5"), KeyboardButton("6")
    )
    markup.add(KeyboardButton("⬅️ Հետ"))

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

    if status != "waiting_num":
        return ai_chat(message)

    today = datetime.now().strftime("%Y-%m-%d")
    store.set(f"game_date:{user_id}", today)
    store.delete(f"game_status:{user_id}")

    guess = int(message.text)
    
    dice_msg = bot.send_dice(message.chat.id, emoji="🎲")
    dice_value = dice_msg.dice.value

    time.sleep(3)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))

    if guess == dice_value:
        bot.send_message(
            message.chat.id,
            f"""
🎉 <b>Շնորհավորում ենք։</b>
Դուք գուշակեցիք ճիշտ թիվը ({guess})։

🎁 Դուք ստացաք ձեր օրական բոնուսը՝ <b>Ֆիլմ Դրամ</b>։
""",
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            f"😢 <b>Ափսոս, չհամընկավ։</b>\nԴուք ընտրել էիք {guess}, բայց նետվեց {dice_value}։\n\nՓորձեք վաղը։ 🤞",
            parse_mode="HTML",
            reply_markup=markup
        )


@bot.message_handler(func=lambda m: m.text == "❤️ Ընտրյալներ")
def favorites(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
❤️ <b>Ընտրյալներ</b>

Դուք դեռ չունեք ընտրյալներ։
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🎁 Բոնուսներ")
def bonus(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    
    # Օգտագործում ենք inline կոճակ տելեգրամ ալիքի հղումով
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(InlineKeyboardButton("📢 Միանալ Ալիքին", url="https://t.me/your_channel_username")) # Փոխարինեք ձեր ալիքի լինկով
    inline_markup.add(InlineKeyboardButton("✅ Ստուգել և ստանալ 50֏", callback_data="check_subscription"))

    bot.send_message(
        message.chat.id,
        """
🎁 <b>Բոնուսներ</b>

🎉 Բաժանորդագրվեք մեր տելեգրամյան ալիքին և ստացեք <b>50 դրամ</b> բոնուս հաշվին:

⚠️ <i>Բոնուսը հասանելի է միայն մեկ անգամ նոր բաժանորդների համար:</i>
""",
        parse_mode="HTML",
        reply_markup=markup
    )
    bot.send_message(message.chat.id, "👇 Սեղմեք ներքևի կոճակը ալիքին միանալու համար.", reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subs(call):
    user_id = call.from_user.id
    try:
        # Փոխարինեք @your_channel_username ձեր ալիքի ID-ով կամ username-ով
        chat_member = bot.get_chat_member(chat_id="@your_channel_username", user_id=user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            # Ստուգում ենք արդյոք արդեն ստացել է բոնուսը
            already_received = store.get(f"bonus_received:{user_id}")
            if already_received:
                bot.answer_callback_query(call.id, "❌ Դուք արդեն ստացել եք այս բոնուսը:", show_alert=True)
            else:
                # Ավելացնում ենք 50 դրամ հաշվին
                current_balance = store.get(f"balance:{user_id}")
                balance = float(current_balance) if current_balance else 0.0
                balance += 50.0
                store.set(f"balance:{user_id}", str(balance))
                store.set(f"bonus_received:{user_id}", "true")
                
                bot.answer_callback_query(call.id, "🎉 Շնորհավոր! 50 դրամը փոխանցվեց ձեր հաշվին:", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ Դուք դեռ չեք բաժանորդագրվել ալիքին:", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Չհաջողվեց ստուգել բաժանորդագրությունը: Փորձեք ավելի ուշ:", show_alert=True)


@bot.message_handler(func=lambda m: m.text == "📺 Նորություններ")
def news(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
📺 <b>Նորություններ & Թրենդներ</b>

🎬 <b>Կինո և Սերիալներ.</b>
• Հայկական նոր սերիալի պրեմիերան սպասվում է այս շաբաթավերջին:
• Netflix-ի ամենահայտնի սերիալի նոր եթերաշրջանը արդեն հասանելի է Mini App-ում:

🔥 <b>Հայտնի իրադարձություններ.</b>
• Շուտով սպասվում է մեծ կինոմրցանակաբաշխություն, հետևեք թարմացումներին:
""",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "⬅️ Հետ")
def back_menu(message):
    cmd_start(message)

@bot.message_handler(func=lambda m: m.text == "📥 Ներբեռնումներ")
def downloads(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
📥 <b>Ներբեռնումներ</b>

Դուք դեռ ոչինչ չեք ներբեռնել ցուցակում։
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📂 Պատմություն")
def history(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    
    # Ցուցադրում ենք օգտատիրոջ դիտած ֆիլմերը (ստատիկ կամ բազայից)
    bot.send_message(
        message.chat.id,
        """
📂 <b>Դիտումների Պատմություն</b>

🎬 Ձեր վերջին դիտած ֆիլմերն ու սերիալները.
1. Սարդ-Մարդ. Տունդարձի ճանապարհ (Դիտված է)
2. Խաղալիքների պատմություն 4 (Կիսատ թողնված)

<i>Պատմությունը մաքրելու համար օգտագործեք /reset հրամանը:</i>
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "💳 Վճարումներ")
def payments(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
💳 <b>Վճարումների Պատմություն</b>

📥 <b>Ստացված բոնուսներ.</b>
• +50.00 ֏ (Տելեգրամ ալիքի բոնուս)
• +10.00 ֏ (Օրական Բախտի Զառ խաղից)

📤 <b>Կատարված վճարումներ.</b>
• -100 XTR (HayKino Premium 30 օր)

🟢 Համակարգեր՝ Idram, Telcell, EasyPay, Bank Card, Telegram Stars
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🔔 Ծանուցումներ")
def notifications(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
🔔 <b>Ծանուցումներ</b>

✅ Նոր սերիաներ
✅ Նոր ֆիլմեր
✅ Premium առաջարկներ
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "💰 Հաշվի մնացորդ")
def balance_handler(message):
    user_id = message.from_user.id
    current_balance = store.get(f"balance:{user_id}")
    balance = float(current_balance) if current_balance else 0.0

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))

    bot.send_message(
        message.chat.id,
        f"""
💰 <b>Ձեր Հաշվի Մնացորդը</b>

💵 Ընթացիկ հաշվեկշիռ՝ <b>{balance} դրամ</b>

🎁 Դուք կարող եք օգտագործել այս միջոցները հավելվածի ներսում գնումներ կատարելու համար:
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🌐 Լեզու")
def language(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(KeyboardButton("🇦🇲 Հայերեն"), KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇬🇧 English"))
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
🌐 <b>Ընտրեք լեզուն / Выберите язык / Select Language</b>

🇦🇲 Հայերեն
🇷🇺 Русский
🇬🇧 English
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text in ["🇦🇲 Հայերեն", "🇷🇺 Русский", "🇬🇧 English"])
def set_language_preference(message):
    user_id = message.from_user.id
    selected_lang = message.text

    # Պահպանում ենք ընտրված լեզուն
    store.set(f"user_lang:{user_id}", selected_lang)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))

    if selected_lang == "🇦🇲 Հայերեն":
        msg = "✅ Լեզուն հաջողությամբ փոխվեց՝ Հայերեն:"
    elif selected_lang == "🇷🇺 Русский":
        msg = "✅ Язык успешно изменен на Русский. (Այսուհետ համակարգը կթարգմանվի):"
    else:
        msg = "✅ Language successfully changed to English. (System will translate dynamically):"

    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "⚙️ Կարգավորումներ")
def settings(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🌐 Լեզու"), KeyboardButton("🤖 AI Մոդել"))
    markup.add(KeyboardButton("🔔 Ծանուցումների կարգավորում"), KeyboardButton("🗑️ Մաքրել քեշը"))
    markup.add(KeyboardButton("⬅️ Հետ"))

    bot.send_message(
        message.chat.id,
        """
⚙️ <b>Գլխավոր Կարգավորումներ</b>

🛠️ Այստեղ դուք կարող եք փոփոխել ձեր պրոֆիլի և բոտի աշխատանքի ձևաչափը:

🤖 <b>AI:</b> Ակտիվ
🌐 <b>Լեզու:</b> Ավտոմատ
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📢 Մեր ալիքը")
def channel(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
📢 <b>Մեր ալիքը</b>

📧 Email:
support@example.com

💬 Telegram:
@username
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📞 Կապ")
def contact(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
📞 <b>Կապ</b>

📧 Email:
support@example.com

💬 Telegram:
@username
""",
        parse_mode="HTML",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "ℹ️ Օգնություն")
def help_button(message):
    cmd_help(message)


@bot.message_handler(func=lambda m: m.text == "🤖 AI")
def ai_button(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Հետ"))
    bot.send_message(
        message.chat.id,
        """
🤖 <b>AI Օգնական</b>

Գրեք ձեր հարցը, և ես կպատասխանեմ։
""",
        parse_mode="HTML",
        reply_markup=markup
    )


# ==========================
# AI CHAT HANDLER
# ==========================
@bot.message_handler(commands=["remember"], func=is_allowed)
def cmd_remember(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: /remember something")
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
    prompt = """
Գրիր մեկ կարճ, ոգեշնչող մեջբերում հայերենով։ ✨

Պահանջներ․
- Ամեն անգամ նոր լինի։
- 1-3 նախադասություն։
- Օգտագործիր 1-3 համապատասխան emoji (✨💪🌟🔥😊)։
- Մի մեջբերիր հայտնի մարդկանց։
- Թող լինի օրիգինալ։
- Մի գրիր բացատրություն կամ վերնագիր։
"""
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=["joke"], func=is_allowed)
def cmd_joke(message):
    prompt = """
Պատմիր մեկ կարճ, զվարճալի անեկդոտ հայերենով։ 😂

Պահանջներ․
- Ամեն անգամ նոր անեկդոտ։
- 2-5 տող։
- Օգտագործիր համապատասխան emoji-ներ 😊😂🤣😅🙃։
- Թող լինի մաքուր ու ընտանեկան հումոր։
- Մի գրիր բացատրություն կամ նախաբան, միայն անեկդոտը։
"""
    reply = ask_ai(message.from_user.id, prompt)
    bot.send_message(message.chat.id, reply)


@bot.message_handler(func=lambda m: m.text and m.text not in MENU_BUTTONS)
def ai_chat(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")

        reply = ask_ai(message.from_user.id, message.text)

        bot.send_message(message.chat.id, reply)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ AI սխալ\n{e}")