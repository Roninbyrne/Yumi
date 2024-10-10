import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Configuration for Telegram bot and MongoDB connection
API_ID = 
API_HASH = ""
BOT_TOKEN = ""
MONGO_DB_URI = "mongodb+srv://projectarona:projectarona@projectarona.f2ba1.mongodb.net/?retryWrites=true&w=majority&appName=projectarona"

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 60))
LOGGER_ID = -1002063031380
OWNER_ID = 7337748194
CHANNEL_ID = -1002059639505

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Roninbyrne/combo")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("", None)

SUPPORT_CHANNEL = "https://t.me/mystic_movies"
SUPPORT_CHAT = "https://t.me/mystic_legion"

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_VIDEO = getenv("START_VIDEO", "https://telegra.ph/file/e656b1c788b6c8bcd604e.mp4")
PING_IMG_URL = getenv("PING_IMG_URL", "https://graph.org//file/fc5c4b52bee5a514bcc14.mp4")

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://")

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://")