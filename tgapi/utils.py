import logging
from typing import Any, Union

import requests


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


def call(method: str, json: Union["JsonObj", dict[str, Any]] = None, timeout: int = None):
    if timeout is not None and timeout <= 0:
        timeout = None
    if isinstance(json, dict):
        json = JsonDynamicObj(json)
    json = json.to_json()
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


def get_all_fields(obj):
    return [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]


class ParsedJson:
    __id_field__ = None

    def __init__(self, json: dict[str, Any]):
        a = self.__annotations__
        for key in json:
            v = json[key]
            r = self._parse_field(key, v)
            if r is not None:
                key, v = r
            elif key in a:
                t = a[key]
                if isinstance(t, type) and issubclass(t, ParsedJson):
                    v = t(v)
            if hasattr(self, key):
                setattr(self, key, v)

    def _parse_field(self, key: str, v: Any) -> Union[tuple[str, Any], None]:
        return None

    def __repr__(self) -> str:
        r = self.__class__.__name__ + "("
        if self.__id_field__ is not None and hasattr(self, self.__id_field__):
            r += f"{self.__id_field__}={getattr(self, self.__id_field__)}"
        return r + ")"

    def __str__(self) -> str:
        return self.__repr__()


class JsonObj:
    def to_json(self):
        r = {}
        for field in get_all_fields(self):
            v = getattr(self, field)
            v = JsonObj._item_to_json(v)
            if v is not None:
                r[field] = v
        return r

    def _item_to_json(v: Any):
        if isinstance(v, JsonObj):
            return v.to_json()
        if isinstance(v, list):
            return [JsonObj._item_to_json(vl) for vl in v if vl is not None]
        return v

    def __repr__(self) -> str:
        return self.__class__.__name__ + "()"

    def __str__(self) -> str:
        return self.__repr__()


class JsonDynamicObj(JsonObj):
    def __init__(self, json: dict[str, Any]) -> None:
        for key in json:
            setattr(self, key, json[key])
