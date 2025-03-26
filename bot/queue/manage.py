from bfs import Log, get_datetime_now
from bot.bot import Bot
from bot.queue.utils import get_queue, get_queue_by_reply, silent_mode, update_queue_msg_if_changes, updateQueue, updateQueueLoudness
from data.queue_user import QueueUser
from data.queue import Queue
import tgapi
from utils import parse_int

# TODO: edit queue methods
# delete from queue by № or username
# create/edit queue by list of usernames
# add user to queue by username


@Bot.add_command("queue_rename", (None, "Переименновать очередь"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def new_queue(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    if len(args) < 1:
        return "Укажите новое имя очереди\nUsage: /queue_rename <new_name> [/s]"

    name = " ".join(args)

    old_name = queue.name
    queue.name = name
    Log.updated(queue, bot.user, [("name", old_name, name)])

    updateQueue(bot, queue, updateQueueLoudness.quiet)
    if not s:
        return f"✏ Имя очереди {old_name} обновлено на очередь {name}"


@Bot.add_command("queue_clear", (None, "Очистить очередь"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_clear(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    QueueUser.delete_all_in_queue(bot.db_sess, queue.id)

    updateQueue(bot, queue)
    if not s:
        return f"✏ Очередь {queue.name} очищена"


@Bot.add_command("queue_force_update", (None, "Обновить очередь"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_force_update(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    updateQueue(bot, queue, updateQueueLoudness.scream)


@Bot.add_command("queue_kick", (None, "Выпнуть из очереди"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_kick(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    if len(args) < 1:
        return "Укажите ник или номер человека в очереди\nUsage: /queue_kick <name> [/s]\n/queue_kick <number> [/s]"

    num = parse_int(args[0])
    uq = None
    if num is None:
        username = args[0]
        if username.startswith("@"):
            username = username[1:]
        uq = QueueUser.get_by_username(bot.db_sess, queue.id, username)
    elif num - 1 >= 0:
        uq = QueueUser.get_by_order(bot.db_sess, queue.id, num - 1)

    if uq is None:
        return "Человек не найден в очереди\nUsage: /queue_kick <name> [/s]\n/queue_kick <number> [/s]"

    user = uq.user
    with update_queue_msg_if_changes(bot, queue):
        uq.delete()
        bot.db_sess.commit()

    if not s:
        return f"{user.get_tagname()} удалён из очереди {queue.name}"
