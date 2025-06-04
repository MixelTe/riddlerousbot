from typing import List, Union
from .utils import call
from .types import *


def getUpdates(offset: int = 0, timeout: int = 0):
    ok, r = call("getUpdates", {"offset": offset, "timeout": timeout}, timeout=timeout + 5)
    if not ok:
        return False, r
    return True, list(map(lambda x: Update(x), r["result"]))


# https://core.telegram.org/bots/api#sendmessage
def sendMessage(chat_id: str, text: str, message_thread_id: int = None, use_markdown=False,
                reply_markup: InlineKeyboardMarkup = None, reply_parameters: ReplyParameters = None,
                entities: List[MessageEntity] = None):
    ok, r = call("sendMessage", {
        "chat_id": chat_id,
        "message_thread_id": message_thread_id,
        "text": text,
        "parse_mode": "MarkdownV2" if use_markdown else None,
        "reply_markup": reply_markup,
        "reply_parameters": reply_parameters,
        "entities": entities,
    })
    if not ok:
        return False, r
    return True, Message(r["result"])


# https://core.telegram.org/bots/api#editmessagetext
def editMessageText(chat_id: Union[int, str], message_id: int, text: str, use_markdown=False, reply_markup: InlineKeyboardMarkup = None):
    ok, r = call("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "MarkdownV2" if use_markdown else None,
        "reply_markup": reply_markup,
    })
    if not ok:
        return False, r
    return True, Message(r["result"])


# https://core.telegram.org/bots/api#editmessagetext
def editMessageText_inline(inline_message_id: str, text: str, use_markdown=False, reply_markup: InlineKeyboardMarkup = None):
    ok, r = call("editMessageText", {
        "inline_message_id": inline_message_id,
        "text": text,
        "parse_mode": "MarkdownV2" if use_markdown else None,
        "reply_markup": reply_markup,
    })
    if not ok:
        return False, r
    return True, Message(r["result"])


# https://core.telegram.org/bots/api#editmessagereplymarkup
def editMessageReplyMarkup(chat_id: Union[int, str], message_id: int, reply_markup: InlineKeyboardMarkup):
    ok, r = call("editMessageReplyMarkup", {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup,
    })
    if not ok:
        return False, r
    return True, Message(r["result"])


# https://core.telegram.org/bots/api#editmessagereplymarkup
def editMessageReplyMarkup_inline(inline_message_id: str, reply_markup: InlineKeyboardMarkup):
    ok, r = call("editMessageReplyMarkup", {
        "inline_message_id": inline_message_id,
        "reply_markup": reply_markup,
    })
    if not ok:
        return False, r
    return True, Message(r["result"])


# https://core.telegram.org/bots/api#deletemessage
def deleteMessage(chat_id: Union[int, str], message_id: int):
    ok, r = call("deleteMessage", {
        "chat_id": chat_id,
        "message_id": message_id,
    })
    if not ok:
        return False, r
    return True, r["result"]


# https://core.telegram.org/bots/api#answerinlinequery
def answerInlineQuery(
    inline_query_id: str,
    results: list[InlineQueryResult],
    cache_time: int = 300,
    is_personal: bool = False,
    next_offset: str = None,
    # button: InlineQueryResultsButton = None,
):
    ok, r = call("answerInlineQuery", {
        "inline_query_id": inline_query_id,
        "results": results,
        "cache_time": cache_time,
        "is_personal": is_personal,
        "next_offset": next_offset,
    })
    if not ok:
        return False, r
    return True, r["result"]


# https://core.telegram.org/bots/api#answercallbackquery
def answerCallbackQuery(
    callback_query_id: str,
    text: str = None,
    show_alert: bool = False,
    url: str = None,
    cache_time: int = 0,
):
    ok, r = call("answerCallbackQuery", {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert,
        "url": url,
        "cache_time": cache_time,
    })
    if not ok:
        return False, r
    return True, r["result"]


# https://core.telegram.org/bots/api#setmycommands
def setMyCommands(commands: list[BotCommand], scope=None, language_code=None):
    ok, r = call("setMyCommands", {
        "commands": commands,
        "scope": scope,
        "language_code": language_code,
    })
    if not ok:
        return False, r
    return True, r["result"]


# https://core.telegram.org/bots/api#getchatmember
def getChatMember(chat_id: Union[str, int], user_id: int):
    ok, r = call("getChatMember", {
        "chat_id": chat_id,
        "user_id": user_id,
    })
    if not ok:
        return False, r
    return True, ChatMember(r["result"])


# https://core.telegram.org/bots/api#pinchatmessage
def pinChatMessage(chat_id: Union[str, int], message_id: int, disable_notification=True):
    ok, r = call("pinChatMessage", {
        "chat_id": chat_id,
        "message_id": message_id,
        "disable_notification": disable_notification,
    })
    if not ok:
        return False, r
    return True, r["result"]
