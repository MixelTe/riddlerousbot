import logging

from flask import Blueprint, g, request

from bfs import response_msg
from bot.main import process_update
import tgapi


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
    process_update(tgapi.Update(values))
    return "ok"
