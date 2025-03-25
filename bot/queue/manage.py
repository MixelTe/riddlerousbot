from bfs import Log, get_datetime_now
from bot.bot import Bot
from bot.queue.utils import get_queue, updateQueue
from data.queue_user import QueueUser
from data.queue import Queue

# TODO: edit queue methods

@Bot.add_command("queue_rename", "Переименновать очередь")
def new_queue(bot: Bot, args: list[str]):
    if not bot.message or not bot.message.reply_to_message:
        return "Укажите очередь, ответив на неё"

    queue = Queue.get_by_message(bot.db_sess, bot.message.reply_to_message)
    if not queue:
        return "Необходимо ответить на сообщение очереди (это не оно, или оно уже не действительно)"

    if len(args) < 1:
        return "Укажите новое имя очереди\nUsage: /queue_rename <new_name>"
    name = " ".join(args)

    old_name = queue.name
    queue.name = name
    Log.updated(queue, bot.user, [("name", old_name, name)])

    updateQueue(bot, queue)
    return f"✏ Имя очереди {old_name} обновлено на очередь {name}"
