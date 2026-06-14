print("8724847696:AAE5pgxmb8O4N_4U6ZbZTQ6GtnxL7yWhDMA", repr(TOKEN))
print("BOT FILE STARTED")
print("8724847696:AAE5pgxmb8O4N_4U6ZbZTQ6GtnxL7yWhDMA", TOKEN)

import requests
import time
import os
import uuid
import subprocess

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

offset = 0


def get_updates():
    global offset
    r = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 10}).json()
    return r.get("result", [])


def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", data={"chat_id": chat_id, "text": text})


def send_audio(chat_id, file_path):
    with open(file_path, "rb") as f:
        requests.post(
            f"{BASE_URL}/sendAudio",
            data={"chat_id": chat_id},
            files={"audio": f}
        )


def download_audio(url):
    file_id = str(uuid.uuid4())
    output = f"{file_id}.mp3"

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "-o", f"{file_id}.%(ext)s",
        url
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output


def main():
    global offset
    print("Bot started...")

    while True:
        try:
            updates = get_updates()

            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]

                text = message.get("text", "")

                # старт
                if text == "/start":
                    send_message(chat_id, "🎵 Отправь ссылку на видео — я скачаю аудио")
                    continue

                # ссылка
                if "http" in text:
                    send_message(chat_id, "⏬ Скачиваю аудио...")

                    try:
                        file_path = download_audio(text)

                        send_audio(chat_id, file_path)

                        os.remove(file_path)

                    except Exception as e:
                        send_message(chat_id, f"❌ Ошибка: {e}")

                else:
                    send_message(chat_id, "❌ Пришли ссылку на видео")

            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
