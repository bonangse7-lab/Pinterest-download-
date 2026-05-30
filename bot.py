import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8825680908:AAGtIitkyTME5DA8gFGquhA6KuOqfoNSML8"

async def download_pinterest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "pinterest.com" not in url and "pin.it" not in url:
        await update.message.reply_text("សូមផ្ញើ Pinterest Video Link")
        return

    try:
        ydl_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "mp4/best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption="Pinterest Video Downloaded ✅"
        )

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    os.makedirs("downloads", exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_pinterest)
    )

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
