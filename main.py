import os
import asyncio
import subprocess

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

user_links = {}


# ─────────────────────────────
# START
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📎 Отправь ссылку на видео\n"
        "Я дам выбор: скачать видео / музыку / конвертировать"
    )


# ─────────────────────────────
# ПОЛУЧЕНИЕ ССЫЛКИ
# ─────────────────────────────
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not url.startswith("http"):
        await update.message.reply_text("❌ Это не ссылка")
        return

    user_links[update.message.chat_id] = url

    keyboard = [
        [
            InlineKeyboardButton("📹 Видео", callback_data="video"),
            InlineKeyboardButton("🎵 Музыка", callback_data="audio"),
        ],
        [
            InlineKeyboardButton("🔄 Конвертировать в MP3", callback_data="convert_mp3"),
        ]
    ]

    await update.message.reply_text(
        "Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────
# СКАЧИВАНИЕ
# ─────────────────────────────
def download_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "video.mp4"


def download_audio(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "audio.mp3"


# ─────────────────────────────
# КОНВЕРТАЦИЯ
# ─────────────────────────────
def convert_to_mp3(file):
    out = "converted.mp3"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", file,
        "-vn",
        "-b:a", "192k",
        out
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return out


# ─────────────────────────────
# CALLBACK КНОПОК
# ─────────────────────────────
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mode = query.data
    chat_id = query.message.chat_id

    url = user_links.get(chat_id)

    if not url:
        await query.message.reply_text("❌ Сначала отправь ссылку")
        return

    await query.message.reply_text("⏳ Обрабатываю...")

    loop = asyncio.get_event_loop()

    # ── ВИДЕО ──
    if mode == "video":
        file = await loop.run_in_executor(None, download_video, url)
        await query.message.reply_video(video=open(file, "rb"))
        os.remove(file)

    # ── МУЗЫКА ──
    elif mode == "audio":
        file = await loop.run_in_executor(None, download_audio, url)
        await query.message.reply_audio(audio=open(file, "rb"))
        os.remove(file)

    # ── КОНВЕРТАЦИЯ ──
    elif mode == "convert_mp3":
        file = await loop.run_in_executor(None, download_video, url)
        converted = await loop.run_in_executor(None, convert_to_mp3, file)

        await query.message.reply_audio(audio=open(converted, "rb"))

        os.remove(file)
        os.remove(converted)


# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    if not TOKEN:
        print("BOT_TOKEN не найден")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    
