from .utils import call
from .types import *


def getUpdates(offset: int = 0, timeout: int = 0):
    ok, r = call("getUpdates", {"offset": offset, "timeout": timeout}, timeout=timeout + 5)
    if not ok:
        return False, r
    return True, list(map(lambda x: Update(x), r["result"]))


def sendMessage(chat_id: str, text: str, message_thread_id: int = None, use_markdown=False, reply_markup: InlineKeyboardMarkup = None):
    ok, r = call("sendMessage", {
        "chat_id": chat_id,
        "message_thread_id": message_thread_id,
        "text": text,
        "parse_mode": "MarkdownV2" if use_markdown else None,
        "reply_markup": reply_markup,
    })
    if not ok:
        return False, r
    return True, Message(r["result"])


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
