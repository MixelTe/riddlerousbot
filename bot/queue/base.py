from bfs import get_datetime_now
from bot.bot import Bot
from bot.queue.utils import get_queue, updateQueue
from data.queue_user import QueueUser
from data.queue import Queue
from utils import find


@Bot.add_command("queue_new", (None, "Создать новую очередь"))
def queue_new(bot: Bot, args: list[str]):
    if len(args) < 1:
        return "Укажите имя очереди\nUsage: /queue_new <name>"
    name = " ".join(args)
    ok, r = bot.sendMessage(f"📝 Очередь {name}:\n⏳ Создание...")
    if not ok:
        return "Error!"

    queue = Queue.new_by_message(bot.user, r, name)
    updateQueue(bot, queue)


@Bot.add_command("queue_enter", None)
def queue_enter(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    qu = QueueUser.get(bot.db_sess, queue.id, bot.user.id)
    if qu is not None:
        return "Уже в очереди"

    QueueUser.new(bot.db_sess, queue.id, bot.user.id)
    updateQueue(bot, queue)
    return "Вы встали в очередь"


@Bot.add_command("queue_exit", None)
def queue_exit(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    qu = QueueUser.get(bot.db_sess, queue.id, bot.user.id)
    if qu is None:
        return "Уже не в очереди"

    qu.delete()
    updateQueue(bot, queue)
    return "Вы вышли из очереди"


@Bot.add_command("queue_pass", None)
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

    qu.enter_date, next_qu.enter_date = next_qu.enter_date, qu.enter_date
    bot.db_sess.commit()
    updateQueue(bot, queue)
    return "Вы пропустили одного"


@Bot.add_command("queue_end", None)
def queue_end(bot: Bot, args: list[str]):
    queue, err = get_queue(bot, args)
    if err:
        return err

    qu = QueueUser.get(bot.db_sess, queue.id, bot.user.id)
    if qu is None:
        QueueUser.new(bot.db_sess, queue.id, bot.user.id)
    else:
        qu.enter_date = get_datetime_now()
        bot.db_sess.commit()

    updateQueue(bot, queue)
    return "Вы встали в конец"
