from datetime import datetime, timedelta


def get_current_date():
    current_date = datetime.now()
    return current_date.strftime("%Y%m%d")
