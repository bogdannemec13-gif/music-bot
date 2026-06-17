import os
import subprocess

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь мне MP4-видео, и я превращу его в MP3 🎵"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Просто отправь MP4-файл или видео."
    )


async def video_to_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document

    if not video:
        return

    await update.message.reply_text("Конвертирую в MP3...")

    input_file = "video.mp4"
    output_file = "audio.mp3"

    telegram_file = await video.get_file()
    await telegram_file.download_to_drive(input_file)

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            input_file,
            "-vn",
            "-acodec",
            "libmp3lame",
            output_file,
            "-y",
        ],
        check=True,
    )

    with open(output_file, "rb") as audio:
        await update.message.reply_audio(audio)

    if os.path.exists(input_file):
        os.remove(input_file)

    if os.path.exists(output_file):
        os.remove(output_file)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(
        MessageHandler(
            filters.VIDEO | filters.Document.VIDEO,
            video_to_mp3,
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
