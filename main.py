import sys

import bafser_tgapi as tgapi
from bafser import AppConfig, create_app

from bot.bot import Bot
from utils.init_db import init_db

app, run = create_app(__name__, AppConfig(DEV_MODE="dev" in sys.argv))
tgapi.setup(botCls=Bot, app=app)

run(False, init_db)

if __name__ == "__main__":
    tgapi.run_long_polling()
else:
    tgapi.set_webhook()
