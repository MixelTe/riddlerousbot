from sqlalchemy.orm import Session

from bfs import db_session
from data.task import Task
from data.user import User
import tgapi


class Bot(tgapi.Bot):
    db_sess: Session = None
    user: User = None

    def before_process_update(self, tguser: tgapi.User):
        db_sess = db_session.create_session()
        user = User.get_by_id_tg(db_sess, tguser.id)
        if user is None:
            user = User.new_from_data(db_sess, tguser)
        self.db_sess = db_sess
        self.user = user

    def after_process_update(self):
        self.db_sess.close()

    def on_message_text(self):
        if self.user.is_admin():
            text = f"Hi! {self.user.first_name}\nDo you say: {self.message.text}?\n/add_task"
            self.sendMessage(text, reply_markup=tgapi.InlineKeyboardMarkup([[
                tgapi.InlineKeyboardButton.callback("Task list", "show_tasks"),
            ]]))
        else:
            # text = "Мне не разрешают разговаривать с незнакомцами("
            text = f"Привет! {self.user.first_name}\nГоворишь значит: {self.message.text}?"
            self.sendMessage(text)


@Bot.add_command("show_tasks", "Show tasks")
def cmd_show_tasks(bot: Bot, args: list[str]):
    tasks = Task.all(bot.db_sess)
    text = "\n".join(map(str, tasks))
    if text == "":
        text = "no tasks"
    bot.sendMessage(text)


@Bot.add_command("add_task", "Add task")
def cmd_add_task(bot: Bot, args: list[str]):
    answer = " ".join(args)
    if answer == "":
        bot.sendMessage("/add_task <answer>")
    else:
        Task.new(bot.user, answer)
        bot.sendMessage(f"task added: {answer}")
