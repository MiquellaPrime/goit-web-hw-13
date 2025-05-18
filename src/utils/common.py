from datetime import datetime, timezone


def current_time() -> datetime:
    """
    Returns the current UTC datetime without microseconds.

    :return: Current UTC datetime.
    :rtype: datetime
    """
    return datetime.now(timezone.utc).replace(microsecond=0)
