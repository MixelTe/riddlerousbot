import sys

from bafser import AppConfig, create_app

import tgapi
from bot.main import process_update, setup_bot
from scripts.init_db import init_db

tgapi.setup("token_dev.txt" if __name__ == "__main__" else "token.txt")
setup_bot()
app, run = create_app(__name__, AppConfig(
    MESSAGE_TO_FRONTEND="",
    DEV_MODE="dev" in sys.argv,
    DELAY_MODE="delay" in sys.argv,
))

run(False, init_db)

if __name__ == "__main__":
    print("listening for updates...")
    update_id = -1
    while True:
        ok, updates = tgapi.getUpdates(update_id + 1, 60)
        if not ok:
            print("Error!", updates)
            break
        for update in updates:
            update_id = max(update_id, update.update_id)
            process_update(update)
