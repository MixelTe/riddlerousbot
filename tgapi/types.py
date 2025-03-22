from typing import Any, Literal
from .utils import JsonObj, ParsedJson


class User(ParsedJson):
    # https://core.telegram.org/bots/api#user
    __id_field__ = "id"
    id: int = 0
    is_bot: bool = False
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    language_code: str = ""


class Chat(ParsedJson):
    # https://core.telegram.org/bots/api#chat
    __id_field__ = "id"
    id: int = 0
    type: Literal["private", "group", "supergroup", "channel"] = ""
    title: str = ""
    is_forum: bool = False


class Message(ParsedJson):
    __id_field__ = "message_id"
    # https://core.telegram.org/bots/api#message
    message_id: int = 0
    sender: User = None
    chat: Chat = None
    text: str = ""
    date: int = 0

    def _parse_field(self, key: str, v: Any):
        if key == "from":
            return "sender", User(v)


class InlineQuery(ParsedJson):
    # https://core.telegram.org/bots/api#inlinequery
    __id_field__ = "id"
    id: str = ""
    sender: User = None
    query: str = ""
    offset: str = ""
    chat_type: Literal["sender", "private", "group", "supergroup", "channel"] = ""

    def _parse_field(self, key: str, v: Any):
        if key == "from":
            return "sender", User(v)

MaybeInaccessibleMessage = Message

class CallbackQuery(ParsedJson):
    # https://core.telegram.org/bots/api#callbackquery
    __id_field__ = "id"
    id: str = ""
    sender: User = None
    message: MaybeInaccessibleMessage = None
    inline_message_id: str = ""
    chat_instance: str = ""
    data: str = ""
    game_short_name: str = ""

    def _parse_field(self, key: str, v: Any):
        if key == "from":
            return "sender", User(v)


class ChosenInlineResult(ParsedJson):
    # https://core.telegram.org/bots/api#choseninlineresult
    __id_field__ = "result_id"
    result_id: str = ""
    sender: User = None
    # location: Location
    inline_message_id: str = ""
    query: str = ""

    def _parse_field(self, key: str, v: Any):
        if key == "from":
            return "sender", User(v)

class Update(ParsedJson):
    # https://core.telegram.org/bots/api#update
    __id_field__ = "update_id"
    update_id: int = 0
    message: Message = None
    inline_query: InlineQuery = None
    callback_query: CallbackQuery = None
    chosen_inline_result: ChosenInlineResult = None


class InputMessageContent(JsonObj):
    # https://core.telegram.org/bots/api#inputmessagecontent
    pass


class InputTextMessageContent(InputMessageContent):
    # https://core.telegram.org/bots/api#inputtextmessagecontent
    message_text: str
    parse_mode: Literal["MarkdownV2"]
    # entities: list[MessageEntity]
    # link_preview_options: LinkPreviewOptions

    def __init__(self, message_text, use_markdown = False) -> None:
        self.message_text = message_text
        self.parse_mode = "MarkdownV2" if use_markdown else None


class CallbackGame(JsonObj):
    # https://core.telegram.org/bots/api#callbackgame
    pass


class InlineKeyboardButton(JsonObj):
    # https://core.telegram.org/bots/api#inlinekeyboardbutton
    text: str
    url: str = None
    callback_data: str = None
    # web_app: WebAppInfo
    # login_url: LoginUrl
    # switch_inline_query: str
    switch_inline_query_current_chat: str
    # switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat
    # copy_text: CopyTextButton
    callback_game: CallbackGame = None
    # pay: bool

    def __init__(self, text: str) -> None:
        self.text = text

    @staticmethod
    def callback(text: str, callback_data: str):
        b = InlineKeyboardButton(text)
        b.callback_data = callback_data
        return b

    @staticmethod
    def inline_query_current_chat(text: str, query: str):
        b = InlineKeyboardButton(text)
        b.switch_inline_query_current_chat = query
        return b

    @staticmethod
    def run_game(text: str):
        b = InlineKeyboardButton(text)
        b.callback_game = CallbackGame()
        return b

    @staticmethod
    def open_url(text: str, url: str):
        b = InlineKeyboardButton(text)
        b.url = url
        return b


class InlineKeyboardMarkup(JsonObj):
    # https://core.telegram.org/bots/api#inlinekeyboardmarkup
    inline_keyboard: list[list[InlineKeyboardButton]]

    def __init__(self, inline_keyboard: list[list[InlineKeyboardButton]]) -> None:
        self.inline_keyboard = inline_keyboard


class InlineQueryResult(JsonObj):
    # https://core.telegram.org/bots/api#inlinequeryresult
    pass


class InlineQueryResultArticle(InlineQueryResult):
    # https://core.telegram.org/bots/api#inlinequeryresultarticle
    type = "article"
    id: str
    title: str
    input_message_content: InputMessageContent
    # reply_markup: InlineKeyboardMarkup
    url: str = None
    hide_url: bool = None
    description: str = None
    thumbnail_url: str = None
    thumbnail_width: int = None
    thumbnail_height: int = None

    def __init__(self, id: str, title: str, input_message_content: InputMessageContent) -> None:
        self.id = id
        self.title = title
        self.input_message_content = input_message_content


class InlineQueryResultGame(InlineQueryResult):
    # https://core.telegram.org/bots/api#inlinequeryresultgame
    type = "game"
    id: str
    game_short_name: str
    reply_markup: InlineKeyboardMarkup = None
    def __init__(self, id: str, game_short_name: str, reply_markup: InlineKeyboardMarkup = None) -> None:
        self.id = id
        self.game_short_name = game_short_name
        self.reply_markup = reply_markup
