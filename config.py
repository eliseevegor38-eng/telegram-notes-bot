import os
from dotenv import load_dotenv

load_dotenv()

# Railway предоставляет переменные окружения, берем оттуда
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверь переменные окружения.")