import logging

from bafser import response_msg
from flask import Blueprint, g, request

import tgapi
from bot.main import process_update

blueprint = Blueprint("api", __name__)


@blueprint.post("/webhook")
def webhook():
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if (not tgapi.check_webhook_token(token)):
        return response_msg("wrong token", 403)

    values, is_json = g.json
    if not is_json:
        return response_msg("body is not json", 415)

    logging.info(f"webhook: {values}")
    process_update(tgapi.Update.new(values).valid())
    return "ok"
