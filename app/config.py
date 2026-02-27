import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users.db")
PIN_LOCK_TIMEOUT = int(os.getenv("PIN_LOCK_TIMEOUT", 300))
