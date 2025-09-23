import logging

from bafser import Log, db_session
from sqlalchemy.orm import Session

import tgapi
from data.user import User


class Bot(tgapi.Bot):
    db_sess: Session | None = None
    user: User | None = None

    @staticmethod
    def cmd_connect_db(fn: tgapi.Bot.tcmd_fn["Bot"]):
        def wrapped(bot: Bot, args: tgapi.BotCmdArgs, **kwargs: str):
            assert bot.sender
            with db_session.create_session() as db_sess:
                bot.db_sess = db_sess
                user = User.get_by_id_tg(db_sess, bot.sender.id)
                if user is None:
                    user = User.new_from_data(db_sess, bot.sender)
                if user.username != bot.sender.username:
                    old_username = user.username
                    user.username = bot.sender.username
                    Log.updated(user, user, [("username", old_username, user.username)])
                bot.user = user
                return fn(bot, args, **kwargs)
        return wrapped

    def on_message(self):
        if self.message and self.message.chat.type == "private" and self.sender:
            with db_session.create_session() as db_sess:
                try:
                    user = User.get_by_id_tg(db_sess, self.sender.id)
                    if user is None:
                        user = User.new_from_data(db_sess, self.sender)
                    if user.username != self.sender.username:
                        old_username = user.username
                        user.username = self.sender.username
                        Log.updated(user, user, [("username", old_username, user.username)])
                    if not user.is_friendly:
                        user.is_friendly = True
                        Log.updated(user, user, [("is_friendly", False, True)])
                except Exception as x:
                    logging.error(x)
        super().on_message()


@Bot.add_command("help")
def help(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    def format_cmd(v: tuple[str, tgapi.Bot.tcmd_dsc]):
        cmd, desc = v
        if isinstance(desc, str):
            return f"/{cmd} - {desc}"
        desc, hints = desc
        if isinstance(hints, str):
            hints = [hints]

        return "\n".join(f"/{cmd} {h}" for h in hints) + f"\n - {desc}"

    txt = "💠 Команды\n\n👥 Для всех:\n"
    txt += "\n".join(format_cmd(cmd) for cmd in bot.get_my_commands())
    txt += "\n\n👨‍🔧 Для админов:\n"
    txt += "\n".join(format_cmd(cmd) for cmd in bot.get_my_commands(True))
    return txt


def import_commands():
    from . import commands, tic_tac_toe
    from .queue import base, manage


import_commands()
