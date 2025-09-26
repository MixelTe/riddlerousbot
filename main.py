import sys

from bafser import AppConfig, create_app

import tgapi
from bot.bot import Bot
from scripts.init_db import init_db

app, run = create_app(__name__, AppConfig(
    MESSAGE_TO_FRONTEND="",
    DEV_MODE="dev" in sys.argv,
    DELAY_MODE="delay" in sys.argv,
))

tgapi.setup(
    config_path="config_dev.txt" if __name__ == "__main__" else "config.txt",
    botCls=Bot,
    import_folder="bot",
    app=app,
)

run(False, init_db)

if __name__ == "__main__":
    tgapi.run_long_polling()
else:
    tgapi.set_webhook()
