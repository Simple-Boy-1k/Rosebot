import os

from tg_bot.sample_config import Config as SampleConfig

# Safe defaults so missing Heroku Config Vars never crash int() or clients
API_ID = int(os.environ.get("API_ID") or "0")
API_HASH = os.environ.get("API_HASH") or ""


class Config(SampleConfig):
    LOGGER = True

    # REQUIRED
    API_KEY = os.environ.get("TOKEN") or "8451761734:AAHg_Orrk-XhQ14PDJvClBmnyrVGIA6vl90"
    OWNER_ID = os.environ.get("OWNER_ID") or "8056191996"
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME") or "Sarkar_owner1k"
    API_ID = int(os.environ.get("API_ID") or "31551910")
    API_HASH = os.environ.get("API_HASH") or "c2e8e7946d5e4ea947d44b674008f33e"

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///rosebot.db"
    MESSAGE_DUMP = -1003941683136
    LOAD = []
    NO_LOAD = ["translation", "rss"]
    WEBHOOK = False
    URL = None

    # OPTIONAL
    SUDO_USERS = [8056191996]
    SUPPORT_USERS = [8056191996]
    WHITELIST_USERS = [8056191996]
    DONATION_LINK = None
    CERT_PATH = None
    PORT = int(os.environ.get("PORT", 5000))
    DEL_CMDS = True
    STRICT_GBAN = True
    STRICT_GMUTE = True
    WORKERS = 8
    BAN_STICKER = "CAACAgQAAxkBAAEHAedfwdK1GHtSZe1Q0F0q6vWRsxL91gAC-QgAAoThEVJCGmPkkeA1_R4E"
    ALLOW_EXCL = True


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
