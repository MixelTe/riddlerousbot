def parse_int(v: str, default: int = None):
    try:
        return int(v)
    except Exception:
        return default
