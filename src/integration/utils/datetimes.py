from datetime import UTC, datetime

# import pytz

# tz = pytz.timezone('Europe/Moscow')


def get_timezone_now() -> datetime:
    return datetime.now(UTC)
