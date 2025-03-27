from bfs import Log, get_datetime_now
from bot.bot import Bot
from bot.queue.utils import get_queue, get_queue_by_reply, silent_mode, update_queue_msg_if_changes, updateQueue, updateQueueLoudness
from data.queue_user import QueueUser
from data.queue import Queue
from data.user import User
import tgapi
from utils import find, parse_int

# TODO: edit queue methods
# create/edit queue by list of usernames


@Bot.add_command("queue_rename", (None, ("Переименновать очередь", "<new_name> [\\s]")))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_rename(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    if len(args) < 1:
        return "Укажите новое имя очереди\nUsage: /queue_rename <new_name> [\\s]"

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


@Bot.add_command("queue_kick", (None, ("Выпнуть из очереди", ["<username> [\\s]", "<number> [\\s]"])))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_kick(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    if len(args) < 1:
        return "Укажите ник или номер человека в очереди\nUsage: /queue_kick <username> [\\s]\n/queue_kick <position> [\\s]"

    num = parse_int(args[0])
    uq = None
    if num is None:
        username = args[0]
        uq = QueueUser.get_by_username(bot.db_sess, queue.id, username)
    elif num - 1 >= 0:
        uq = QueueUser.get_by_order(bot.db_sess, queue.id, num - 1)

    if uq is None:
        return "Человек не найден в очереди\nUsage: /queue_kick <username> [\\s]\n/queue_kick <number> [\\s]"

    user = uq.user
    with update_queue_msg_if_changes(bot, queue):
        uq.delete()
        bot.db_sess.commit()

    if not s:
        return f"🔴 {user.get_tagname()} теперь не в очереди {queue.name}"


@Bot.add_command("queue_add_to", (None, ("Добавить на позицию в очереди", "<position> <username> [\\s]")))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_add_to(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    if len(args) < 2:
        return "Укажите позицию для вставки и ник человека\nUsage: /queue_add_to <position> <username> [\\s]"

    pos = parse_int(args[0])
    if pos is None:
        return "Позиция для вставки должна быть целым числом"
    pos -= 1

    username = args[1]
    user = User.get_by_username(bot.db_sess, username)
    if not user:
        return "👻 Этот пользователь не знаком боту (если в имени ошибки нет, пускай он хотя бы раз повзаимодействует с ботом)"

    with update_queue_msg_if_changes(bot, queue):
        qus = QueueUser.all_in_queue(bot.db_sess, queue.id)
        qu = find(qus, lambda x: x.user_id == user.id)
        if qu is None:
            qu = QueueUser.new(bot.db_sess, queue.id, user.id)
            qus.append(qu)
        qui = qus.index(qu)

        while True:
            if qui < pos:
                if qui >= len(qus) - 1:
                    break
                qus[qui], qus[qui + 1] = qus[qui + 1], qus[qui]
                qus[qui].enter_date, qus[qui + 1].enter_date = qus[qui + 1].enter_date, qus[qui].enter_date
                qui += 1
            elif qui > pos:
                if qui <= 0:
                    break
                qus[qui], qus[qui - 1] = qus[qui - 1], qus[qui]
                qus[qui].enter_date, qus[qui - 1].enter_date = qus[qui - 1].enter_date, qus[qui].enter_date
                qui -= 1
            else:
                break
        bot.db_sess.commit()

    if not s:
        return f"🟢 {user.get_tagname()} теперь в очереди {queue.name} на позиции {qui + 1}"
