import sys

import tgapi


def main(set=True, dev=False):
    tgapi.configureWebhook(set, config_path="config_dev.txt" if dev else "config.txt")


if __name__ == "__main__":
    if (len(sys.argv) == 2 or len(sys.argv) == 3 and sys.argv[2] == "dev") and sys.argv[1] in ("set", "delete"):
        main(sys.argv[1] == "set", sys.argv[-1] == "dev")
    else:
        print("configureWebhook.py [set|delete] [dev]")
