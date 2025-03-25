from bfs import Log, get_datetime_now
from bot.bot import Bot
from bot.queue.utils import get_queue, get_queue_by_reply, updateQueue, updateQueueLoudness
from data.queue_user import QueueUser
from data.queue import Queue

# TODO: edit queue methods
# delete from queue by № or username
# create/edit queue by list of usernames
# add user to queue by username


@Bot.add_command("queue_rename", (None, "Переименновать очередь"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
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

    updateQueue(bot, queue, updateQueueLoudness.quiet)
    return f"✏ Имя очереди {old_name} обновлено на очередь {name}"


@Bot.add_command("queue_clear", (None, "Очистить очередь"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_clear(bot: Bot, args: list[str]):
    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    QueueUser.delete_all_in_queue(bot.db_sess, queue.id)

    updateQueue(bot, queue)
    return f"✏ Очередь {queue.name} очищена"


@Bot.add_command("queue_force_update", (None, "Обновить очередь"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_force_update(bot: Bot, args: list[str]):
    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    updateQueue(bot, queue, updateQueueLoudness.scream)
