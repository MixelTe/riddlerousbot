import bafser_tgapi as tgapi
from bafser import Undefined

from bot.bot import Bot
from data.msg import Msg


@Bot.on_message
def on_message(bot: Bot):
    if not bot.message or not bot.sender:
        return
    if bot.message.chat.type != "private":
        return
    if bot.sender.username != "MixelTe":
        return
    if not Undefined.defined(bot.message.reply_to_message):
        return
    msg = Msg.get_by_message_id(bot.db_sess, bot.message.reply_to_message.message_id)
    if not msg or not msg.reply_to_id:
        return
    msg = Msg.get(bot.db_sess, msg.reply_to_id)
    if not msg:
        return
    tgapi.copyMessage(msg.chat_id, msg.message_thread_id,
                      bot.message.chat.id, bot.message.message_id,
                      reply_parameters=tgapi.ReplyParameters(message_id=msg.message_id))
