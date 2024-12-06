from datetime import datetime, timedelta
import logging


def custom_time(*args):
    utc_dt = datetime.utcnow()
    utc_dt += timedelta(hours=3)
    return utc_dt.timetuple()


class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno == logging.INFO and rec.name == "root"


def set_logging():
    logging.basicConfig(
        level=logging.INFO,
        # filename="log.log",
        format=u"[%(asctime)s] %(levelname)s in %(module)s (%(name)s): %(message)s",
        encoding="utf-8"
    )
    logger = logging.getLogger()
    logger.handlers.clear()
    logging.Formatter.converter = custom_time

    file_handler_error = logging.FileHandler("log_errors.log", mode="a", encoding="utf-8")
    file_handler_error.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    file_handler_error.setLevel(logging.WARNING)
    file_handler_error.encoding = "utf8"
    logger.addHandler(file_handler_error)

    file_handler_info = logging.FileHandler("log_info.log", mode="a", encoding="utf-8")
    file_handler_info.setFormatter(logging.Formatter("[%(asctime)s] in %(module)s: %(message)s"))
    file_handler_info.addFilter(InfoFilter())
    file_handler_info.encoding = "utf8"
    logger.addHandler(file_handler_info)
