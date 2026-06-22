import os
from datetime import datetime
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)

from bot.clients import bot, BOT_INFO, store
from bot.config import COMMIT_SHA, HF_SPACE_ID, HOSTING_LABEL, MODEL, RATE_LIMIT
from bot.ai import ask_ai
from bot.helpers import is_allowed, keep_typing, send_reply, should_respond
from bot.history import clear_history
from bot.preferences import get_provider, set_provider
from bot.rate_limit import is_rate_limited

VERBOSE_LOG = os.environ.get("BOT_VERBOSE_LOG", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)


def _log(message, direction: str, text: str) -> None:
    if not VERBOSE_LOG:
        return

    user = message.from_user
    user_name = (
        f"@{user.username}" if user.username else (user.first_name or f"user:{user.id}")
    )
    bot_name = f"@{BOT_INFO.username}"

    snippet = (text or "").replace("\n", " ").replace("\r", " ")
    if len(snippet) > 500:
        snippet = snippet[:500] + "..."

    if direction == "in":
        sender, receiver = user_name, bot_name
    else:
        sender, receiver = bot_name, user_name

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {sender} → {receiver}: {snippet}", flush=True)



@bot.message_handler(commands=["start"], func=is_allowed)
def cmd_start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(
        KeyboardButton(
            text="🎬 Open Mini App",
            web_app=WebAppInfo("https://your-domain.com")
        )
    )

    bot.send_message(
        message.chat.id,
        """
🎬 Welcome!

Open the Mini App to browse movies and series.

👇 Press the button below.
        """,
        reply_markup=markup,
    )


@bot.message_handler(commands=["help"], func=is_allowed)
def cmd_help(message):
    lines = [
        "/start — welcome message",
        "/help — show this message",
        "/reset — clear conversation history",
        "/about — about this bot",
        "/menu — show menu",
    ]

    if HF_SPACE_ID:
        lines.append("/model — switch AI provider")

    bot.send_message(message.chat.id, "\n".join(lines))




@bot.message_handler(commands=["reset"], func=is_allowed)
def cmd_reset(message):
    clear_history(message.from_user.id)
    bot.send_message(message.chat.id, "Conversation cleared. Starting fresh!")



@bot.message_handler(commands=["about"], func=is_allowed)
def cmd_about(message):
    if HF_SPACE_ID:
        provider = get_provider(message.from_user.id)
        model_line = (
            f"{MODEL} (main)"
            if provider == "main"
            else f"{HF_SPACE_ID} (hf)"
        )
    else:
        model_line = MODEL

    storage_line = "SQLite" if store is not None else "stateless (no memory)"

    lines = [
        f"Model  : {model_line}",
        f"Storage: {storage_line}",
        f"Hosting: {HOSTING_LABEL}",
    ]

    if COMMIT_SHA:
        lines.append(f"Version: {COMMIT_SHA}")

    bot.send_message(message.chat.id, "\n".join(lines))




if HF_SPACE_ID:

    @bot.message_handler(commands=["model"], func=is_allowed)
    def cmd_model(message):
        parts = (message.text or "").split(maxsplit=1)

        if len(parts) == 1:
            current = get_provider(message.from_user.id)

            bot.send_message(
                message.chat.id,
                f"Current provider: {current}\n\n"
                "Options:\n"
                "/model main — Cerebras\n"
                "/model hf — ArmGPT",
            )
            return

        choice = parts[1].strip().lower()

        if choice not in ("main", "hf"):
            bot.send_message(
                message.chat.id,
                "Invalid choice. Use: /model main or /model hf",
            )
            return

        if not set_provider(message.from_user.id, choice):
            bot.send_message(
                message.chat.id,
                "Could not save preference.",
            )
            return

        if choice == "hf":
            bot.send_message(
                message.chat.id,
                "Switched to ArmGPT.",
            )
        else:
            bot.send_message(
                message.chat.id,
                "Switched to Main Provider.",
            )




@bot.message_handler(content_types=["text"], func=is_allowed)
def handle_message(message):
    if not should_respond(message):
        return

    text = (message.text or "").replace(f"@{BOT_INFO.username}", "").strip()

    if not text:
        return

    _log(message, "in", text)

    if is_rate_limited(message.from_user.id):
        limit_msg = (
            f"You've reached the daily limit of {RATE_LIMIT} messages."
        )

        bot.send_message(message.chat.id, limit_msg)
        _log(message, "out", limit_msg)
        return

    try:
        with keep_typing(message.chat.id):
            reply = ask_ai(message.from_user.id, text)

        send_reply(message, reply)
        _log(message, "out", reply)

    except Exception as e:
        print(f"Error: {e}")

        bot.send_message(
            message.chat.id,
            "Something went wrong. Please try again.",
        )

        _log(message, "out", f"[error] {e}")