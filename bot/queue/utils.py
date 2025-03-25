import tgapi
from bot.bot import Bot
from data.msg import Msg
from data.queue import Queue
from data.queue_user import QueueUser
from utils import parse_int


class updateQueueLoudness:
    silent = 0
    quiet = 1
    loud = 2
    scream = 3


def updateQueue(bot: Bot, queue: Queue, loudness=updateQueueLoudness.loud):
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
            if user.username == "":
                username = f"🥷 {user.first_name} {user.last_name}"
            else:
                username = f"@{user.username}"
            txt += f"{i+1}) {username}\n"

        if loudness >= updateQueueLoudness.quiet:
            if len(qus) > 1:
                txt_next = f"🎞 Следующие в очереди {queue.name}\n🥇-> @{qus[0].user.username}\n🥈-> @{qus[1].user.username}"
                if len(qus) == 3:
                    txt_next += "\n💤 И ещё 1 ждущий"
                elif len(qus) > 3:
                    txt_next += f"\n💤 И ещё {len(qus) - 2} ждущих"
            else:
                txt_next = f"🎞 Следующий в очереди {queue.name}\n🥇-> @{qus[0].user.username}"

            btns = []
            if len(qus) > 1:
                btns.append(tgapi.InlineKeyboardButton.callback("Пропустить 1", f"queue_pass {queue.id}"))
            btns.append(tgapi.InlineKeyboardButton.callback("Выйти", f"queue_exit {queue.id}"))
            if len(qus) > 2:
                btns.append(tgapi.InlineKeyboardButton.callback("Уйти в конец", f"queue_end {queue.id}"))

            if loudness >= updateQueueLoudness.loud:
                if queue.msg_next is not None:
                    tgapi.deleteMessage(queue.msg_next.chat_id, queue.msg_next.message_id)
                    queue.msg_next = None
                ok, r = bot.sendMessage(txt_next,
                                        reply_markup=tgapi.InlineKeyboardMarkup([btns]),
                                        message_thread_id=queue.msg.message_thread_id,
                                        reply_parameters=tgapi.ReplyParameters(queue.msg.message_id))
                if not ok:
                    return "Error!"
                queue.msg_next = Msg.new_from_data(bot.user, r)
                bot.db_sess.commit()
            else:
                if queue.msg_next is not None:
                    tgapi.editMessageText(queue.msg_next.chat_id, queue.msg_next.message_id,
                                          txt_next, reply_markup=tgapi.InlineKeyboardMarkup([btns]))

    if loudness >= updateQueueLoudness.scream:
        ok, r = bot.sendMessage(f"📝 Очередь {queue.name}:\n⏳ Обновление...")
        if not ok:
            return "Error!"

        queue.msg = Msg.new_from_data(bot.user, r)
        bot.db_sess.commit()
        tgapi.pinChatMessage(r.chat.id, r.message_id)

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
        self.count = QueueUser.count_in_queue(self.bot.db_sess, self.queue.id)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        first, second = QueueUser.first2_in_queue(self.bot.db_sess, self.queue.id)
        count = QueueUser.count_in_queue(self.bot.db_sess, self.queue.id)
        big_changes = False
        if self.first is not None and first is not None:
            if self.first.user_id != first.user_id:
                big_changes = True
        else:
            if self.first is None != first is None:
                big_changes = True
        if self.second is not None and second is not None:
            if self.second.user_id != second.user_id:
                big_changes = True
        else:
            if self.second is None != second is None:
                big_changes = True
        count_changed = self.count != count
        silence = updateQueueLoudness.silent
        if count_changed:
            silence = updateQueueLoudness.quiet
        if big_changes:
            silence = updateQueueLoudness.loud
        updateQueue(self.bot, self.queue, silence)
