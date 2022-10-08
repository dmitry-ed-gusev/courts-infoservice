from datetime import datetime, timedelta


def daterange(date1: datetime, date2: datetime) -> list[datetime]:
    result = []
    for n in range(int((date2 - date1).days) + 1):
        result.append((date1 + timedelta(days=n)))

    return result
