import subprocess
import os
import cv2
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

TOKEN = os.getenv("TOKEN")
USER_ID = int(os.getenv("USER_ID"))


# Функция проверки пользователя
def is_user_allowed(user_id):
    return user_id == USER_ID


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ У тебя нет доступа к этому боту.")
        return
    await update.message.reply_text(
        "✅ Доступ разрешён. Доступные команды:\n"
        "/shutdown — выключить ПК\n"
        "/cmd [команда] — выполнить команду\n"
        "/screenshot — скриншот экрана\n"
        "/webcam — фото с веб-камеры\n"
        "/upload [путь] — отправить файл\n"
        "/download — загрузить файл"
    )


# Универсальный декоратор для проверки доступа
def check_access(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_user_allowed(user_id):
            await update.message.reply_text("❌ У тебя нет доступа к этой команде.")
            return
        await func(update, context)

    return wrapper


# Команда /upload [путь_к_файлу]
@check_access
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /upload [путь_к_файлу]")
        return

    file_path = " ".join(context.args)
    if not os.path.exists(file_path):
        await update.message.reply_text("Файл не найден")
        return

    try:
        await update.message.reply_document(document=open(file_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Ошибка отправки файла: {e}")


# Команда /download - принимает файл, отправленный пользователем
@check_access
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text(
            "Пожалуйста, отправьте файл как документ (не фото)"
        )
        return

    try:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
        await file.download_to_drive(file_name)
        await update.message.reply_text(f"Файл сохранён как: {file_name}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка загрузки файла: {e}")


# Команда /webcam
@check_access
async def webcam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Делаю фото с веб-камеры...")
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if not ret:
            await update.message.reply_text("Не удалось получить изображение с камеры")
            cap.release()
            return
        cap.release()
        cv2.imwrite("webcam.jpg", frame)
        await update.message.reply_photo(photo=open("webcam.jpg", "rb"))
        os.remove("webcam.jpg")
    except Exception as e:
        await update.message.reply_text(f"Ошибка веб-камеры: {e}")


# Команда /screenshot
@check_access
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Делаю скриншот...")
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        await update.message.reply_photo(photo=open("screenshot.png", "rb"))
        os.remove("screenshot.png")
    except Exception as e:
        await update.message.reply_text(f"Ошибка скриншота: {e}")


# Команда /shutdown
@check_access
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выключаю ПК через 10 секунд...")
    try:
        system = platform.system()
        if system == "Windows":
            subprocess.run("shutdown /s /t 10", shell=True)
        elif system == "Linux" or system == "Darwin":
            subprocess.run("shutdown -h +1", shell=True)
    except Exception as e:
        await update.message.reply_text(f"Ошибка выключения: {e}")


# Команда /cmd
@check_access
async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = " ".join(context.args)
    if not command:
        await update.message.reply_text("Использование: /cmd [команда]")
        return

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


# Обработчик документов для загрузки
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        return
    if update.message.document:
        await download(update, context)


# Обработчик текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ У тебя нет доступа к этому боту.")
        return
    await update.message.reply_text("Получено: " + update.message.text)


# Основная функция
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("cmd", run_cmd))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(CommandHandler("webcam", webcam))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(CommandHandler("download", download))

    # Обработчик документов
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
