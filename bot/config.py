import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/user.db")
IMAGES_PATH = os.getenv("IMAGES_PATH", "images")
BOT_TOKEN = os.getenv("BOT_TOKEN")
