from datetime import datetime, timedelta
import pytest
from unittest.mock import patch

# 테스트할 모듈 임포트
from chatweather.weather_api_datetime import get_current_datetime, set_api_datetime


def test_get_current_datetime():
    with patch("chatweather.weather_api_datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 10, 28, 10, 0, 0)
        result = get_current_datetime()
        assert result == datetime(2024, 10, 28, 10, 0, 0), "get_current_datetime 함수가 예상 시간을 반환하지 않습니다."


@pytest.mark.parametrize("test_input,expected", [
    # 당일 6시 이전 -> 당일 6시로 반올림
    (datetime(2024, 10, 28, 4, 30), datetime(2024, 10, 28, 6, 0, 0)),

    # 가장 가까운 3시간 단위로 반올림 (아래는 몇 가지 예시)
    (datetime(2024, 10, 28, 8, 15), datetime(2024, 10, 28, 9, 0, 0)),
    (datetime(2024, 10, 28, 10, 00), datetime(2024, 10, 28, 9, 0, 0)),
    (datetime(2024, 10, 28, 14, 30), datetime(2024, 10, 28, 15, 0, 0)),
    (datetime(2024, 10, 28, 20, 00), datetime(2024, 10, 28, 21, 0, 0)),

    # 자정을 넘기는 경우
    (datetime(2024, 10, 28, 23, 15), datetime(2024, 10, 29, 0, 0, 0)),
])
def test_set_api_datetime(test_input, expected):
    result = set_api_datetime(test_input)
    assert result == expected, f"입력 {test_input}에 대해 예상 결과 {expected}를 반환하지 않았습니다."
