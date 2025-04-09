import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = 20948356
API_HASH = "6b202043d2b3c4db3f4ebefb06f2df12"
BOT_TOKEN = "7809892112:AAHLoiY41jC6NaAgNyq4OduESMoPjEpq2vQ"
MONGO_DB_URI = "mongodb+srv://Yumi:Yumi@yumi.inctk.mongodb.net/?retryWrites=true&w=majority&appName=Yumi"

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 60))

LOGGER_ID = -1002063031380
OWNER_ID = 7337748194
CHANNEL_ID = -1002059639505

Helpers = [7337748194, 7202110938, 6648618400]

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Roninbyrne/Yumi")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("git_token", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/PacificArc")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/phoenixXsupport")

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_VIDEO = getenv("START_VIDEO", "https://envs.sh/niT.jpg")
START_IMG_URL = getenv("START_IMG_URL", "https://te.legra.ph/file/25efe6aa029c6baea73ea.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://unitedcamps.in/Images/file_5134.jpg")
PLAYLIST_IMG_URL = "https://te.legra.ph/file/4ec5ae4381dffb039b4ef.jpg"
STATS_IMG_URL = "https://unitedcamps.in/Images/file_5135.jpg"
TELEGRAM_AUDIO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
TELEGRAM_VIDEO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://")

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://")