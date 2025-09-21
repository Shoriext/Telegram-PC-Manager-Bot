import subprocess
import os
import platform
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from PIL import ImageGrab
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("token")

print(TOKEN)


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для управления ПК.")


# Команда /shutdown
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выключаю ПК через 10 секунд...")
    try:
        system = platform.system()
        if system == "Windows":
            subprocess.run("shutdown /s /t 10", shell=True)
        elif system == "Linux" or system == "Darwin":
            subprocess.run("shutdown -h +1", shell=True)
        else:
            await update.message.reply_text("Неизвестная ОС")
    except Exception as e:
        await update.message.reply_text(f"Ошибка выключения: {e}")


# Команда /cmd
async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = " ".join(context.args)
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, encoding="cp866"
        )
        output = result.stdout + result.stderr
        if not output:
            output = "Команда выполнена, вывод пуст."
        if len(output) > 4096:
            output = output[:4090] + "\n[...]"
        await update.message.reply_text(
            f"Результат выполнения:\n```\n{output}\n```", parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка выполнения команды: {e}")


# Команда /screenshot
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Делаю скриншот...")
        # Делаем скриншот
        screenshot = ImageGrab.grab()
        # Сохраняем во временный файл
        screenshot.save("screenshot.png")
        # Отправляем в Telegram
        await update.message.reply_photo(photo=open("screenshot.png", "rb"))
        # Удаляем файл
        os.remove("screenshot.png")
    except Exception as e:
        await update.message.reply_text(f"Ошибка скриншота: {e}")


# Команда /webcam
async def webcam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Делаю запись с веб-камеры...")


# Обработчик текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Получено: " + update.message.text)


# Основная функция
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("cmd", run_cmd))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(CommandHandler("webcam", webcam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
