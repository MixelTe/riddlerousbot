from bot.bot import Bot
from bot.queue.utils import get_queue, get_queue_by_reply, silent_mode, update_queue_msg_if_changes, updateQueue
from data.queue_user import QueueUser
from data.queue import Queue
from data.user import User
import tgapi
from utils import find


@Bot.add_command("queue_new", (None, ("Создать новую очередь", "<name> [\\s]")))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def queue_new(bot: Bot, args: list[str]):
    args, _ = silent_mode(bot, args)
    if len(args) < 1:
        return "Укажите имя очереди\nUsage: /queue_new <name> [\\s]"

    name = " ".join(args)
    bot.logger.info(f"creating {name}")
    ok, r = bot.sendMessage(f"📝 Очередь {name}:\n⏳ Создание...")
    if not ok:
        bot.logger.error(r)
        return "Error!"
    bot.logger.info(f"created {name}")

    queue = Queue.new_by_message(bot.user, r, name)
    tgapi.pinChatMessage(r.chat.id, r.message_id)
    updateQueue(bot, queue)


@Bot.add_command("queue_enter", None)
@Bot.cmd_connect_db
def queue_enter(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    qu = QueueUser.get(bot.db_sess, queue.id, bot.user.id)
    if qu is not None:
        return "Уже в очереди"

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        QueueUser.new(bot.user, queue.id, bot.user.id)
    return "Вы встали в очередь"


@Bot.add_command("queue_exit", None)
@Bot.cmd_connect_db
def queue_exit(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    qu = QueueUser.get(bot.db_sess, queue.id, bot.user.id)
    if qu is None:
        return "Уже не в очереди"

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        qu.delete(bot.user)
    return "Вы вышли из очереди"


@Bot.add_command("queue_pass", None)
@Bot.cmd_connect_db
def queue_pass(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    qus = list(QueueUser.all_in_queue(bot.db_sess, queue.id))
    qu = find(qus, lambda x: x.user_id == bot.user.id)
    if qu is None:
        return "Вы не в очереди"
    qui = qus.index(qu)

    if qui + 1 >= len(qus):
        return "Вы уже в конце очереди"

    next_qu = qus[qui + 1]

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        QueueUser.swap_enter_date(bot.user, qu, next_qu)

    return "Вы пропустили одного"


@Bot.add_command("queue_end", None)
@Bot.cmd_connect_db
def queue_end(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    bot.logger.info(f"qid={queue.id} uid={bot.user.id} ({bot.user.get_username()})")
    qu = QueueUser.get(bot.db_sess, queue.id, bot.user.id)
    with update_queue_msg_if_changes(bot, queue):
        if qu is None:
            QueueUser.new(bot.user, queue.id, bot.user.id)
        else:
            qu.set_now_as_enter_date(bot.user)

    return "Вы встали в конец"


@Bot.add_command("queue_add", (("Добавить в очередь", "<username> [\\s]"), None))
@Bot.cmd_connect_db
def queue_add(bot: Bot, args: list[str]):
    args, s = silent_mode(bot, args)

    queue, err = get_queue_by_reply(bot)
    if err:
        return err

    username = args[0]
    user = User.get_by_username(bot.db_sess, username)

    if not user:
        return "👻 Этот пользователь не знаком боту (если в имени ошибки нет, пускай он хотя бы раз повзаимодействует с ботом)"

    qu = QueueUser.get(bot.db_sess, queue.id, user.id)
    if qu is not None:
        return f"🟢 {user.get_tagname()} уже в очереди {queue.name}"

    bot.logger.info(f"qid={queue.id} uid={user.id} ({user.get_username()})")
    with update_queue_msg_if_changes(bot, queue):
        QueueUser.new(bot.user, queue.id, user.id)

    if not s:
        return f"🟢 {user.get_tagname()} теперь в очереди {queue.name}"
