import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone


def log_request(url):
    tz_utc3 = timezone(timedelta(hours=3))
    timestamp = datetime.now(tz_utc3).strftime("%Y-%m-%d %H:%M:%S")

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status = response.getcode()
            if status == 200:
                print(f"[{timestamp}] INFO: Status {status} OK")
            else:
                body = response.read().decode("utf-8", errors="replace")
                print(f"[{timestamp}] WARNING: Status {status} Body: {body}")
    except urllib.error.HTTPError as e:
        # http error 4xx and 5xx
        body = e.read().decode("utf-8", errors="replace")
        print(f"[{timestamp}] ERROR: Status {e.code} Body: {body}")
    except Exception as e:
        print(f"[{timestamp}] CRITICAL: Connection failed. Reason: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        log_request(target_url)
    else:
        print("Usage: python ping.py <URL>")
        sys.exit(1)


# Откройте редактор crontab:
# crontab -e

# Добавьте строку в конец файла:
# */5 * * * * /usr/bin/python3 /полный/путь/к/вашему_скрипту.py >> /полный/путь/к/логу.log 2>&1

# */5 * * * * означает выполнение каждые 5 минут.
# /usr/bin/python3 — абсолютный путь к интерпретатору Python (можно узнать через which python3).
# >> ... 2>&1 сохраняет вывод и ошибки в лог-файл, что полезно для отладки.
# Сохраните и выйдете. Cron автоматически подхватит изменения.


# Create the file: nano ping.sh
# Make it executable: chmod +x ping.sh
