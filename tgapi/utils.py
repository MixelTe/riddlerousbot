import logging
from typing import Any

import requests
from bafser import JsonObj

token_bot = ""
bot_name = ""
token_webhook = ""
url = ""


def setup(token_path="token.txt"):
    global token_bot, bot_name, token_webhook, url
    try:
        with open(token_path) as f:
            token_bot = f.readline().strip()
            bot_name = f.readline().strip()
            token_webhook = f.readline().strip()
            url = f.readline().strip()
    except Exception as e:
        logging.error(f"Cant read token\n{e}")
        raise e


def check_webhook_token(token: str):
    return token == token_webhook


def get_url(path):
    return url + path


def get_bot_name():
    return bot_name


def call(method: str, data: JsonObj | dict[str, Any], timeout: int | None = None):
    if timeout is not None and timeout <= 0:
        timeout = None
    if isinstance(data, dict):
        json = __item_to_json__(data)
    else:
        json = data.json()
    try:
        r = requests.post(f"https://api.telegram.org/bot{token_bot}/{method}", json=json, timeout=timeout)
        if not r.ok:
            logging.error(f"tgapi: {method} [{r.status_code}]\t{json}; {r.content}")
            return False, r.json()
        rj = r.json()
        logging.info(f"tgapi: {method}\t{json} -> {rj}")
        return True, rj
    except Exception as e:
        logging.error(f"tgapi call error\n{e}")
        raise Exception("tgapi call error")


def __item_to_json__(item: Any) -> Any:
    if isinstance(item, dict):
        r = {}
        for field, v in item.items():
            v = __item_to_json__(v)
            if v is not None:
                r[field] = v
        return r
    if isinstance(item, (list, tuple)):
        return [__item_to_json__(v) for v in item if v is not None]
    if isinstance(item, JsonObj):
        return item.json()
    return item
