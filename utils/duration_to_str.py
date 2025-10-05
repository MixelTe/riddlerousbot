from datetime import timedelta

from utils.num_noun import num_noun


def duration_to_str(duration: timedelta):
    t = int(duration.total_seconds())
    if t < 60:
        return f"{t} сек"
    t //= 60
    if t < 60:
        return f"{t} мин"
    t //= 60
    if t < 60:
        return f"{t} ч"
    t //= 24
    return f"{t} {num_noun(t, "день", "дня", "дней")}"
