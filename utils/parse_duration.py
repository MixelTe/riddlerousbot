from datetime import timedelta

from utils.parse_int import parse_int


def parse_duration(duration: str):
    if len(duration) < 2:
        return timedelta(), False
    unit = duration[-1]
    value = parse_int(duration[:-1])
    if value is None:
        return timedelta(), False
    match unit:
        case "m": return timedelta(minutes=value), True
        case "h": return timedelta(hours=value), True
        case "d": return timedelta(days=value), True
    return timedelta(), False
