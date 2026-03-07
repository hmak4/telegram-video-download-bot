#!/usr/bin/env python3
"""
Telegram Multi Tool Bot
Supports: AI chat, video download, password generator, URL shortener.
Uses python-telegram-bot v20+ (async), yt-dlp, requests.
"""

import os
import logging
import secrets
import string
import asyncio
import tempfile
from pathlib import Path

import requests
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- Configuration ----------
TOKEN = os.getenv("8538615381:AAE_-uK9Tnu_QgC_5Tz6QhsruBZCYKULlV8")
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

# API endpoints
AI_API_URL = "https://api.affiliateplus.xyz/api/chatbot"  # placeholder
TINYURL_API = "https://tinyurl.com/api-create.php"

# ---------- Helper Functions ----------
async def download_video(url: str) -> str | None:
    """
    Download video from given URL using yt-dlp.
    Returns the path to the downloaded file, or None on failure.
    """
    ydl_opts = {
        'format': 'best[filesize<50M]',  # try to keep under 50MB for Telegram
        'outtmpl': str(Path(tempfile.gettempdir()) / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # yt-dlp may append different extension; we look for any file starting with title
            # simpler: take the path from the output template
            return filename
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None

def generate_password(length: int = 12) -> str:
    """Generate a strong random password."""
    if length < 4:
        length = 4
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def shorten_url(long_url: str) -> str | None:
    """Shorten URL using TinyURL."""
    try:
        resp = requests.get(TINYURL_API, params={'url': long_url}, timeout=10)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception as e:
        logger.error(f"URL shortener error: {e}")
    return None

# ---------- Command Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with command list."""
    welcome_text = (
        "🤖 Welcome to Multi Tool Bot!\n\n"
        "Available commands:\n"
        "/ai <your question> – AI Chat\n"
        "/download <video_url> – Download video (YouTube, FB, TikTok, IG)\n"
        "/password <length> – Generate strong password\n"
        "/short <long_url> – Shorten a URL\n"
        "/help – Show this help menu"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    await start(update, context)  # reuse start message

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ai command – query placeholder AI API."""
    if not context.args:
        await update.message.reply_text("Please provide a question. Example: /ai What is Python?")
        return

    question = ' '.join(context.args)
    await update.message.reply_text("🤔 Thinking...")

    try:
        # Using the placeholder API – it expects a 'message' parameter
        response = requests.get(AI_API_URL, params={'message': question}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # The API returns {"message": "response text"} according to documentation
            answer = data.get('message', 'No response from AI.')
        else:
            answer = f"AI service error (HTTP {response.status_code})"
    except Exception as e:
        logger.error(f"AI API error: {e}")
        answer = "Sorry, I couldn't reach the AI service right now."

    await update.message.reply_text(f"💬 {answer}")

async def video_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /download command – download video and send to user."""
    if not context.args:
        await update.message.reply_text("Please provide a video URL. Example: /download https://youtube.com/watch?v=...")
        return

    url = context.args[0]
    await update.message.reply_text("⏳ Downloading video, please wait... (may take a while)")

    # Run download in a thread to avoid blocking
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, download_video, url)

    if file_path and Path(file_path).exists():
        try:
            with open(file_path, 'rb') as f:
                await update.message.reply_video(video=f, caption="Here's your video 🎥")
        except Exception as e:
            logger.error(f"Failed to send video: {e}")
            await update.message.reply_text("Video downloaded but could not be sent (maybe too large).")
        finally:
            # Clean up
            Path(file_path).unlink(missing_ok=True)
    else:
        await update.message.reply_text("❌ Failed to download video. Make sure the URL is valid and the video is not too large (Telegram limit: 50MB).")

async def password_gen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /password command – generate strong password."""
    length = 12  # default
    if context.args:
        try:
            length = int(context.args[0])
            if length <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Invalid length. Using 12 characters.")

    password = generate_password(length)
    await update.message.reply_text(f"🔐 Generated Password:\n`{password}`", parse_mode='MarkdownV2')

async def url_short(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /short command – shorten a URL."""
    if not context.args:
        await update.message.reply_text("Please provide a long URL. Example: /short https://example.com")
        return

    long_url = context.args[0]
    short = shorten_url(long_url)

    if short:
        await update.message.reply_text(f"🔗 Short URL:\n{short}")
    else:
        await update.message.reply_text("❌ Failed to shorten the URL. Please check the link and try again.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text("An unexpected error occurred. Please try again later.")

# ---------- Main ----------
def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", ai_chat))
    application.add_handler(CommandHandler("download", video_download))
    application.add_handler(CommandHandler("password", password_gen))
    application.add_handler(CommandHandler("short", url_short))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start polling
    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
