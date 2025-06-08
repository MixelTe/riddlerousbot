from bot.bot import Bot
from bot.queue.base import silent_mode
from data.screamer import Screamer
from data.user import User
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
        bot.logger.info(f"uid={bot.user.id} ({bot.user.get_username()}) upd cmd {txt}")
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


@Bot.add_command("all", "Вызвать всех!")
@Bot.cmd_connect_db
def all(bot: Bot, args: list[str]):
    ok, msg = bot.sendMessage("Загрузка списка группы")
    users = User.all(bot.db_sess)
    users.sort(key=lambda u: u.get_tagname() + u.get_username())
    text = ""
    entities = []
    for user in users:
        if check_is_member_of_chat(bot, user):
            utext = user.get_tagname()
            if user.username == "":
                entities.append(ME.text_mention(ME.len(text), ME.len(utext), user.id_tg))
            text += utext + " "
    if msg:
        tgapi.deleteMessage(msg.chat.id, msg.message_id)

    bot.sendMessage(text, entities=entities)


@Bot.add_command("say", None, raw_args=True)
@Bot.cmd_connect_db
def say(bot: Bot, args: list[str]):
    if bot.user.username != "MixelTe":
        return
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    if len(args) == 0:
        return

    return args[0]


def check_is_member_of_chat(bot: Bot, user: User):
    if bot.chat is None:
        return False
    bot.sender
    ok, r = tgapi.getChatMember(bot.chat.id, user.id_tg)
    if not ok:
        return False

    return r.status != "left" and r.status != "kicked"
