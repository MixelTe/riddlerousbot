import sys


def main(set=True, dev=False):
    import urllib.parse
    import requests
    try:
        with open("token_dev.txt" if dev else "token.txt") as f:
            token_bot = f.readline().strip()
            f.readline()
            token_webhook = f.readline().strip()
            url = f.readline().strip() + "webhook"
    except Exception as e:
        print(f"Cant read token\n{e}")
        return

    if set:
        method = "setWebhook"
        url_safe = urllib.parse.quote(url, safe="")
        params = f"secret_token={token_webhook}&url={url_safe}"
    else:
        method = "deleteWebhook"
        params = "drop_pending_updates=True"
    r = requests.post(f"https://api.telegram.org/bot{token_bot}/{method}?{params}")
    print(f"{r.status_code}\n {r.content}")


if __name__ == "__main__":
    if (len(sys.argv) == 2 or len(sys.argv) == 3 and sys.argv[2] == "dev") and sys.argv[1] in ("set", "delete"):
        main(sys.argv[1] == "set", sys.argv[-1] == "dev")
    else:
        print("configureWebhook.py [set|delete] [dev]")
