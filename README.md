# 🖥️ Telegram PC Manager Bot

Бот для удалённого управления компьютером через Telegram.

## 🔧 Функционал:

- `/shutdown` — выключить ПК
- `/cmd [команда]` — выполнить команду в CMD
- `/screenshot` — скриншот экрана
- `/webcam` — фото с веб-камеры
- `/upload [путь]` — отправить файл с ПК
- `/download` — загрузить файл на ПК

## 🔐 Безопасность:

Только пользователь с указанным Telegram ID может управлять ботом.

## 🚀 Установка:

1. Установи Python 3.8+
2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Создай бота через @BotFather и получи токен
4. Узнай свой Telegram ID через @userinfobot
5. Вставь токен и ID в `.env`

```
TOKEN=Ваш токен
USER_ID= Ваш Telegram ID
```

6. Запусти:

```
python bot.py
```

## ⚠️ ВНИМАНИЕ:

Используйте только на своём компьютере. Автор не несёт ответственности за возможные риски.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
