from functools import wraps
from .bot import Bot
from .types import *
from .methods import *


class BotCommand(Bot):
    BotName = "@BotName"
    TextWrongCommand = "Wrong command"
    _commands = {}

    def on_text(self):
        pass

    def register_command(self, command: str, fn):
        self._commands[command] = fn

    @classmethod
    def add_command(cls):
        def wrapper(fn, command: str):
            cls._commands[command] = fn
            @wraps(fn)
            def decorator(*args, **kwargs):
                fn(*args, **kwargs)
            return decorator
        return wrapper

    def on_message(self):
        if self.message.text.startswith(self.BotName):
            args = [str.strip(v) for v in self.message.text[len(self.BotName):].split()]
            success = len(args) != 0 and self.on_command(args[0], args[1:])
            if not success:
                self.sendMessage(self.TextWrongCommand)
        else:
            self.on_text()

    def on_callback_query(self):
        super().on_callback_query()
        command = self.callback_query.data
        success = self.on_command(command, [])
        if not success:
            self.sendMessage(self.TextWrongCommand)

    def on_command(self, command, args: list[str]):
        fn = self._commands.get(command, None)
        if not fn:
            return False
        fn(args)
        return True
