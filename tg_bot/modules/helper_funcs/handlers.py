from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters

CMD_STARTERS = ("/", "!")


class CustomCommandHandler(CommandHandler):
    def __init__(self, command, callback, **kwargs):
        kwargs.pop("admin_ok", None)
        kwargs.pop("pass_args", None)
        kwargs.pop("pass_update_queue", None)
        kwargs.pop("pass_job_queue", None)
        kwargs.pop("pass_user_data", None)
        kwargs.pop("pass_chat_data", None)
        kwargs.pop("allow_edited", None)

        if isinstance(command, str):
            commands = [command]
        else:
            commands = list(command)

        expanded_commands = []
        for cmd in commands:
            cmd_clean = cmd.lstrip("/")
            expanded_commands.append(cmd_clean)
            for starter in CMD_STARTERS:
                if starter != "/":
                    expanded_commands.append(f"{starter}{cmd_clean}")

        super().__init__(expanded_commands, callback, **kwargs)


class CustomRegexHandler(MessageHandler):
    def __init__(self, pattern, callback, friendly="", **kwargs):
        kwargs.pop("pass_args", None)
        kwargs.pop("pass_update_queue", None)
        kwargs.pop("pass_job_queue", None)
        kwargs.pop("pass_user_data", None)
        kwargs.pop("pass_chat_data", None)
        kwargs.pop("pass_groups", None)
        self.friendly = friendly
        regex_filter = filters.Regex(pattern) if isinstance(pattern, str) else pattern
        super().__init__(regex_filter, callback, **kwargs)
