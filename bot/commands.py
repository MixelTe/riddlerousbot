from random import choice

import bafser_tgapi as tgapi

from bot.bot import Bot
from bot.utils import get_users_from_msg, silent_mode, silent_mode_on
from data.checker import Checker
from data.msg import Msg
from data.screamer import Screamer
from data.tagger import Tagger
from data.user import User


@Bot.add_command()
def start(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    for chk in Checker.all_by_user(bot.user):
        users = Tagger.get_all_by_cmd_in_chat(chk.cmd, chk.msg.chat_id)
        users.sort(key=lambda u: u.user.get_tagname() + u.user.get_username())
        msg, nof_users, reply_markup = all_check_msg(users)
        text, entities = msg.build()
        if len(nof_users) == 0:
            tgapi.editMessageText(chk.msg.chat_id, chk.msg.message_id, "🔔 Все познакомились с ботом лично!")
        else:
            tgapi.editMessageText(chk.msg.chat_id, chk.msg.message_id, text, entities=entities, reply_markup=reply_markup)
        chk.delete()
    return "Приятно познакомиться"


@Bot.add_command("goida_<txt>", desc=("Кричалка", "[new_text] [\\s]"))
def goida(bot: Bot, args: tgapi.BotCmdArgs, txt: str, **_: str):
    sl = False
    if args.raw_args != "" and args.raw_args[-2:] == "\\s":
        silent_mode_on(bot)
        sl = True
        args.raw_args = args.raw_args[:-2]
    t = "🤟 " + bot.user.get_name() + " 🤟\n"
    if not txt:
        return t + "Тыц-тыц!"
    s = Screamer.get_by_cmd(txt)
    if args.raw_args != "":
        if args.raw_args == "txt":
            return None
        if s:
            s.update_text(args.raw_args)
        else:
            s = Screamer.new(txt, args.raw_args)
        bot.logger.info(f"uid={bot.user.id} ({bot.user.get_username()}) upd cmd {txt}")
        if sl:
            return None
    text = s.text if s else txt.replace("_", " ")
    return tgapi.build_msg(t).blockquote(text).build()


@Bot.add_command("q", desc=("Цитата", "<Author>\\n<text>"))
def quote(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if args.raw_args == "":
        return "📖 Для отправки цитаты напишите: \n/q Имя автора\nТекст цитаты с новой строки"
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    parts = args.raw_args.split("\n")
    author = "\n©" + parts[0] + "\n"
    user = "by " + bot.user.get_name()
    text = "\n".join(parts[1:])
    return tgapi.build_msg().blockquote(text).text(author).spoiler(user).build()


@Bot.add_command("all<txt>_set", desc="Настроить список для вызова всех")
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


@Bot.add_command("all<txt>_check", desc="Проверить, всех ли может тегать бот")
@Bot.cmd_for_admin
def all_check(bot: Bot, args: tgapi.BotCmdArgs, txt: str, **_: str):
    if not bot.message or not bot.chat:
        return "Call by message"
    sl = silent_mode(bot, args)

    users = Tagger.get_all_by_cmd_in_chat(txt, bot.chat.id)
    users.sort(key=lambda u: u.user.get_tagname() + u.user.get_username())

    if len(users) == 0:
        return f"Список пуст\nсоздайте его командой: /all{txt}_set"

    msg, nof_users, reply_markup = all_check_msg(users)
    if len(nof_users) == 0:
        if sl:
            return
        return "Всех можно тегать!"

    ok, msg = bot.sendMessage(msg, reply_markup=reply_markup)
    if not ok:
        return "Error!"
    msg = Msg.new_from_data(bot.user, msg)
    for user in nof_users:
        Checker.new(msg, user, cmd=txt, commit=False)
    bot.db_sess.commit()


def all_check_msg(users: list[Tagger]):
    msg = tgapi.build_msg("🔔 Для корректной работы команды /all, просим вас нажать на кнопку:\n")
    nof_users: list[User] = []
    for u in users:
        if not u.user.is_friendly:
            nof_users.append(u.user)
            utext = u.user.get_tagname()
            if u.user.username == "":
                msg.text_mention(utext, u.user.id_tg)
            else:
                msg.text(utext)
            msg.text(" ")
    reply_markup = tgapi.reply_markup([
        tgapi.InlineKeyboardButton.open_url("Тык!", f"https://t.me/{tgapi.get_bot_name()[1:]}?start=checker")
    ])
    return msg, nof_users, reply_markup


@Bot.add_command("all<txt>", desc="Вызвать всех!")
def all(bot: Bot, args: tgapi.BotCmdArgs, txt: str, **_: str):
    if not bot.message or not bot.chat:
        return "Call by message"
    silent_mode(bot, args)

    users = Tagger.get_all_by_cmd_in_chat(txt, bot.chat.id)
    users.sort(key=lambda u: u.user.get_tagname() + u.user.get_username())

    if len(users) == 0:
        return f"Список пуст\nсоздайте его командой: /all{txt}_set"

    msg = tgapi.build_msg("🔔 ")
    full_names = False
    if full_names:
        for u in users:
            utext = u.user.get_tagname()
            if u.user.username == "":
                msg.text_mention(utext, u.user.id_tg)
            else:
                msg.text(utext)
            msg.text(" ")
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
            msg.text_mention(utext, u.user.id_tg)

    return msg.build()


@Bot.add_command()
def say(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.user.is_admin():
        return
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    if args.raw_args == "":
        return

    return args.raw_args
