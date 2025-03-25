from sqlalchemy.orm import Session
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


def get_queue_by_reply(bot: Bot):
    if not bot.message or not bot.message.reply_to_message:
        return None, "Укажите очередь, ответив на неё"

    queue = Queue.get_by_message(bot.db_sess, bot.message.reply_to_message)
    if not queue:
        return None, "Необходимо ответить на сообщение очереди (это не оно, или оно уже не действительно)"

    return queue, None


class update_queue_msg_if_changes():
    def __init__(self, bot: Bot, queue: Queue):
        self.bot = bot
        self.queue = queue

    def __enter__(self):
        self.first, self.second = QueueUser.first2_in_queue(self.bot.db_sess, self.queue.id)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        first, second = QueueUser.first2_in_queue(self.bot.db_sess, self.queue.id)
        changes = False
        pfirst_None = self.first is None
        nfirst_None = first is None
        psecond_None = self.second is None
        nsecond_None = self.second is None
        if not pfirst_None and not nfirst_None:
            if self.first.user_id != first.user_id:
                changes = True
        else:
            if pfirst_None != nfirst_None:
                changes = True
        if not psecond_None and not nsecond_None:
            if self.second.user_id != second.user_id:
                changes = True
        else:
            if psecond_None != nsecond_None:
                changes = True
        if changes:
            updateQueue(self.bot, self.queue)
