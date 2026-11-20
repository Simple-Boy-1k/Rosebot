from tg_bot.sample_config import Config as SampleConfig


class Config(SampleConfig):
    LOGGER = True

    # REQUIRED
    API_KEY = "8451761734:AAHg_Orrk-XhQ14PDJvClBmnyrVGIA6vl90"
    OWNER_ID = "8056191996"
    OWNER_USERNAME = ""

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = ""
    MESSAGE_DUMP = -1003941683136
    LOAD = []
    NO_LOAD = ['translation', 'rss']
    WEBHOOK = False
    URL = None

    # OPTIONAL
    SUDO_USERS = [8056191996]
    SUPPORT_USERS = [8056191996]
    WHITELIST_USERS = [8056191996]
    DONATION_LINK = None
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = True
    STRICT_GBAN = True
    STRICT_GMUTE = True
    WORKERS = 8
    BAN_STICKER = 'CAACAgQAAxkBAAEHAedfwdK1GHtSZe1Q0F0q6vWRsxL91gAC-QgAAoThEVJCGmPkkeA1_R4E'
    ALLOW_EXCL = True


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
