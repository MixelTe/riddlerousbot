from sqlalchemy.orm import Session

from data.task import Task
from data.user import User
import tgapi


class BotAdmin(tgapi.BotCommand):
    BotName = "@riddlerousbot"
    db_sess: Session = None
    user: User = None

    def __init__(self):
        super().__init__()
        self.register_command("show_tasks", self.cmd_show_tasks)
        self.register_command("add_task", self.cmd_add_task)

    def on_text(self):
        text = f"Hi! {self.user.first_name}\nDo you say: {self.message.text}?"
        self.sendMessage(text, reply_markup=tgapi.InlineKeyboardMarkup([[
            tgapi.InlineKeyboardButton.callback("Task list", "show_tasks"),
            tgapi.InlineKeyboardButton.inline_query_current_chat("Add task", "add_task"),
        ]]))

@BotAdmin.add_command("show_tasks")
def cmd_show_tasks(self, args: list[str]):
    tasks = Task.all(self.db_sess)
    text = "\n".join(map(str, tasks))
    if text == "":
        text = "no tasks"
    self.sendMessage(text)

def cmd_add_task(self, args: list[str]):
    answer = " ".join(args)
    if answer == "":
        self.sendMessage("add_task <answer>")
    else:
        Task.new(self.user, answer)
        self.sendMessage(f"task added: {answer}")
