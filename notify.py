from datetime import datetime, timedelta
import bafser_tgapi as tgapi

with open("notify.txt") as f:
    date = datetime.fromisoformat(f.readline().strip())
    chat_id = f.readline().strip()

delta = date - datetime.now()
if delta > timedelta(days=2):
    exit()

tgapi.setup()
tgapi.sendMessage(chat_id, "💤 Falling asleep...")
