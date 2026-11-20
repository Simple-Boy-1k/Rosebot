import importlib
import re
from typing import List, Optional

from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Update, User
from telegram.constants import ParseMode
from telegram.error import BadRequest, ChatMigrated, Forbidden, NetworkError, TelegramError, TimedOut
from telegram.ext import (
    ApplicationHandlerStop,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

from tg_bot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    application,
)
from tg_bot.modules import ALL_MODULES
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.misc import paginate_modules

BOT_NAME = "Rose"

PM_START_TEXT = """
Hey there! My name is *{}*, I'm here to help you manage your groups! Hit /help to find out more about how to use me to my full potential.

Join my [news channel](https://t.me/ProIndians) to get information on all the latest updates.
"""

HELP_STRINGS = """
Hey! My name is *{}*. I am a group management bot, here to help you get around and keep the order in your groups!
I have lots of handy features, such as flood control, a warning system, a note keeping system, and even predetermined replies on certain keywords.

*Helpful commands*:
- /start: Starts me! You've probably already used this.
- /help: Sends this message; I'll tell you more about myself!
- /donate: Gives you info on how to support me and my creator.

{}
All commands can be used with the following: / !
""".format(
    BOT_NAME,
    ""
    if not ALLOW_EXCL
    else "If you have any bugs or questions on how to use me, have a look at my [Group](https://t.me/ProHelpDesk), or head to @ProIndians.",
)

DONATE_STRING = """Heya, glad to hear you want to donate!
It took lots of work for [my creator](t.me/SonOfLars) to get me to where I am now, and every donation helps \
motivate him to make me even better. All the donation money will go to a better VPS to host me, and/or beer \
(see his bio!). He's just a poor student, so every little helps!
There are two ways of paying him; [PayPal](paypal.me/PaulSonOfLars), or [Monzo](monzo.me/paulnionvestergaardlarsen)."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("tg_bot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


async def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await application.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def test(update: Update, context):
    if update.effective_message:
        await update.effective_message.reply_text("This person edited a message")
        print(update.effective_message)


async def start(update: Update, context):
    args: List[str] = context.args or []
    bot = context.bot
    if update.effective_chat and update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                await send_help(update.effective_chat.id, HELP_STRINGS)

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                if match:
                    chat = await bot.get_chat(match.group(1))
                    if update.effective_user and is_user_admin(chat, update.effective_user.id):
                        await send_settings(match.group(1), update.effective_user.id, False)
                    elif update.effective_user:
                        await send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                await IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            await update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(bot.first_name or BOT_NAME)),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Add me to your chat!",
                                url="https://t.me/{}?startgroup=true".format(bot.username),
                            )
                        ]
                    ]
                ),
            )
    elif update.effective_message:
        await update.effective_message.reply_text("Hello all Join @ProIndians.")


async def error_callback(update: object, context):
    error = context.error
    try:
        if error:
            raise error
    except Forbidden:
        print("no nono1")
        print(error)
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)
    except TimedOut:
        print("no nono3")
    except NetworkError:
        print("no nono4")
    except ChatMigrated as err:
        print("no nono5")
        print(err)
    except TelegramError:
        print(error)


async def help_button(update: Update, context):
    query = update.callback_query
    if not query:
        return
    mod_match = re.match(r"help_module\((.+?)\)", query.data or "")
    prev_match = re.match(r"help_prev\((.+?)\)", query.data or "")
    next_match = re.match(r"help_next\((.+?)\)", query.data or "")
    back_match = re.match(r"help_back", query.data or "")
    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(HELPABLE[module].__mod_name__)
                + HELPABLE[module].__help__
            )
            await query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.reply_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.reply_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            await query.message.reply_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            )

        await query.answer()
        await query.message.delete()
    except BadRequest as excp:
        if excp.message in ("Message is not modified", "Query_id_invalid", "Message can't be deleted"):
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))


async def get_help(update: Update, context):
    chat: Optional[Chat] = update.effective_chat
    msg = update.effective_message
    if not chat or not msg:
        return
    args = (msg.text or "").split(None, 1)

    if chat.type != Chat.PRIVATE:
        await msg.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="https://t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(HELPABLE[module].__mod_name__)
            + HELPABLE[module].__help__
        )
        await send_help(
            chat.id,
            text,
            InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="help_back")]]),
        )

    else:
        await send_help(chat.id, HELP_STRINGS)


async def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            await application.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await application.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        if CHAT_SETTINGS:
            chat = await application.bot.get_chat(chat_id)
            await application.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            await application.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


async def settings_button(update: Update, context):
    query = update.callback_query
    user: Optional[User] = update.effective_user
    if not query or not user:
        return
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data or "")
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data or "")
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data or "")
    back_match = re.match(r"stngs_back\((.+?)\)", query.data or "")
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = await context.bot.get_chat(chat_id)
            text = (
                "*{}* has the following settings for the *{}* module:\n\n".format(
                    escape_markdown(chat.title or ""),
                    CHAT_SETTINGS[module].__mod_name__,
                )
                + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            )
            await query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="stngs_back({})".format(chat_id))]]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = await context.bot.get_chat(chat_id)
            await query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = await context.bot.get_chat(chat_id)
            await query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = await context.bot.get_chat(chat_id)
            await query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title or "")),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)),
            )

        await query.answer()
        await query.message.delete()
    except BadRequest as excp:
        if excp.message in ("Message is not modified", "Query_id_invalid", "Message can't be deleted"):
            pass
        else:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


async def get_settings(update: Update, context):
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg = update.effective_message
    if not chat or not user or not msg:
        return

    if chat.type != Chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            await msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="https://t.me/{}?start=stngs_{}".format(context.bot.username, chat.id),
                            )
                        ]
                    ]
                ),
            )
    else:
        await send_settings(chat.id, user.id, True)


async def donate(update: Update, context):
    msg = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    if not msg or not chat or not msg.from_user:
        return
    user = msg.from_user

    if chat.type == "private":
        await msg.reply_text(
            DONATE_STRING,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

        if OWNER_ID != 254318997 and DONATION_LINK:
            await msg.reply_text(
                "You can also donate to the person currently running me [here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            await context.bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            await msg.reply_text("I've PM'ed you about donating to my creator!")
        except Forbidden:
            await msg.reply_text("Contact me in PM first to get donation information.")


async def migrate_chats(update: Update, context):
    msg = update.effective_message
    if not msg or not update.effective_chat:
        return
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise ApplicationHandlerStop


def main():
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")
    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(settings_handler)
    application.add_handler(help_callback_handler)
    application.add_handler(settings_callback_handler)
    application.add_handler(migrate_handler)
    application.add_handler(donate_handler)

    if WEBHOOK and URL:
        LOGGER.info("Using webhooks.")
        webhook_url = URL.rstrip("/") + "/" + TOKEN
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url,
            cert=CERT_PATH,
        )
    else:
        LOGGER.info("Using long polling.")
        application.run_polling(poll_interval=1.0, timeout=15)


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main()
