from flask import Flask, jsonify, request
import telebot
from bot.clients import bot

app = Flask(__name__)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "🚀 Bot Web App is Running"


# =========================
# HEALTH
# =========================
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# =========================
# WEBHOOK (ONLY ONE!)
# =========================
import json

@app.route("/api/webhook", methods=["POST"])
def webhook():
    try:
        from flask import request
        from bot.clients import bot

        data = request.get_data(as_text=True)
        update_dict = json.loads(data)

        update = telebot.types.Update.de_json(update_dict)

        bot.process_new_updates([update])

        return "OK", 200

    except Exception as e:
        print("❌ ERROR:", e)
        return "OK", 200