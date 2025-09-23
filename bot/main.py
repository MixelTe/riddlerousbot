import tgapi
from bot.bot import Bot

bot = Bot()


def setup_bot():
    bot.init()


def process_update(update: tgapi.Update):
    print(f"Update(update_id={update.update_id})")
    bot.process_update(update)
