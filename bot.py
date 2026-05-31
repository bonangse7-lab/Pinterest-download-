import os
import logging
import yt_dlp

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

# យក Token ពី Environment Variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

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

def main():
    try:
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN not found")

        os.makedirs("downloads", exist_ok=True)

        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                download_pinterest
            )
        )

        print("Bot Running...")

        app.run_polling()

    except Exception as e:
        print("STARTUP ERROR:", e)
        raise

if __name__ == "__main__":
    main()
