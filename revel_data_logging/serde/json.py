from datetime import datetime

__all__ = [
    "json_serialize"
]


def json_serialize(o):
    if isinstance(o, datetime):
        return o.isoformat()

    if hasattr(o, "__json__"):
        return o.__json__()

    return str(o)
