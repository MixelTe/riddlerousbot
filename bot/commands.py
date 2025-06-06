from bot.bot import Bot
from bot.queue.base import silent_mode
from data.screamer import Screamer
import tgapi

ME = tgapi.MessageEntity


@Bot.add_command("goida_<txt>", (("Кричалка", "[new_text] [\\s]"), None), raw_args=True)
@Bot.cmd_connect_db
def goida(bot: Bot, args: list[str], txt: str):
    sl = False
    if len(args) > 0 and args[0][-2:] == "\\s":
        _, sl = silent_mode(bot, [args[0], "\\s"])
        args[0] = args[0][:-2]
    t = "🤟 " + bot.user.get_name() + " 🤟\n"
    if not txt:
        return t + "Тыц-тыц!"
    s = Screamer.get_by_cmd(bot.db_sess, txt)
    if len(args) > 0:
        text = args[0]
        if txt == "txt":
            return None
        if s:
            s.update_text(bot.user, text)
        else:
            s = Screamer.new(bot.user, txt, text)
        if sl:
            return None
    text = s.text if s else txt.replace("_", " ")
    bot.sendMessage(t + text, entities=[
        ME.blockquote(ME.len(t), ME.len(text)),
    ])


@Bot.add_command("q", (("Цитата", "<Author>\\n<text>"), None), raw_args=True)
@Bot.cmd_connect_db
def quote(bot: Bot, args: list[str]):
    if len(args) == 0:
        return
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    parts = args[0].split("\n")
    author = "\n©" + parts[0] + "\n"
    user = "by " + bot.user.get_name()
    text = "\n".join(parts[1:])
    bot.sendMessage(text + author + user, entities=[
        ME.blockquote(0, ME.len(text)),
        ME.spoiler(ME.len(text + author), ME.len(user)),
    ])


# def all
