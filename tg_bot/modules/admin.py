import html
from typing import List, Optional

from telegram import Chat, Update, User
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, filters
from telegram.helpers import mention_html

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import bot_admin, can_pin, can_promote, user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.log_channel import loggable


@bot_admin
@can_promote
@user_admin
@loggable
async def promote(update: Update, context) -> str:
    args: List[str] = context.args or []
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message
    user = update.effective_user  # type: Optional[User]

    if not chat or not message or not user:
        return ""

    user_id = await extract_user(message, args)
    if not user_id:
        await message.reply_text("mension one.... 🤷🏻‍♂.")
        return ""

    user_member = await chat.get_member(user_id)
    if user_member.status in ("administrator", "creator"):
        await message.reply_text("How am I meant to promote someone that's already an admin?")
        return ""

    if user_id == bot.id:
        await message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return ""

    bot_member = await chat.get_member(bot.id)

    await bot.promote_chat_member(
        chat_id=chat.id,
        user_id=user_id,
        can_change_info=bool(bot_member.can_change_info),
        can_post_messages=bool(bot_member.can_post_messages),
        can_edit_messages=bool(bot_member.can_edit_messages),
        can_delete_messages=bool(bot_member.can_delete_messages),
        can_restrict_members=bool(bot_member.can_restrict_members),
        can_pin_messages=bool(bot_member.can_pin_messages),
        can_promote_members=bool(bot_member.can_promote_members),
    )

    await message.reply_text("promoted🧡")
    return (
        "<b>{}:</b>"
        "\n#PROMOTED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {}".format(
            html.escape(chat.title or ""),
            mention_html(user.id, user.first_name or "Admin"),
            mention_html(user_member.user.id, user_member.user.first_name or "User"),
        )
    )


@bot_admin
@can_promote
@user_admin
@loggable
async def demote(update: Update, context) -> str:
    args: List[str] = context.args or []
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message
    user = update.effective_user  # type: Optional[User]

    if not chat or not message or not user:
        return ""

    user_id = await extract_user(message, args)
    if not user_id:
        await message.reply_text("mension one.... 🤷🏻‍♂.")
        return ""

    user_member = await chat.get_member(user_id)
    if user_member.status == "creator":
        await message.reply_text("i cant ban creator of the group.... 😬")
        return ""

    if user_member.status != "administrator":
        await message.reply_text("Can't demote what wasn't promoted!")
        return ""

    if user_id == bot.id:
        await message.reply_text("I can't demote myself! Get an admin to do it for me.")
        return ""

    try:
        await bot.promote_chat_member(
            chat_id=int(chat.id),
            user_id=int(user_id),
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )
        await message.reply_text("Successfully demoted!")
        return (
            "<b>{}:</b>"
            "\n#DEMOTED"
            "\n<b>Admin:</b> {}"
            "\n<b>User:</b> {}".format(
                html.escape(chat.title or ""),
                mention_html(user.id, user.first_name or "Admin"),
                mention_html(user_member.user.id, user_member.user.first_name or "User"),
            )
        )
    except BadRequest:
        await message.reply_text(
            "Could not demote. I might not be admin, or the admin status was appointed by another "
            "user, so I can't act upon them!"
        )
        return ""


@bot_admin
@can_pin
@user_admin
@loggable
async def pin(update: Update, context) -> str:
    args: List[str] = context.args or []
    bot = context.bot
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message

    if not chat or not user or not message:
        return ""

    is_group = chat.type not in ("private", "channel")
    prev_message = message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() in ("notify", "loud", "violent")
        )

    if prev_message and is_group:
        try:
            await bot.pin_chat_message(
                chat_id=chat.id,
                message_id=prev_message.message_id,
                disable_notification=is_silent,
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        return (
            "<b>{}:</b>"
            "\n#PINNED"
            "\n<b>Admin:</b> {}".format(
                html.escape(chat.title or ""),
                mention_html(user.id, user.first_name or "Admin"),
            )
        )

    return ""


@bot_admin
@can_pin
@user_admin
@loggable
async def unpin(update: Update, context) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]

    if not chat or not user:
        return ""

    try:
        await bot.unpin_chat_message(chat_id=chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    return (
        "<b>{}:</b>"
        "\n#UNPINNED"
        "\n<b>Admin:</b> {}".format(
            html.escape(chat.title or ""),
            mention_html(user.id, user.first_name or "Admin"),
        )
    )


@bot_admin
@user_admin
async def invite(update: Update, context):
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message

    if not chat or not message:
        return

    if chat.username:
        await message.reply_text(chat.username)
    elif chat.type in (Chat.SUPERGROUP, Chat.CHANNEL):
        bot_member = await chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = await bot.export_chat_invite_link(chat.id)
            await message.reply_text(invitelink)
        else:
            await message.reply_text("I don't have access to the invite link, try changing my permissions!")
    else:
        await message.reply_text("I can only give you invite links for supergroups and channels, sorry!")


async def adminlist(update: Update, context):
    chat = update.effective_chat
    message = update.effective_message

    if not chat or not message:
        return

    administrators = await chat.get_administrators()
    text = "Admins in *{}*:".format(chat.title or "this chat")

    for admin in administrators:
        user = admin.user
        status = admin.status
        full_name = (user.first_name or "") + (" " + user.last_name if user.last_name else "")
        name = "[{}](tg://user?id={})".format(full_name.strip() or "User", user.id)
        if status == "creator":
            text += "\n 🔱 Creator:"
            text += "\n` • `{} \n\n 🔰 Admin:".format(name)

    for admin in administrators:
        user = admin.user
        status = admin.status
        full_name = (user.first_name or "") + (" " + user.last_name if user.last_name else "")
        name = "[{}](tg://user?id={})".format(full_name.strip() or "User", user.id)
        if status == "administrator":
            text += "\n` • `{}".format(name)

    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def __chat_settings__(chat_id, user_id):
    member = await dispatcher.bot.get_chat_member(chat_id, user_id)
    return "You are *admin*: `{}`".format(member.status in ("administrator", "creator"))


__help__ = """
 - /adminlist: list of admins in the chat

*Admin only:*
 - /pin: silently pins the message replied to - add 'loud' or 'notify' to give notifs to users.
 - /unpin: unpins the currently pinned message
 - /invitelink: gets invitelink
 - /promote: promotes the user replied to
 - /demote: demotes the user replied to
"""

__mod_name__ = "Admin"

PIN_HANDLER = CommandHandler("pin", pin, filters=filters.ChatType.GROUPS)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=filters.ChatType.GROUPS)

INVITE_HANDLER = CommandHandler("invitelink", invite, filters=filters.ChatType.GROUPS)

PROMOTE_HANDLER = CommandHandler("promote", promote, filters=filters.ChatType.GROUPS)
DEMOTE_HANDLER = CommandHandler("demote", demote, filters=filters.ChatType.GROUPS)

ADMINLIST_HANDLER = DisableAbleCommandHandler("adminlist", adminlist, filters=filters.ChatType.GROUPS)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
