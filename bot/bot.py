from sqlalchemy.orm import Session

from bfs import db_session
from data.user import User
import tgapi


class Bot(tgapi.Bot):
    db_sess: Session = None
    user: User = None

    @staticmethod
    def cmd_connect_db(fn):
        def wrapped(bot: Bot, args: list[str]):  # noqa: F811
            db_sess = db_session.create_session()
            bot.db_sess = db_sess
            if bot.sender is not None:
                user = User.get_by_id_tg(db_sess, bot.sender.id)
                if user is None:
                    user = User.new_from_data(db_sess, bot.sender)
            bot.user = user
            try:
                return fn(bot, args)
            finally:
                db_sess.close()
        return wrapped


@Bot.add_command("help", None)
def help(bot: Bot, args: list[str]):  # noqa: F811
    def format_cmd(cmd):
        cmd, desc = cmd
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


import bot.queue.base
import bot.queue.manage
