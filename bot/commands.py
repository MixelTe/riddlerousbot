from bot.bot import Bot
from bot.queue.base import silent_mode
from data.screamer import Screamer
import tgapi


@Bot.add_command("goida_<txt>", (("Кричалка", "[new_text] [\\s]"), None))
@Bot.cmd_connect_db
def goida(bot: Bot, args: list[str], txt: str):
    args, sl = silent_mode(bot, args)
    t = "🤟 " + bot.user.get_name() + " 🤟\n"
    if not txt:
        return t + "Тыц-тыц!"
    s = Screamer.get_by_cmd(bot.db_sess, txt)
    if len(args) > 0:
        text = " ".join(args)
        if s:
            s.update_text(bot.user, text)
        else:
            s = Screamer.new(bot.user, txt, text)
        if sl:
            return None
    text = s.text if s else txt.replace("_", " ")
    bot.sendMessage(t + text, entities=[
        tgapi.MessageEntity.blockquote(tgapi.MessageEntity.len(t), tgapi.MessageEntity.len(text)),
    ])
