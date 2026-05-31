import os
import logging
import yt_dlp

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("8825680908:AAGtIitkyTME5DA8gFGquhA6KuOqfoNSML8")
WEBHOOK_URL = os.getenv("https://pinterest-download-1-di66.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

app_flask = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()


async def download_pinterest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if "pinterest.com" not in url and "pin.it" not in url:
        await update.message.reply_text("សូមផ្ញើ Pinterest Video Link")
        return

    try:
        os.makedirs("downloads", exist_ok=True)

        msg = await update.message.reply_text("⏳ កំពុងទាញយក...")

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        with open(file_path, "rb") as video:
            await update.message.reply_video(
                video=video,
                caption="✅ Pinterest Video Downloaded"
            )

        if os.path.exists(file_path):
            os.remove(file_path)

        await msg.delete()

    except Exception as e:
        logging.exception(e)
        await update.message.reply_text(f"❌ Error:\n{e}")


telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, download_pinterest)
)


@app_flask.route("/")
def home():
    return "Bot is running!"


@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

    return "OK"


async def setup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(setup())

    port = int(os.environ.get("PORT", 10000))

    app_flask.run(
        host="0.0.0.0",
        port=port
    )
