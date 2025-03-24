from sqlalchemy.orm import Session

from bfs import db_session
from data.msg import Msg
from data.queue_user import QueueUser
from data.user import User
from data.queue import Queue
import tgapi
from utils import parse_int


class Bot(tgapi.Bot):
    db_sess: Session = None
    user: User = None

    def before_process_update(self, tguser: tgapi.User):
        db_sess = db_session.create_session()
        user = User.get_by_id_tg(db_sess, tguser.id)
        if user is None:
            user = User.new_from_data(db_sess, tguser)
        self.db_sess = db_sess
        self.user = user

    def after_process_update(self):
        self.db_sess.close()


@Bot.add_command("new_queue", "Создать новую очередь")
def new_queue(bot: Bot, args: list[str]):
    if len(args) < 1:
        return "Укажите имя очереди\nUsage: /new_queue <name>"
    name = " ".join(args)
    ok, r = bot.sendMessage(f"📝 Очередь {name}:\n⏳ Создание...", message_thread_id=bot.message.message_thread_id)
    if not ok:
        return "Error!"

    queue = Queue.new_by_message(bot.db_sess, r, name)
    updateQueue(bot, queue)


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
            if len(qus) > 2:
                txt_next += f"\n💤 И ещё {len(qus) - 2} ждущих"
        else:
            txt_next = f"🎞 Следующий в очереди {queue.name}\n🥇-> @{qus[0].user.username}"
        if queue.msg_next is not None:
            tgapi.deleteMessage(queue.msg_next.chat_id, queue.msg_next.message_id)
            queue.msg_next = None
        ok, r = bot.sendMessage(txt_next, reply_markup=tgapi.InlineKeyboardMarkup([[
            tgapi.InlineKeyboardButton.callback("Пропустить 1", f"pass_queue {queue.id}"),
            tgapi.InlineKeyboardButton.callback("Выйти из очди", f"exit_queue {queue.id}"),
        ]]), message_thread_id=queue.msg.message_thread_id)
        if not ok:
            return "Error!"
        queue.msg_next = Msg.new_from_data(bot.db_sess, r)
        bot.db_sess.commit()

    tgapi.editMessageText(queue.msg.chat_id, queue.msg.message_id, txt, reply_markup=tgapi.InlineKeyboardMarkup([[
        tgapi.InlineKeyboardButton.callback("Встать в очдь", f"enter_queue {queue.id}"),
        tgapi.InlineKeyboardButton.callback("Выйти из очди", f"exit_queue {queue.id}"),
    ]]))


@Bot.add_command("enter_queue", None)
def enter_queue(bot: Bot, args: list[str]):
    if len(args) < 1:
        return "No queue id provided"

    id = parse_int(args[0])
    if id is None:
        return "id is NaN"

    queue = Queue.get(bot.db_sess, id)
    if queue is None:
        return f"queue with id={id} doesnt exist"

    qu = QueueUser.get(bot.db_sess, id, bot.user.id)
    if qu is not None:
        return "Уже в очереди"

    QueueUser.new(bot.db_sess, id, bot.user.id)
    updateQueue(bot, queue)
    return "Вы встали в очередь"


@Bot.add_command("exit_queue", None)
def exit_queue(bot: Bot, args: list[str]):
    if len(args) < 1:
        return "No queue id provided"

    id = parse_int(args[0])
    if id is None:
        return "id is NaN"

    queue = Queue.get(bot.db_sess, id)
    if queue is None:
        return f"queue with id={id} doesnt exist"

    qu = QueueUser.get(bot.db_sess, id, bot.user.id)
    if qu is None:
        return "Уже не в очереди"

    qu.delete()
    updateQueue(bot, queue)
    return "Вы вышли из очереди"
