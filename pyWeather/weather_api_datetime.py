from datetime import datetime, timedelta


def get_current_datetime():
    current_date = datetime.now()
    return current_date.strftime("%Y-%m-%d %H:%M:%S")


def set_api_datetime(date_time):
    """
    주어진 날짜/시간을 3시간 단위로 맞춰 가장 가까운 시간을 반환하는 함수.
    API는 6, 9, 12, 15, 18, 21, 0, 3시의 데이터를 제공하므로,
    주어진 시간에서 가장 가까운 3시간 단위로 시간을 반올림합니다.

    Args:
        date_time (datetime): 기준이 되는 날짜와 시간 (datetime 객체)

    Returns:
        str: 'YYYY-MM-DD HH:MM:SS' 형식으로 가장 가까운 3시간 단위의 시간을 반환
    """

    # 만약 날짜 시간이 당일 6시 이전이면 당일 6시를 반환
    today = datetime.now().date()
    if (date_time.date() == today) & (date_time.hour < 6):
        return date_time.replace(hour=6, minute=0, second=0, microsecond=0)

    # 주어진 시간이 몇 시인지 확인
    hour = date_time.hour

    # 3시간 단위로 반올림 (6, 9, 12, 15, 18, 21, 0, 3)
    rounded_hour = round(hour / 3) * 3

    # 만약 반올림한 시간이 24시가 넘으면 다음날로 넘김
    if rounded_hour == 24:
        date_time = date_time + timedelta(days=1)
        rounded_hour = 0

    # 최종적으로 반올림된 시간으로 업데이트
    rounded_date_time = date_time.replace(hour=rounded_hour, minute=0, second=0, microsecond=0)
    return rounded_date_time
