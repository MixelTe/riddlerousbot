from bot.bot import Bot
from bot.queue.base import silent_mode
from data.screamer import Screamer
import tgapi


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
        tgapi.MessageEntity.blockquote(tgapi.MessageEntity.len(t), tgapi.MessageEntity.len(text)),
    ])
