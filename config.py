from database.db_handler import get_force_sub_channel, get_auto_delete_time, get_admins
import os
import logging
from logging.handlers import RotatingFileHandler




BOT_TOKEN = os.environ.get("BOT_TOKEN", "7796253868:AAH_rB27IvdW-jnIbWu7631QzO_DRwAbp4U")
API_ID = int(os.environ.get("API_ID", "29547761"))
API_HASH = os.environ.get("API_HASH", "b67055bfe5d0cab29e31297c453ae9a8")


OWNER_ID = int(os.environ.get("OWNER_ID", "1214348787"))
DB_URL = os.environ.get("DB_URL", "mongodb+srv://niksharma92297:redhood@cluster0.6tegn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "DBFalsh")


CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002477094584"))

FORCE_SUB_CHANNEL_1 = get_force_sub_channel(1)
FORCE_SUB_CHANNEL_2 = get_force_sub_channel(2)
FORCE_SUB_CHANNEL_3 = get_force_sub_channel(3)
FORCE_SUB_CHANNEL_4 = get_force_sub_channel(4)

FILE_AUTO_DELETE = get_auto_delete_time() or 600  # default to 600 seconds if not set  # auto delete in seconds

PORT = os.environ.get("PORT", "8083")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

try:
    SUDO_USERS = [1993048420, 5743248220, 1214348787]
    for x in (os.environ.get("SUDO_USERS", "1993048420 5743248220 1214348787 6321064549").split()):
        SUDO_USERS.append(int(x))
except ValueError:
    raise Exception("Your SUDO_USERS list does not contain valid integers.")

ADMINS = [OWNER_ID] + SUDO_USERS

try:
    admin_env = os.environ.get("ADMINS", " ".join(map(str, get_admins())))
    for x in admin_env.split():
        ADMINS.append(int(x))
except ValueError:
    raise Exception("Your Admins list does not contain valid integers.")

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False
DISABLE_CHANNEL_BUTTON = True if os.environ.get('DISABLE_CHANNEL_BUTTON', "True") == "True" else False

BOT_STATS_TEXT = "<b>BOT UPTIME :</b>\n{uptime}"

USER_REPLY_TEXT = ""

START_MSG = os.environ.get("START_MESSAGE", "<blockquote>Hello {mention}</blockquote>\n\n<blockquote>I Can Store Private Files In Specified Channel And Other Users Can Access It From Special Link</blockquote>\n<blockquote>Main channel @Animes_Station.</blockquote>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "Hello {mention}\n\n<b>You Need To Join In My Channel/Group To Use Me\n\nKindly Please Join Channel</b>")

photos = [
    "https://litter.catbox.moe/f8t3au.jpg",
    "https://litter.catbox.moe/npli8j.jpg",
    # Add more photo URLs as needed
]

ADMINS.append(OWNER_ID)
ADMINS.append(5743248220)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
