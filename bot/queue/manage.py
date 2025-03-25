from bfs import Log, get_datetime_now
from bot.bot import Bot
from bot.queue.utils import get_queue, get_queue_by_reply, updateQueue
from data.queue_user import QueueUser
from data.queue import Queue

# TODO: edit queue methods

@Bot.add_command("queue_rename", (None, "Переименновать очередь"))
def new_queue(bot: Bot, args: list[str]):
    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    if len(args) < 1:
        return "Укажите новое имя очереди\nUsage: /queue_rename <new_name>"
    name = " ".join(args)

    old_name = queue.name
    queue.name = name
    Log.updated(queue, bot.user, [("name", old_name, name)])

    updateQueue(bot, queue)
    return f"✏ Имя очереди {old_name} обновлено на очередь {name}"


@Bot.add_command("queue_clear", (None, "Очистить очередь"))
def new_queue(bot: Bot, args: list[str]):
    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    QueueUser.delete_all_in_queue(bot.db_sess, queue.id)

    updateQueue(bot, queue)
    return f"✏ Очередь {queue.name} очищена"
