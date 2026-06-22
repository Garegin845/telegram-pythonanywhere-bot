import os
from datetime import datetime

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)


from bot.clients import bot, BOT_INFO, store

from bot.config import (
    COMMIT_SHA,
    HF_SPACE_ID,
    HOSTING_LABEL,
    MODEL,
    RATE_LIMIT,
)

from bot.ai import ask_ai
from bot.helpers import (
    is_allowed,
    keep_typing,
    send_reply,
    should_respond,
)
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
from bot.rate_limit import is_rate_limited
@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )


    markup.add(
        KeyboardButton(
            text="🎬 Բացել Mini App",
            web_app=WebAppInfo("https://your-domain.com")
        )
    )


    markup.add(
        KeyboardButton("🤖 AI"),
        KeyboardButton("👤 Իմ պրոֆիլը")
    )

    markup.add(
        KeyboardButton("⭐ Premium"),
        KeyboardButton("❤️ Ընտրյալներ")
    )


    markup.add(
        KeyboardButton("🎁 Բոնուսներ"),
        KeyboardButton("🎮 Խաղեր")
    )


    markup.add(
        KeyboardButton("📺 Նորություններ"),
        KeyboardButton("📥 Ներբեռնումներ")
    )

    markup.add(
        KeyboardButton("📂 Պատմություն"),
        KeyboardButton("💳 Վճարումներ")
    )

    markup.add(
        KeyboardButton("🔔 Ծանուցումներ"),
        KeyboardButton("🌙 Գիշերային ռեժիմ")
    )

    markup.add(
        KeyboardButton("🌐 Լեզու"),
        KeyboardButton("⚙️ Կարգավորումներ")
    )

    markup.add(
        KeyboardButton("📢 Մեր ալիքը"),
        KeyboardButton("📞 Կապ")
    )

    # Row 9
    markup.add(
        KeyboardButton("ℹ️ Օգնություն")
    )

    bot.send_message(
        message.chat.id,
        f"""
🎉 <b>Բարի գալուստ, {message.from_user.first_name}։</b>

🤖 AI Օգնական

🎬 Mini App

⭐ Premium

❤️ Ընտրյալներ

📺 Նորություններ

🎁 Բոնուսներ

👇 Ընտրեք ցանկալի բաժինը։
""",
        parse_mode="HTML",
        reply_markup=markup
    )




@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):
    bot.send_message(
        message.chat.id,
        """
📖 <b>Օգնություն</b>

🟢 /start - Գլխավոր էջ

♻️ /reset - Մաքրել հիշողությունը

ℹ️ /about - Տեղեկություն բոտի մասին

⚙️ /model - AI մոդելի ընտրություն

📞 Հարցերի դեպքում գրեք մեզ։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "👤 Իմ պրոֆիլը")
def profile(message):

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
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "⭐ Premium")
def premium(message):

    bot.send_message(
        message.chat.id,
        """
💎 <b>Premium</b>

✅ Առանց գովազդի

✅ Full HD

✅ Արագ սպասարկում

✅ Վաղ հասանելիություն

✅ Premium բաժին

💳 Շուտով հնարավոր կլինի գնել։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "❤️ Ընտրյալներ")
def favorites(message):

    bot.send_message(
        message.chat.id,
        """
❤️ <b>Ընտրյալներ</b>

Դուք դեռ չունեք ընտրյալներ։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "🎁 Բոնուսներ")
def bonus(message):

    bot.send_message(
        message.chat.id,
        """
🎁 <b>Բոնուսներ</b>

🎉 Ամեն օր ստացեք բոնուսներ։

⭐ Premium օգտատերերը ստանում են կրկնակի բոնուս։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "🎮 Խաղեր")
def games(message):

    bot.send_message(
        message.chat.id,
        """
🎮 <b>Խաղեր</b>

Շուտով այստեղ կլինեն Telegram Mini Games։
""",
        parse_mode="HTML"
    )



@bot.message_handler(func=lambda m: m.text == "📺 Նորություններ")
def news(message):

    bot.send_message(
        message.chat.id,
        """
📺 <b>Նորություններ</b>

Այս պահին նորություններ չկան։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "📥 Ներբեռնումներ")
def downloads(message):

    bot.send_message(
        message.chat.id,
        """
📥 <b>Ներբեռնումներ</b>

Դուք դեռ ոչինչ չեք ներբեռնել։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "📂 Պատմություն")
def history(message):

    bot.send_message(
        message.chat.id,
        """
📂 <b>Պատմություն</b>

Դիտումների պատմությունը դատարկ է։
""",
        parse_mode="HTML"
    )



@bot.message_handler(func=lambda m: m.text == "💳 Վճարումներ")
def payments(message):

    bot.send_message(
        message.chat.id,
        """
💳 <b>Վճարումներ</b>

Idram

Telcell

EasyPay

Bank Card

Telegram Stars
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "🔔 Ծանուցումներ")
def notifications(message):

    bot.send_message(
        message.chat.id,
        """
🔔 <b>Ծանուցումներ</b>

✅ Նոր սերիաներ

✅ Նոր ֆիլմեր

✅ Premium առաջարկներ
""",
        parse_mode="HTML"
    )



@bot.message_handler(func=lambda m: m.text == "🌙 Գիշերային ռեժիմ")
def dark_mode(message):

    bot.send_message(
        message.chat.id,
        """
🌙 <b>Գիշերային ռեժիմ</b>

Շուտով հասանելի կլինի։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "🌐 Լեզու")
def language(message):

    bot.send_message(
        message.chat.id,
        """
🌐 <b>Լեզու</b>

🇦🇲 Հայերեն

🇬🇧 English

🇷🇺 Русский

Շուտով հնարավոր կլինի փոխել։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "⚙️ Կարգավորումներ")
def settings(message):

    bot.send_message(
        message.chat.id,
        """
⚙️ <b>Կարգավորումներ</b>

🤖 AI

🌐 Լեզու

🌙 Թեմա

🔔 Ծանուցումներ

💾 Հիշողություն
""",
        parse_mode="HTML"
    )



@bot.message_handler(func=lambda m: m.text == "📢 Մեր ալիքը")
def channel(message):

    bot.send_message(
        message.chat.id,
        """
📢 <b>Մեր ալիքը</b>

Այստեղ կարող եք տեղադրել ձեր Telegram Channel-ի հղումը։
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "📞 Կապ")
def contact(message):

    bot.send_message(
        message.chat.id,
        """
📞 <b>Կապ</b>

📧 Email:
support@example.com

💬 Telegram:
@username
""",
        parse_mode="HTML"
    )




@bot.message_handler(func=lambda m: m.text == "ℹ️ Օգնություն")
def help_button(message):
    cmd_help(message)