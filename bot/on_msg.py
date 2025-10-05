import bafser_tgapi as tgapi
from bafser import Undefined

from bot.bot import Bot
from data.msg import Msg
from data.user import User


@Bot.on_message
def on_message(bot: Bot):
    if not bot.message or not bot.sender:
        return

    if not Undefined.defined(bot.message.reply_to_message):
        return

    if bot.message.chat.type == "private" and bot.sender.username == "MixelTe":
        msg = Msg.get_by_message_id(bot.db_sess, bot.message.reply_to_message.message_id)
        if not msg or not msg.reply_to:
            return
        msg = msg.reply_to
        tgapi.copyMessage(msg.chat_id, msg.message_thread_id,
                          bot.message.chat.id, bot.message.message_id,
                          reply_parameters=tgapi.ReplyParameters(message_id=msg.message_id))
        return

    if bot.message.chat.type == "private":
        return
    if Undefined.defined(bot.message.reply_to_message.sender):
        if bot.message.reply_to_message.sender.username == tgapi.get_bot_name()[1:]:
            adm = User.get_by_username(bot.db_sess, "MixelTe")
            if not adm:
                return
            ok, msg = tgapi.forwardMessage(adm.id_tg, None, bot.message.chat.id, bot.message.message_id)
            if not ok:
                return
            msg_orig = Msg.new_from_data(bot.user, bot.message)
            Msg.new_from_data(bot.user, msg, msg_orig.id)
            return
