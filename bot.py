import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("8538615381:AAE_-uK9Tnu_QgC_5Tz6QhsruBZCYKULlV8")

DOWNLOAD_PATH = "./downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

COOKIES_FILE = "tiktok_cookies.txt"

BASE_OPTS = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
    'merge_output_format': 'mp4',
    'quiet': True,
    'no_warnings': True,
    'socket_timeout': 30,
    'retries': 5,
    'fragment_retries': 5,
    'nocheckcertificate': True,
}

TIKTOK_OPTS = BASE_OPTS.copy()
TIKTOK_OPTS.update({
    'cookiefile':  tiktok_cookies.txt,
    'headers': {
        'User-Agent': 'Mozilla/5.0'
    }
})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n"
        "ভিডিও লিংক পাঠান (TikTok / YouTube / Facebook / Instagram)"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    urls = [word for word in text.split() if word.startswith(('http://', 'https://'))]

    if not urls:
        await update.message.reply_text("❌ কোনো URL পাওয়া যায়নি")
        return

    url = urls[0]

    await update.message.reply_text("⏳ ডাউনলোড হচ্ছে...")

    if 'tiktok.com' in url:
        opts = TIKTOK_OPTS.copy()
    else:
        opts = BASE_OPTS.copy()

    try:
        loop = asyncio.get_event_loop()
        filename = await loop.run_in_executor(None, download_video, url, opts)

        if not filename or not os.path.exists(filename):
            raise Exception("ডাউনলোড ব্যর্থ হয়েছে")

        size = os.path.getsize(filename) / (1024 * 1024)

        if size > 50:
            await update.message.reply_text("⚠️ ভিডিও 50MB এর বেশি")
            os.remove(filename)
            return

        with open(filename, 'rb') as f:
            await update.message.reply_video(f)

        os.remove(filename)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"❌ Error:\n{str(e)[:200]}")

def download_video(url, opts):

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        if not filename.endswith('.mp4'):
            filename = filename.rsplit('.', 1)[0] + '.mp4'

        return filename

def main():

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")

    application.run_polling()

if __name__ == "__main__":
    main()
