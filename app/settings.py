import os

from dotenv import load_dotenv
load_dotenv()


BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("DB_URL")
