from typing import override

from bafser import Log
from sqlalchemy.orm import Session

import tgapi
from data.user import User


class Bot(tgapi.BotWithDB[User]):
    @override
    def get_user(self, db_sess: Session, sender: tgapi.User) -> User:
        user = User.get_by_id_tg(db_sess, sender.id)
        if user is None:
            user = User.new_from_data(db_sess, sender)
        if user.username != sender.username:
            old_username = user.username
            user.username = sender.username
            Log.updated(user, user, [("username", old_username, user.username)])
        if self.message and self.message.chat.type == "private":
            if not user.is_friendly:
                user.is_friendly = True
                Log.updated(user, user, [("is_friendly", False, True)])
        return user


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
