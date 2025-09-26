from datetime import timedelta

import bafser_tgapi as tgapi
from bafser import Undefined, get_datetime_now, listfind

from bot.bot import Bot
from bot.queue.utils import get_queue_by_reply, update_queue_msg_if_changes, updateQueue, updateQueueLoudness
from bot.utils import get_users_from_msg, silent_mode
from data.queue import Queue
from data.queue_user import QueueUser
from data.user import User
from utils import parse_int


@Bot.add_command("queue_rename", desc_adm=("Переименновать очередь", "<new_name> [\\s]"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_rename(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.user
    s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err
    assert queue

    if len(args) < 1:
        return "Укажите новое имя очереди\nUsage: /queue_rename <new_name> [\\s]"

    old_name = queue.name
    name = " ".join(args)
    queue.update_name(bot.user, name)

    bot.logger.info(f"qid={queue.id} (\"{old_name}\" -> \"{name}\")")
    updateQueue(bot, queue, updateQueueLoudness.quiet)
    if not s:
        return f"✏ Имя очереди {old_name} обновлено на очередь {name}"


@Bot.add_command("queue_clear", desc_adm="Очистить очередь")
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_clear(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.user
    s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err
    assert queue

    QueueUser.delete_all_in_queue(bot.user, queue.id)

    bot.logger.info(f"qid={queue.id}")
    updateQueue(bot, queue)
    if not s:
        return f"✏ Очередь {queue.name} очищена"


@Bot.add_command("queue_force_update", desc_adm="Обновить очередь")
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_force_update(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err
    assert queue

    bot.logger.info(f"qid={queue.id}")
    updateQueue(bot, queue, updateQueueLoudness.scream)


@Bot.add_command("queue_kick", desc_adm=("Выпнуть из очереди", ["<username> [\\s]", "<number> [\\s]"]))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_kick(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.db_sess
    assert bot.user
    s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err
    assert queue

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

    if num is not None:
        bot.sendMessage(f"Удалить {user.get_tagname()} ?", reply_markup=tgapi.InlineKeyboardMarkup(inline_keyboard=[[
            tgapi.InlineKeyboardButton.callback("🟢 Да", f"queue_kick_cmd + {queue.id} {user.id}" + (" \\s" if s else "")),
            tgapi.InlineKeyboardButton.callback("🔴 Отмена", f"queue_kick_cmd - {queue.id} {user.id}" + (" \\s" if s else "")),
        ]]))
        return

    bot.logger.info(f"qid={queue.id} uid={user.id} ({user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        uq.delete(bot.user)

    if not s:
        return f"🔴 {user.get_tagname()} теперь не в очереди {queue.name}"


@Bot.add_command("queue_kick_cmd")
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_kick_cmd(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.db_sess
    assert bot.user
    s = silent_mode(bot, args)

    if len(args) < 3:
        return "not enought args"

    if bot.callback_query and Undefined.defined(bot.callback_query.message):
        msg = bot.callback_query.message
        tgapi.deleteMessage(msg.chat.id, msg.message_id)

    if args[0] == "-":
        return

    queue_id = parse_int(args[1])
    user_id = parse_int(args[2])

    if queue_id is None:
        return "queue_id is None"
    if user_id is None:
        return "user_id is None"

    queue = Queue.get(bot.db_sess, queue_id)
    if queue is None:
        return "queue not found"

    uq = QueueUser.get_by_user_id(bot.db_sess, queue.id, user_id)
    if uq is None:
        return "user not found in queue"

    user = uq.user
    bot.logger.info(f"qid={queue.id} uid={user.id} ({user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        uq.delete(bot.user)

    if not s:
        return f"🔴 {user.get_tagname()} теперь не в очереди {queue.name}"


@Bot.add_command("queue_add_to", desc_adm=("Добавить на позицию в очереди", "<position> <username> [\\s]"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_add_to(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.db_sess
    assert bot.user
    s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err
    assert queue

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
        qu = listfind(qus, lambda x: x.user_id == user.id)
        if qu is None:
            qu = QueueUser.new(bot.user, queue.id, user.id)
            qus.append(qu)
        qui = qus.index(qu)

        while True:
            if qui < pos:
                if qui >= len(qus) - 1:
                    break
                qus[qui], qus[qui + 1] = qus[qui + 1], qus[qui]
                QueueUser.swap_enter_date(bot.user, qus[qui], qus[qui + 1], commit=False)
                qui += 1
            elif qui > pos:
                if qui <= 0:
                    break
                qus[qui], qus[qui - 1] = qus[qui - 1], qus[qui]
                QueueUser.swap_enter_date(bot.user, qus[qui], qus[qui - 1], commit=False)
                qui -= 1
            else:
                break
        bot.db_sess.commit()

    bot.logger.info(f"qid={queue.id} uid={user.id} ({user.get_username()}) qui={qui}")
    if not s:
        return f"🟢 {user.get_tagname()} теперь в очереди {queue.name} на позиции {qui + 1}"


@Bot.add_command("queue_set", desc_adm=("Полностью изменить очередь", "<username> [...<username>]"))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_set(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    assert bot.user
    assert bot.db_sess
    s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err
    assert queue

    users, err = get_users_from_msg(bot, args)
    if err:
        bot.sendMessage(err)

    if len(users) == 0:
        return

    bot.logger.info(f"qid={queue.id} [{'; '.join(f'{u.id} ({u.get_username()})' for u in users)}]")
    QueueUser.delete_all_in_queue(bot.user, queue.id)
    now = get_datetime_now() - timedelta(seconds=len(users))
    for i, user in enumerate(users):
        qu = QueueUser.new(bot.user, queue.id, user.id, commit=False)
        qu.enter_date = now + timedelta(seconds=i)

    bot.db_sess.commit()
    updateQueue(bot, queue)

    if not s:
        return f"✏ Очередь {queue.name} изменена"
