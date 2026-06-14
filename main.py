import asyncio
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

TOKEN = os.getenv("8724847696:AAE5pgxmb8O4N_4U6ZbZTQ6GtnxL7yWhDMA")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎥 Пришли ссылку на видео — я верну mp3")


def download_audio(url: str) -> str:
    file_id = str(uuid.uuid4())
    output = f"{file_id}.mp3"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": file_id + ".%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output


@dp.message()
async def handler(message: types.Message):
    url = message.text.strip()

    if "http" not in url:
        await message.answer("❌ Отправь ссылку на видео")
        return

    await message.answer("⏬ Скачиваю...")

    try:
        file_path = download_audio(url)

        audio = types.FSInputFile(file_path)
        await message.answer_audio(audio)

        os.remove(file_path)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
