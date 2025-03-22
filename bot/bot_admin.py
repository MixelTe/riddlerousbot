from sqlalchemy.orm import Session

from data.task import Task
from data.user import User
import tgapi


class BotAdmin(tgapi.BotCommand):
    BotName = "@riddlerousbot"
    db_sess: Session = None
    user: User = None

    def on_text(self):
        text = f"Hi! {self.user.first_name}\nDo you say: {self.message.text}?"
        self.sendMessage(text, reply_markup=tgapi.InlineKeyboardMarkup([[
            tgapi.InlineKeyboardButton.callback("Task list", "show_tasks"),
            tgapi.InlineKeyboardButton.inline_query_current_chat("Add task", "add_task"),
        ]]))


@BotAdmin.add_command("show_tasks")
def cmd_show_tasks(bot: BotAdmin, args: list[str]):
    tasks = Task.all(bot.db_sess)
    text = "\n".join(map(str, tasks))
    if text == "":
        text = "no tasks"
    bot.sendMessage(text)


@BotAdmin.add_command("add_task")
def cmd_add_task(bot: BotAdmin, args: list[str]):
    answer = " ".join(args)
    if answer == "":
        bot.sendMessage("add_task <answer>")
    else:
        Task.new(bot.user, answer)
        bot.sendMessage(f"task added: {answer}")
