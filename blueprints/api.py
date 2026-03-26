from datetime import timezone
import random

import bafser_tgapi as tgapi
from bafser import Undefined, get_datetime_now, get_db_session
from flask import Blueprint, g

from bot.bot import Bot, User
from bot.queue.utils import updateQueue
from data.queue import Queue
from data.queue_user import QueueUser

bp = Blueprint("api", __name__)


@bp.route("/api/ping")
def ping():
    now = get_datetime_now()
    day = (now.weekday() + 1) * 10000
    curtime = now.hour * 100 + now.minute
    queues = Queue.query2().filter(Queue.clear_at >= day, Queue.clear_at <= day + curtime).all()
    if not queues:
        return "ok"
    g.user = User.get_admin(get_db_session())
    for queue in queues:
        clear_at = queue.get_parsed_clear_at()
        if not clear_at:
            continue
        _, _, hour, minute = clear_at
        cleared_at = queue.cleared_at
        clear_at = get_datetime_now()
        clear_at = clear_at.replace(hour=hour, minute=minute, second=0, microsecond=0)
        clear = not cleared_at or cleared_at.replace(tzinfo=timezone.utc) < clear_at
        if not clear:
            continue

        with Bot() as bot:
            bot.message = tgapi.Message(
                message_id=queue.msg.message_id,
                message_thread_id=queue.msg.message_thread_id or Undefined,
                is_topic_message=queue.msg.message_thread_id is not None,
                chat=tgapi.Chat(id=queue.msg.chat_id, type="supergroup"),
                date=now,
            )
            is_check_success, is_message_exists = tgapi.check_message_exists(queue.msg.chat_id, queue.msg.message_id)
            if not is_message_exists:
                if is_check_success:
                    queue.delete2()
                continue
            queue.cleared_at = now
            qus = QueueUser.all_in_queue(queue.id)
            if not qus:
                queue.db_sess.commit()
                continue
            txt_one, txt_many = random.choice(queue_variants)
            if len(qus) == 1:
                txt = f"{txt_one}: {qus[0].user.get_tagname()}"
            else:
                txt = f"{txt_many}:\n"
                for i, qu in enumerate(qus):
                    txt += f"{i + 1}) {qu.user.get_tagname()}\n"
            QueueUser.delete_all_in_queue(queue.id)
            updateQueue(bot, queue)
            bot.logger.info(f"autoclear qid={queue.id}")
            bot.sendMessage(
                f"🧹 Очередь {queue.name} очищена по расписанию\n{txt}",
                reply_parameters=tgapi.ReplyParameters(message_id=queue.msg.message_id, allow_sending_without_reply=True),
            )
    return "ok"


queue_variants = [
    ("Застрявший в текстурах", "Застрявшие в текстурах"),
    ("Потерянная душа", "Потерянные души"),
    ("Унесенный Бездной", "Унесенные Бездной"),
    ("Жертва очищения", "Жертвы очищения"),
    ("Призрак очереди", "Призраки очереди"),
    ("Растаявший", "Растаявшие"),
    ("Битый пиксель", "Битые пиксели"),
    ("Забытый", "Забытые"),
    ("Потеряшка", "Потеряшки"),
    ("Растворенный в эфире", "Растворенные в эфире"),
    ("Тень прошлого", "Тени прошлого"),
    ("Скипнутый", "Пропущенные кадры"),
    ("Зависший в текстурах", "Выпавшие за карту"),
    ("Потерянный в астрале", "Потерянные в астрале"),
    ("Рассыпавшийся в ману", "Рассыпавшиеся в ману"),
    ("Дезинтегрированный", "Дезинтегрированные"),
    ("Отформатированный", "Отформатированные"),
    ("Потерянный пакет", "Потерянные пакеты"),
    ("Списанный юнит", "Списанные юниты"),
    ("Стертый из хроник", "Стертые из хроник"),
    ("Унесённый ветрами кода", "Унесённые ветрами кода"),
    ("Удалённый заклинанием очистки", "Удалённые заклинанием очистки"),
    ("Отправленный в /dev/null", "Отправленные в /dev/null"),
    ("Забытый в подземельях сервера", "Забытые в подземельях сервера"),
    ("Затёртый патчем", "Затёртые патчем"),
    ("Снесённый апдейтом", "Снесённые апдейтом"),
    ("Скрытый display:none", "Скрытые display:none"),
    ("Уехавший за пределы viewport", "Уехавшие за пределы viewport"),
    ("Спрятанный за overflow:hidden", "Спрятанные за overflow:hidden"),
    ("Отрендеренный в никуда", "Отрендеренные в никуда"),
    ("Скрытый z-index’ом", "Скрытые z-index’ом"),
    ("Удалённый devtools’ом", "Удалённые devtools’ом"),
]
