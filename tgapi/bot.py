from .types import *
from .methods import *


class Bot:
    update: Update = None
    message: Message = None
    callback_query: CallbackQuery = None
    inline_query: InlineQuery = None
    chosen_inline_result: ChosenInlineResult = None

    def process_update(self, update: Update):
        self.update = update
        self.message = update.message
        self.callback_query = update.callback_query
        self.inline_query = update.inline_query
        self.chosen_inline_result = update.chosen_inline_result
        if update.message and update.message.text != "":
            self.on_message()
        if update.callback_query:
            self.on_callback_query()
        if update.inline_query:
            self.on_inline_query()
        if update.chosen_inline_result:
            self.on_chosen_inline_result()

    def on_message(self):
        pass

    def on_callback_query(self):
        answerCallbackQuery(self.callback_query.id)

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
