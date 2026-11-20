import logging
import os
import sys

import telegram.ext as tg
from telegram.ext import ApplicationBuilder

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

# Python version check
if sys.version_info < (3, 6):
    LOGGER.error("Python 3.6 or higher is required!")
    sys.exit(1)


# Boolean environment variable helper
def get_bool(name, default=False):
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in ("true", "1", "yes", "on")


# Environment configuration
ENV = get_bool("ENV", False)

if ENV:
    TOKEN = os.environ.get("TOKEN")

    if not TOKEN:
        raise ValueError("TOKEN is missing!")

    try:
        OWNER_ID = int(os.environ.get("OWNER_ID") or "8056191996")
    except ValueError:
        raise ValueError("OWNER_ID must be a valid integer!")

    MESSAGE_DUMP = os.environ.get("MESSAGE_DUMP")
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME")

    try:
        SUDO_USERS = set(
            int(x) for x in os.environ.get("SUDO_USERS", "").split()
        )
    except ValueError:
        raise ValueError("SUDO_USERS contains invalid IDs!")

    try:
        SUPPORT_USERS = set(
            int(x) for x in os.environ.get("SUPPORT_USERS", "").split()
        )
    except ValueError:
        raise ValueError("SUPPORT_USERS contains invalid IDs!")

    try:
        WHITELIST_USERS = set(
            int(x) for x in os.environ.get("WHITELIST_USERS", "").split()
        )
    except ValueError:
        raise ValueError("WHITELIST_USERS contains invalid IDs!")

    WEBHOOK = get_bool("WEBHOOK")
    URL = os.environ.get("URL", "")
    PORT = int(os.environ.get("PORT", 5000))
    CERT_PATH = os.environ.get("CERT_PATH")

    DB_URI = os.environ.get("DATABASE_URL")

    if DB_URI and DB_URI.startswith("postgres://"):
        DB_URI = DB_URI.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    if not DB_URI:
        raise ValueError("DATABASE_URL is missing!")

    DONATION_LINK = os.environ.get("DONATION_LINK")
    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD", "").split()

    DEL_CMDS = get_bool("DEL_CMDS")
    STRICT_GBAN = get_bool("STRICT_GBAN")
    WORKERS = int(os.environ.get("WORKERS", 8))

    BAN_STICKER = os.environ.get(
        "BAN_STICKER",
        "CAACAgQAAxkBAAEHAedfwdK1GHtSZe1Q0F0q6vWRsxL91gAC-QgAAoThEVJCGmPkkeA1_R4E",
    )

    ALLOW_EXCL = get_bool("ALLOW_EXCL")
    STRICT_GMUTE = get_bool("STRICT_GMUTE")

else:
    from tg_bot.config import Development as Config

    TOKEN = Config.API_KEY

    try:
        OWNER_ID = int(Config.OWNER_ID)
    except (ValueError, TypeError):
        raise ValueError("OWNER_ID must be a valid integer!")

    MESSAGE_DUMP = Config.MESSAGE_DUMP
    OWNER_USERNAME = Config.OWNER_USERNAME

    try:
        SUDO_USERS = set(int(x) for x in Config.SUDO_USERS or [])
    except ValueError:
        raise ValueError("Invalid SUDO_USERS!")

    try:
        SUPPORT_USERS = set(int(x) for x in Config.SUPPORT_USERS or [])
    except ValueError:
        raise ValueError("Invalid SUPPORT_USERS!")

    try:
        WHITELIST_USERS = set(int(x) for x in Config.WHITELIST_USERS or [])
    except ValueError:
        raise ValueError("Invalid WHITELIST_USERS!")

    WEBHOOK = Config.WEBHOOK
    URL = Config.URL
    PORT = Config.PORT
    CERT_PATH = Config.CERT_PATH

    DB_URI = Config.SQLALCHEMY_DATABASE_URI

    if DB_URI and DB_URI.startswith("postgres://"):
        DB_URI = DB_URI.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    DONATION_LINK = Config.DONATION_LINK
    LOAD = Config.LOAD
    NO_LOAD = Config.NO_LOAD
    DEL_CMDS = Config.DEL_CMDS
    STRICT_GBAN = Config.STRICT_GBAN
    WORKERS = Config.WORKERS
    BAN_STICKER = Config.BAN_STICKER
    ALLOW_EXCL = Config.ALLOW_EXCL
    STRICT_GMUTE = Config.STRICT_GMUTE


# Owner permissions
SUDO_USERS.add(OWNER_ID)

# Existing sudo users from original code
SUDO_USERS.update({
    683538773,
    570400686,
    466337795,
    254318997,
})


# Initialize Telegram Bot (PTB v20+)
application = ApplicationBuilder().token(TOKEN).build()
updater = application.updater
dispatcher = application

SUDO_USERS = list(SUDO_USERS)
WHITELIST_USERS = list(WHITELIST_USERS)
SUPPORT_USERS = list(SUPPORT_USERS)


# Load handlers
from tg_bot.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomRegexHandler,
)

if ALLOW_EXCL:
    tg.CommandHandler = CustomCommandHandler

LOGGER.info("Miss Rose configuration loaded successfully!")
