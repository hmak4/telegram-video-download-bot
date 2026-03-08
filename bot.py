import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# লগিং সেটআপ (ত্রুটি নির্ণয়ের জন্য)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# টোকেন সেট করুন (এনভায়রনমেন্ট ভেরিয়েবল থেকে নেয়া ভালো)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8538615381:AAE_-uK9Tnu_QgC_5Tz6QhsruBZCYKULlV8")  # আপনার টোকেন বসান বা ENV এ সেট করুন

# ডাউনলোড ফোল্ডার
DOWNLOAD_PATH = "./downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# কুকিজ ফাইলের পাথ (টিকটকের জন্য) - ইউজার এক্সপোর্ট করে এখানে রাখবেন
COOKIES_FILE = "tiktok_cookies.txt"  # এই ফাইলটি বটের ডিরেক্টরিতে থাকতে হবে

# ---------- yt-dlp কনফিগারেশন ----------
BASE_OPTS = {
    'format': 'best[ext=mp4]/best',        # MP4 অগ্রাধিকার
    'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
    'merge_output_format': 'mp4',
    'quiet': True,
    'no_warnings': True,
    'socket_timeout': 30,
    'retries': 5,
    'fragment_retries': 5,
    'nocheckcertificate': True,            # SSL সার্টিফিকেট ইগনোর (ফেসবুকের জন্য)
    'extract_flat': False,
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
}

# টিকটকের জন্য আলাদা অপশন (কুকিজ + হেডার)
TIKTOK_OPTS = BASE_OPTS.copy()
TIKTOK_OPTS.update({
    'cookiefile': COOKIES_FILE,             # কুকিজ ফাইল
    'extractor_args': {'tiktok': {'app_info': '0'}},  # মোবাইল API
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
})

# ---------- হ্যান্ডলার ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম! আমি ভিডিও ডাউনলোড বট।\n"
        "যেকোনো সমর্থিত ভিডিও লিংক (ফেসবুক, টিকটক, ইউটিউব, ইনস্টাগ্রাম, টুইটার ইত্যাদি) পাঠান, আমি ডাউনলোড করে দেব।"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    # মেসেজ থেকে প্রথম URL বের করা
    urls = [word for word in text.split() if word.startswith(('http://', 'https://'))]
    if not urls:
        await update.message.reply_text("❌ কোনো বৈধ URL পাওয়া যায়নি।")
        return

    url = urls[0]
    await update.message.reply_text("⏳ ডাউনলোড শুরু হয়েছে, একটু অপেক্ষা করুন...")

    # প্ল্যাটফর্ম অনুযায়ী অপশন নির্বাচন
    if 'tiktok.com' in url:
        opts = TIKTOK_OPTS
        await update.message.reply_text("🎵 টিকটক ভিডিও শনাক্ত হয়েছে, একটু ধৈর্য ধরুন...")
    else:
        opts = BASE_OPTS
        # ফেসবুকের জন্য বাড়তি হেডার
        if 'facebook.com' in url or 'fb.watch' in url:
            opts['headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

    try:
        # ডাউনলোড (থ্রেডে চালানো)
        loop = asyncio.get_event_loop()
        filename = await loop.run_in_executor(None, download_video, url, opts)

        if not filename or not os.path.exists(filename):
            raise Exception("ফাইল ডাউনলোড হয়নি")

        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        if file_size_mb > 50:
            await update.message.reply_text(
                f"⚠️ ভিডিওটি 50MB এর বেশি ({file_size_mb:.2f}MB)। টেলিগ্রাম বট 50MB এর বেশি পাঠাতে পারে না।"
            )
            os.remove(filename)
            return

        # ভিডিও পাঠানো
        with open(filename, 'rb') as f:
            await update.message.reply_video(f, caption="✅ ডাউনলোড সম্পন্ন!")

        # ফাইল মুছে ফেলা
        os.remove(filename)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ ডাউনলোড ব্যর্থ হয়েছে।\nত্রুটি: {str(e)[:200]}")

def download_video(url, opts):
    """সিঙ্ক্রোনাস ডাউনলোড ফাংশন (থ্রেডে চলবে)"""
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # নিশ্চিত করা যে এক্সটেনশন mp4
        if not filename.endswith('.mp4'):
            filename = filename.rsplit('.', 1)[0] + '.mp4'
        return filename

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 বট চালু হয়েছে...")
    application.run_polling()

if __name__ == '__main__':
    main()
