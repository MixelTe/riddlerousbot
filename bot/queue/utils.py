import tgapi
from bot.bot import Bot
from data.msg import Msg
from data.queue import Queue
from data.queue_user import QueueUser
from utils import parse_int


def updateQueue(bot: Bot, queue: Queue):
    txt = f"📝 Очередь {queue.name}:\n"
    txt += "-" * (len(txt) - 2) + "\n"
    qus = QueueUser.all_in_queue(bot.db_sess, queue.id)
    if len(qus) == 0:
        txt += "Никого в очереди"
        if queue.msg_next is not None:
            tgapi.deleteMessage(queue.msg_next.chat_id, queue.msg_next.message_id)
            queue.msg_next = None
            bot.db_sess.commit()
    else:
        for i, qu in enumerate(qus):
            user = qu.user
            txt += f"{i+1}) @{user.username}\n"
        if len(qus) > 1:
            txt_next = f"🎞 Следующие в очереди {queue.name}\n🥇-> @{qus[0].user.username}\n🥈-> @{qus[1].user.username}"
            if len(qus) == 3:
                txt_next += f"\n💤 И ещё 1 ждущий"
            elif len(qus) > 3:
                txt_next += f"\n💤 И ещё {len(qus) - 2} ждущих"
        else:
            txt_next = f"🎞 Следующий в очереди {queue.name}\n🥇-> @{qus[0].user.username}"
        if queue.msg_next is not None:
            tgapi.deleteMessage(queue.msg_next.chat_id, queue.msg_next.message_id)
            queue.msg_next = None
        btns = []
        if len(qus) > 1:
            btns.append(tgapi.InlineKeyboardButton.callback("Пропустить 1", f"queue_pass {queue.id}"))
        btns.append(tgapi.InlineKeyboardButton.callback("Выйти", f"queue_exit {queue.id}"))
        if len(qus) > 2:
            btns.append(tgapi.InlineKeyboardButton.callback("Уйти в конец", f"queue_end {queue.id}"))
        ok, r = bot.sendMessage(txt_next, reply_markup=tgapi.InlineKeyboardMarkup([btns]), message_thread_id=queue.msg.message_thread_id)
        if not ok:
            return "Error!"
        queue.msg_next = Msg.new_from_data(bot.user, r)
        bot.db_sess.commit()

    tgapi.editMessageText(queue.msg.chat_id, queue.msg.message_id, txt, reply_markup=tgapi.InlineKeyboardMarkup([[
        tgapi.InlineKeyboardButton.callback("Встать", f"queue_enter {queue.id}"),
        tgapi.InlineKeyboardButton.callback("Выйти", f"queue_exit {queue.id}"),
    ]]))


def get_queue(bot: Bot, args: list[str]):
    if len(args) < 1:
        return None, "No queue id provided"

    id = parse_int(args[0])
    if id is None:
        return None, "id is NaN"

    queue = Queue.get(bot.db_sess, id)
    if queue is None:
        return None, f"queue with id={id} doesnt exist"

    return queue, None