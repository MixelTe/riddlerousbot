import math

import bafser_tgapi as tgapi
from bafser import Undefined

from bot.bot import Bot
from data.queue import Queue
from data.queue_user import QueueUser
from utils import parse_int


class updateQueueLoudness:
    silent = 0
    quiet = 1
    loud = 2
    scream = 3


def updateQueue(bot: Bot, queue: Queue, loudness=updateQueueLoudness.loud):
    if loudness >= updateQueueLoudness.scream:
        tgapi.deleteMessage(queue.msg.chat_id, queue.msg.message_id)
        ok, r = bot.sendMessage(f"📝 Очередь {queue.name}:\n⏳ Обновление...")
        if not ok:
            return "Error!"

        queue.update_msg(r)
        tgapi.pinChatMessage(r.chat.id, r.message_id)

    txt = f"📝 Очередь {queue.name}:\n"
    clear_at = queue.get_parsed_clear_at()
    if clear_at:
        (_, day), _, hour, minute = clear_at
        txt += f"🧹 Очистка в {day} {hour:02}:{minute:02}" + "\n"
    txt += "-" * math.floor(len(txt) * 1.8) + "\n"
    qus = QueueUser.all_in_queue(queue.id)
    if len(qus) == 0:
        txt += "Никого в очереди"
        if queue.msg_next is not None:
            tgapi.deleteMessage(queue.msg_next.chat_id, queue.msg_next.message_id)
            queue.update_msg_next(None)
    else:
        for i, qu in enumerate(qus):
            txt += f"{i + 1}) {qu.user.get_tagname()}\n"

        if loudness >= updateQueueLoudness.quiet:
            if len(qus) > 1:
                txt_next = f"🎞 Следующие в очереди {queue.name}\n🥇-> {qus[0].user.get_tagname()}\n🥈-> {qus[1].user.get_tagname()}"
                if len(qus) == 3:
                    txt_next += "\n💤 И ещё 1 ждущий"
                elif len(qus) > 3:
                    txt_next += f"\n💤 И ещё {len(qus) - 2} ждущих"
            else:
                txt_next = f"🎞 Следующий в очереди {queue.name}\n🥇-> {qus[0].user.get_tagname()}"

            btns: list[tuple[str, str]] = []
            if len(qus) > 1:
                btns.append(("🎭 Пропуск", f"queue_pass {queue.id}"))
            btns.append(("🔴 Выйти", f"queue_exit {queue.id}"))
            btns.append(("💫 В конец", f"queue_end {queue.id}"))

            if loudness >= updateQueueLoudness.loud:
                if queue.msg_next is not None:
                    tgapi.deleteMessage(queue.msg_next.chat_id, queue.msg_next.message_id)
                ok, r = bot.sendMessage(txt_next,
                                        reply_markup=tgapi.reply_markup(btns),
                                        message_thread_id=queue.msg.message_thread_id,
                                        reply_parameters=tgapi.ReplyParameters(message_id=queue.msg.message_id))
                if not ok:
                    return "Error!"
                queue.update_msg_next(r)
            else:
                if queue.msg_next is not None:
                    tgapi.editMessageText(queue.msg_next.chat_id, queue.msg_next.message_id,
                                          txt_next, reply_markup=tgapi.reply_markup(btns))

    tgapi.editMessageText(queue.msg.chat_id, queue.msg.message_id, txt, reply_markup=tgapi.reply_markup([
        ("🟢 Встать", f"queue_enter {queue.id}"),
        ("🔴 Выйти", f"queue_exit {queue.id}"),
    ]))


def get_queue(bot: Bot, args: tgapi.BotCmdArgs) -> Queue:
    if len(args) < 1:
        tgapi.raiseBotAnswer("No queue id provided")

    id = parse_int(args[0])
    if id is None:
        tgapi.raiseBotAnswer("id is NaN")

    queue = Queue.get(bot.db_sess, id)
    if queue is None:
        tgapi.raiseBotAnswer(f"queue with id={id} doesnt exist")

    return queue


def get_queue_by_reply(bot: Bot):
    if not bot.message or not Undefined.defined(bot.message.reply_to_message):
        tgapi.raiseBotAnswer("Укажите очередь, ответив на неё")

    queue = Queue.get_by_message(bot.message.reply_to_message)
    if not queue:
        tgapi.raiseBotAnswer("Необходимо ответить на сообщение очереди (это не оно, или оно уже не действительно)")

    return queue


class update_queue_msg_if_changes():
    def __init__(self, bot: Bot, queue: Queue):
        self.bot = bot
        self.queue = queue

    def __enter__(self):
        self.first, self.second = QueueUser.first2_in_queue(self.queue.id)
        self.count = QueueUser.count_in_queue(self.queue.id)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        first, second = QueueUser.first2_in_queue(self.queue.id)
        count = QueueUser.count_in_queue(self.queue.id)
        big_changes = False
        if self.first is not None and first is not None:
            if self.first.user_id != first.user_id:
                big_changes = True
        else:
            if (self.first is None) != (first is None):
                big_changes = True
        if self.second is not None and second is not None:
            if self.second.user_id != second.user_id:
                big_changes = True
        else:
            if (self.second is None) != (second is None):
                big_changes = True
        count_changed = self.count != count
        silence = updateQueueLoudness.silent
        if count_changed:
            silence = updateQueueLoudness.quiet
        if big_changes:
            silence = updateQueueLoudness.loud
        updateQueue(self.bot, self.queue, silence)
