import sys
from bfs import AppConfig, create_app
from scripts.init_values import init_values
from bot.main import process_update
import tgapi


tgapi.setup()
app, run = create_app(__name__, AppConfig(
    MESSAGE_TO_FRONTEND="",
    DEV_MODE="dev" in sys.argv,
    DELAY_MODE="delay" in sys.argv,
))

# run(__name__ == "__main__", lambda: init_dev_values(True), port=5001)

run(False, lambda: init_values(True))

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
