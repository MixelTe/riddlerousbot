import tgapi
from bot.bot import Bot

bot = Bot()


def setup_bot():
    bot.init()


def process_update(update: tgapi.Update):
    print(update)
    bot.process_update(update)
