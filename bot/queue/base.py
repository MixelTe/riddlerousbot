from datetime import timedelta

import bafser_tgapi as tgapi
from bafser import listfind, get_datetime_now

from bot.bot import Bot
from bot.queue.utils import get_queue, get_queue_by_reply, update_queue_msg_if_changes, updateQueue
from bot.utils import silent_mode
from data.queue import Queue
from data.queue_user import QueueUser
from data.user import User


@Bot.add_command(desc_adm=("Создать новую очередь", "<name> [\\s]"))
@Bot.cmd_for_admin
def queue_new(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    silent_mode(bot, args)
    if len(args) < 1:
        return "Укажите имя очереди\nUsage: /queue_new <name> [\\s]"

    name = " ".join(args)
    bot.logger.info(f"creating {name}")
    ok, r = bot.sendMessage(f"📝 Очередь {name}:\n⏳ Создание...")
    if not ok:
        bot.logger.error(r)
        return "Error!"

    queue = Queue.new_by_message(r, name)
    bot.logger.info(f"created id={queue.id} ({name})")
    tgapi.pinChatMessage(r.chat.id, r.message_id)
    updateQueue(bot, queue)


@Bot.add_command()
def queue_enter(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    queue = get_queue(bot, args)
    qu = QueueUser.get(queue.id, bot.user.id)
    if qu is not None:
        return "Уже в очереди"

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        now = get_datetime_now()
        if now.month != 4 or now.day > 4:
            QueueUser.new(queue.id, bot.user.id)
        else:
            qu = QueueUser.new(queue.id, bot.user.id)
            qus = QueueUser.all_in_queue(queue.id)
            qu.enter_date = qus[0].enter_date - timedelta(minutes=1)
            qu.db_sess.commit()
    return "Вы встали в очередь"


@Bot.add_command()
def queue_exit(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    queue = get_queue(bot, args)
    qu = QueueUser.get(queue.id, bot.user.id)
    if qu is None:
        return "Уже не в очереди"

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        qu.delete()
    return "Вы вышли из очереди"


@Bot.add_command()
def queue_pass(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    queue = get_queue(bot, args)
    qus = list(QueueUser.all_in_queue(queue.id))
    uid = bot.user.id
    qu = listfind(qus, lambda x: x.user_id == uid)
    if qu is None:
        return "Вы не в очереди"
    qui = qus.index(qu)

    now = get_datetime_now()
    if now.month != 4 or now.day > 4:
        if qui + 1 >= len(qus):
            return "Вы уже в конце очереди"

        next_qu = qus[qui + 1]
    else:
        if qui - 1 < 0:
            return "Вы уже в начале очереди"

        next_qu = qus[qui - 1]

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        QueueUser.swap_enter_date(qu, next_qu)

    return "Вы пропустили одного"


@Bot.add_command()
def queue_end(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    queue = get_queue(bot, args)
    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    qu = QueueUser.get(queue.id, bot.user.id)
    with update_queue_msg_if_changes(bot, queue):
        if qu is None:
            QueueUser.new(queue.id, bot.user.id)
        else:
            qu.set_now_as_enter_date()

    return "Вы встали в конец"


@Bot.add_command(desc=("Добавить в очередь", "<username> [\\s]"))
def queue_add(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    s = silent_mode(bot, args)

    if len(args) < 1:
        return "Укажите кого добавить в очередь\nUsage: /queue_add <username> [\\s]"

    queue = get_queue_by_reply(bot)
    username = args[0]
    user = User.get_by_username(bot.db_sess, username)

    if not user:
        return f"👻 Этот пользователь ({username}) не знаком боту (если в имени ошибки нет, пускай он хотя бы раз повзаимодействует с ботом)"

    qu = QueueUser.get(queue.id, user.id)
    if qu is not None:
        return f"🟢 {user.get_tagname()} уже в очереди {queue.name}"

    bot.logger.info(f"qid={queue.id} uid={user.id} ({user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        QueueUser.new(queue.id, user.id)

    if not s:
        return f"🟢 {user.get_tagname()} теперь в очереди {queue.name}"
