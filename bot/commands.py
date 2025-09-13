from random import choice

import tgapi
from bot.bot import Bot
from bot.utils import get_users_from_msg, silent_mode, silent_mode_on
from data.screamer import Screamer
from data.tagger import Tagger

ME = tgapi.MessageEntity


@Bot.add_command("goida_<txt>", desc=("Кричалка", "[new_text] [\\s]"))
@Bot.cmd_connect_db
def goida(bot: Bot, args: tgapi.BotCmdArgs, txt: str, **_: str):
    assert bot.user
    assert bot.db_sess
    sl = False
    if args.raw_args != "" and args.raw_args[-2:] == "\\s":
        silent_mode_on(bot)
        sl = True
        args.raw_args = args.raw_args[:-2]
    t = "🤟 " + bot.user.get_name() + " 🤟\n"
    if not txt:
        return t + "Тыц-тыц!"
    s = Screamer.get_by_cmd(bot.db_sess, txt)
    if args.raw_args != "":
        if args.raw_args == "txt":
            return None
        if s:
            s.update_text(bot.user, args.raw_args)
        else:
            s = Screamer.new(bot.user, txt, args.raw_args)
        bot.logger.info(f"uid={bot.user.id} ({bot.user.get_username()}) upd cmd {txt}")
        if sl:
            return None
    text = s.text if s else txt.replace("_", " ")
    bot.sendMessage(t + text, entities=[
        ME.blockquote(ME.len(t), ME.len(text)),
    ])


@Bot.add_command("q", desc=("Цитата", "<Author>\\n<text>"))
@Bot.cmd_connect_db
def quote(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.user
    if args.raw_args == "":
        return
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    parts = args.raw_args.split("\n")
    author = "\n©" + parts[0] + "\n"
    user = "by " + bot.user.get_name()
    text = "\n".join(parts[1:])
    bot.sendMessage(text + author + user, entities=[
        ME.blockquote(0, ME.len(text)),
        ME.spoiler(ME.len(text + author), ME.len(user)),
    ])


@Bot.add_command("all<txt>_set", desc="Настроить список для вызова всех")
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def all_set(bot: Bot, args: tgapi.BotCmdArgs, txt: str, **_: str):
    if not bot.message:
        return "Call by message"
    sl = silent_mode(bot, args)
    users, err = get_users_from_msg(bot, args)
    if err:
        bot.sendMessage(err)

    Tagger.update_cmd_in_chat(bot, txt, users)
    if not sl:
        return f"✏ Изменён список команды /all{txt}\n" + "\n".join([user.get_name() for user in users])


@Bot.add_command("all<txt>", desc="Вызвать всех!")
@Bot.cmd_connect_db
def all(bot: Bot, args: tgapi.BotCmdArgs, txt: str, **_: str):
    assert bot.db_sess
    if not bot.message or not bot.chat:
        return "Call by message"
    silent_mode(bot, args)

    users = Tagger.get_all_by_cmd_in_chat(bot.db_sess, txt, bot.chat.id)
    users.sort(key=lambda u: u.user.get_tagname() + u.user.get_username())

    if len(users) == 0:
        bot.sendMessage(f"Список пуст\nсоздайте его командой: /all{txt}_set")
        return

    text = "🔔 "
    entities = []
    full_names = False
    if full_names:
        for u in users:
            utext = u.user.get_tagname()
            if u.user.username == "":
                entities.append(ME.text_mention(ME.len(text), ME.len(utext), u.user.id_tg))
            text += utext + " "
    else:
        phrase = choice([
            "Придите же люди добрые, на клич бодрый!",
            "Взываю к вам, души добрые",
            "Внимание, о граждане! Сие есть созыв не праздный, но вещий",
            "Собирайтесь, люди добрые, на призыв искренний и решительный!",
            "Откликнитесь, кому не безразлична судьба общая!",
            "Зову вас, не по прихоти, а по нужде великой!",
            "Выходи, кто не прячется! А то потом не жалуйся, что не звали!",
            "Настоящим уведомлением извещаются все заинтересованные лица о необходимости безотлагательного сбора.",
            "Ввиду текущей обстановки, доводим до вашего сведения: участие каждого не просто желательно, но строго рекомендуется.",
            "Уведомляем: игнорирование настоящего призыва может повлечь за собой неприятные последствия",
        ])
        phrase += "." * (len(users) - len(phrase))
        c = len(phrase) // len(users)
        rem = len(phrase) - c * len(users)
        for u in users:
            r = 1 if rem > 0 else 0
            rem -= 1
            utext, phrase = phrase[:c + r], phrase[c + r:]
            entities.append(ME.text_mention(ME.len(text), ME.len(utext), u.user.id_tg))
            text += utext

    bot.sendMessage(text, entities=entities)


@Bot.add_command("say")
@Bot.cmd_connect_db
def say(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.user
    if bot.user.username != "MixelTe":
        return
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    if args.raw_args == "":
        return

    return args.raw_args
