import bafser_tgapi as tgapi
from bafser import Undefined, get_datetime_now

from bot.bot import Bot
from data.curse import Curse
from data.misc import Misc
from data.msg import Msg
from data.user import User
from utils import parse_duration


@Bot.add_command()
def os418_say(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.user.is_admin() or not bot.message:
        return
    tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    if args.raw_args == "":
        return
    misc = Misc.get(bot.db_sess)
    bot.sendMessage(args.raw_args, chat_id=misc.os418_chat_id, message_thread_id=misc.os418_chat_thread_id)


@Bot.add_command()
def os418_set(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.user.is_admin() or not bot.message:
        return
    tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    misc = Misc.get(bot.db_sess)
    misc.os418_chat_id = bot.message.chat.id
    misc.os418_chat_thread_id = Undefined.default(bot.message.message_thread_id)
    bot.logger.info(f"os418_chat_id={misc.os418_chat_id} os418_chat_thread_id={misc.os418_chat_thread_id}")
    bot.db_sess.commit()


@Bot.add_command()
def os418(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.message:
        return
    misc = Misc.get(bot.db_sess)
    if (bot.message.chat.id != misc.os418_chat_id and
            Undefined.default(bot.message.message_thread_id) != misc.os418_chat_thread_id):
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
        return
    msg = args.raw_args.strip()
    if msg == "":
        return "✨ Звёзды обратили внимание на безмолвный крик"
    adm = User.get_by_username(bot.db_sess, "MixelTe")
    if not adm:
        return
    ok, msg = tgapi.forwardMessage(adm.id_tg, None, bot.message.chat.id, bot.message.message_id)
    if not ok:
        return
    msg_orig = Msg.new_from_data(bot.user, bot.message)
    Msg.new_from_data(bot.user, msg, msg_orig.id)


@Bot.add_command()
def os418_curse(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.user.is_admin():
        return

    if len(args) < 2:
        return "/os418_curse username int[m|h|d]"

    username = args[0]
    user = User.get_by_username(bot.db_sess, username)
    if not user:
        return f"unknown user: {username}"

    duration, ok = parse_duration(args[1])
    if not ok:
        return "wrong duration"

    end_date = get_datetime_now() + duration
    curse = Curse.get_by_user(user)
    if curse:
        curse.update_end_date(bot.user, end_date)
    else:
        curse = Curse.new(bot.user, user, end_date)

    return f"Applied {curse.type} curse to {user.get_tagname()} until {end_date:%Y.%m.%d %H:%M:%S}"
