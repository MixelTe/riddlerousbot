from typing import Callable
from .types import *
from .methods import *


class Bot:
    update: Update = None
    message: Message = None
    callback_query: CallbackQuery = None
    inline_query: InlineQuery = None
    chosen_inline_result: ChosenInlineResult = None

    _commands: dict[str, (Callable[["Bot", list[str]], None], str)] = {}
    TextWrongCommand = "Wrong command"

    def init(self):
        setMyCommands([BotCommand(cmd, self._commands[cmd][1]) for cmd in self._commands.keys()])

    @classmethod
    def add_command(cls, command: str, description: str):
        def wrapper(fn: Callable[["Bot", list[str]], None]):
            cls._commands[command] = (fn, description)
            return fn
        return wrapper

    def before_process_update(self, user: User):
        pass

    def after_process_update(self):
        pass

    def process_update(self, update: Update):
        self.update = update
        self.message = update.message
        self.callback_query = update.callback_query
        self.inline_query = update.inline_query
        self.chosen_inline_result = update.chosen_inline_result
        if update.message and update.message.text != "":
            self.before_process_update(self.message.sender)
            self.on_message()
        if update.callback_query:
            self.before_process_update(self.callback_query.sender)
            self.on_callback_query()
        if update.inline_query:
            self.before_process_update(self.inline_query.sender)
            self.on_inline_query()
        if update.chosen_inline_result:
            self.before_process_update(self.chosen_inline_result.sender)
            self.on_chosen_inline_result()
        self.after_process_update()

    def on_message_text(self):
        pass

    def on_message(self):
        if self.message.text.startswith("/"):
            if not self.on_command(self.message.text[1:]):
                self.sendMessage(self.TextWrongCommand)
        else:
            self.on_message_text()

    def on_command(self, input: str):
        args = [str.strip(v) for v in input.split()]
        if len(args) == 0:
            return False
        command = args[0]
        mention = command.find("@")
        if mention > 0:
            command = command[:mention]
        args = args[1:]
        cmd = self._commands.get(command, None)
        if not cmd:
            return False
        fn, description = cmd
        fn(self, args)
        return True

    def on_callback_query(self):
        if self.on_command(self.callback_query.data):
            answerCallbackQuery(self.callback_query.id)
        else:
            answerCallbackQuery(self.callback_query.id, self.TextWrongCommand)

    def on_inline_query(self):
        answerInlineQuery(self.inline_query.id, [])

    def sendMessage(self, text: str, message_thread_id: int = None, use_markdown=False, reply_markup: InlineKeyboardMarkup = None):
        chat_id = None
        if self.message:
            chat_id = self.message.chat.id
        elif self.callback_query:
            chat_id = self.callback_query.message.chat.id
        else:
            raise Exception("tgapi: cant send message without chat id")
        sendMessage(chat_id, text, message_thread_id, use_markdown, reply_markup)

    def on_chosen_inline_result(self):
        pass
