from typing import Callable, Tuple, Union
from .types import *
from .methods import *

cmd_fn = Callable[["Bot", list[str]], Union[None, str]]
cmd_dsc = Union[None, str]

class Bot:
    update: Update = None
    message: Message = None
    callback_query: CallbackQuery = None
    inline_query: InlineQuery = None
    chosen_inline_result: ChosenInlineResult = None

    _commands: dict[str, Tuple[cmd_fn, Tuple[cmd_dsc, cmd_dsc]]] = {}
    TextWrongCommand = "Wrong command"

    @property
    def is_callback(self):
        return self.callback_query is not None

    def init(self):
        setMyCommands([BotCommand(cmd, self._commands[cmd][1][0]) for cmd in self._commands.keys() if self._commands[cmd][1][0]])
        setMyCommands([BotCommand(cmd, self._commands[cmd][1][1]) for cmd in self._commands.keys() if self._commands[cmd][1][1]], BotCommandScope.all_chat_administrators())

    @classmethod
    def add_command(cls, command: str, description: Union[cmd_dsc, Tuple[cmd_dsc, cmd_dsc]]):
        def wrapper(fn: cmd_fn):
            if isinstance(description, tuple):
                pub, pri = description
            else:
                pub, pri = description, description

            cls._commands[command] = (fn, (pub, pri))
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
            r = self.on_command(self.message.text[1:])
            if r:
                if isinstance(r, str):
                    self.sendMessage(r)
            else:
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
        r = fn(self, args)
        if r:
            return r
        return True

    def on_callback_query(self):
        r = self.on_command(self.callback_query.data)
        if r:
            self.answerCallbackQuery(r if isinstance(r, str) else None)
        else:
            self.answerCallbackQuery(self.TextWrongCommand)

    def on_inline_query(self):
        self.answerInlineQuery([])

    def sendMessage(self, text: str, message_thread_id: int = None, use_markdown=False, reply_markup: InlineKeyboardMarkup = None):
        chat_id = None
        if self.message:
            chat_id = self.message.chat.id
            if message_thread_id is None and self.message.is_topic_message:
                message_thread_id = self.message.message_thread_id
        elif self.callback_query:
            chat_id = self.callback_query.message.chat.id
            if message_thread_id is None:
                message_thread_id = self.callback_query.message.message_thread_id
        else:
            raise Exception("tgapi: cant send message without chat id")
        return sendMessage(chat_id, text, message_thread_id, use_markdown, reply_markup)

    def answerCallbackQuery(self, text: str = None, show_alert: bool = False, url: str = None, cache_time: int = 0):
        if self.callback_query is None:
            raise Exception("tgapi: Bot.answerCallbackQuery is avaible only inside on_callback_query")
        return answerCallbackQuery(self.callback_query.id, text, show_alert, url, cache_time)

    def answerInlineQuery(self, results: list[InlineQueryResult], cache_time: int = 300, is_personal: bool = False, next_offset: str = None):
        if self.callback_query is None:
            raise Exception("tgapi: Bot.answerInlineQuery is avaible only inside on_inline_query")
        return answerInlineQuery(self.inline_query.id, results, cache_time, is_personal, next_offset)

    def on_chosen_inline_result(self):
        pass
