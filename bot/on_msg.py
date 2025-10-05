import bafser_tgapi as tgapi
from bafser import Undefined, get_datetime_now

from bot.bot import Bot
from data.curse import Curse
from data.msg import Msg
from data.user import User
from utils import duration_to_str, os418_curse_apply_silence


@Bot.on_message
def on_message(bot: Bot):
    os418_answer(bot)
    os418_question(bot)
    os418_curse(bot)


def os418_answer(bot: Bot):
    if not bot.message or not bot.sender:
        return
    if not Undefined.defined(bot.message.reply_to_message):
        return
    if bot.message.chat.type != "private" and bot.sender.username != "MixelTe":
        return

    msg = Msg.get_by_message_id(bot.db_sess, bot.message.reply_to_message.message_id)
    if not msg or not msg.reply_to:
        return
    msg = msg.reply_to
    tgapi.copyMessage(msg.chat_id, msg.message_thread_id,
                      bot.message.chat.id, bot.message.message_id,
                      reply_parameters=tgapi.ReplyParameters(message_id=msg.message_id))


def os418_question(bot: Bot):
    if not bot.message:
        return
    if bot.message.chat.type == "private":
        return
    if not Undefined.defined(bot.message.reply_to_message):
        return
    if not Undefined.defined(bot.message.reply_to_message.sender):
        return
    if bot.message.reply_to_message.sender.username != tgapi.get_bot_name()[1:]:
        return
    adm = User.get_by_username(bot.db_sess, "MixelTe")
    if not adm:
        return
    ok, msg = tgapi.forwardMessage(adm.id_tg, None, bot.message.chat.id, bot.message.message_id)
    if not ok:
        return
    msg_orig = Msg.new_from_data(bot.user, bot.message)
    Msg.new_from_data(bot.user, msg, msg_orig.id)


def os418_curse(bot: Bot):
    if not bot.message or not bot.sender:
        return
    if bot.message.text == "":
        return

    curse = Curse.get_by_user(bot.user)
    if not curse:
        return
    now = get_datetime_now().replace(tzinfo=None)
    if curse.end_date < now:
        curse.delete(bot.user)
        return

    tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    msg = tgapi.build_msg()
    msg.italic(f"Из тишины доносится голос {bot.user.get_username()}\n")
    msg.blockquote(os418_curse_apply_silence(bot.message.text))
    msg.spoiler(f"🫥 Проклятье спадёт через {duration_to_str(curse.end_date - now)}")
    bot.sendMessage(msg)
