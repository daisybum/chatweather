import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import requests

from pyWeather.weather import (
    forecast,
    fetch_current_weather,
    fetch_forecast_weather,
    get_current_datetime,
    set_api_datetime,
)

# 성공적인 현재 날씨 조회 테스트
def test_current_weather_success():
    fixed_now = datetime(2021, 1, 1, 12, 0, 0)
    params = {
        'city': 'Seoul',
        'serviceKey': 'valid_api_key',
        'target_date': fixed_now.strftime("%Y%m%d%H%M%S"),
    }

    sample_response = {
        'main': {'temp': 20},
        'weather': [{'description': '맑음'}],
    }
    mock_response = Mock()
    mock_response.json.return_value = sample_response
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        with patch('pyWeather.weather.get_current_datetime', return_value=fixed_now):
            temp, sky, dt = forecast(params)

            assert temp == 20
            assert sky == '맑음'
            assert dt == fixed_now

# 성공적인 예보 날씨 조회 테스트
def test_forecast_weather_success():
    fixed_now = datetime(2021, 1, 1, 12, 0, 0)
    target_date = fixed_now + timedelta(days=1)
    params = {
        'city': 'Seoul',
        'serviceKey': 'valid_api_key',
        'target_date': target_date.strftime("%Y%m%d%H%M%S"),
    }

    sample_response = {
        'list': [
            {
                'dt': int(target_date.timestamp()),
                'main': {'temp': 15},
                'weather': [{'description': '구름 조금'}],
            }
        ]
    }
    mock_response = Mock()
    mock_response.json.return_value = sample_response
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        with patch('pyWeather.weather.set_api_datetime', return_value=target_date):
            temp, sky, dt = forecast(params)

            assert temp == 15
            assert sky == '구름 조금'
            assert dt == target_date

# API 키 누락 테스트
def test_forecast_missing_api_key(capsys):
    params = {
        'city': 'Seoul',
        'target_date': '20210101120000',
    }
    temp, sky, dt = forecast(params)
    captured = capsys.readouterr()
    assert "Error: API 키 ('serviceKey')가 필요합니다." in captured.out
    assert temp is None
    assert sky is None
    assert dt is None

# target_date 누락 테스트
def test_forecast_missing_target_date(capsys):
    params = {
        'city': 'Seoul',
        'serviceKey': 'valid_api_key',
    }
    temp, sky, dt = forecast(params)
    captured = capsys.readouterr()
    assert "Error: 'target_date' 파라미터가 필요합니다." in captured.out
    assert temp is None
    assert sky is None
    assert dt is None

# 잘못된 target_date 형식 테스트
def test_forecast_invalid_target_date_format(capsys):
    params = {
        'city': 'Seoul',
        'serviceKey': 'valid_api_key',
        'target_date': 'invalid_date',
    }
    temp, sky, dt = forecast(params)
    captured = capsys.readouterr()
    assert "Error: 'target_date' 파싱 중 오류 발생" in captured.out
    assert temp is None
    assert sky is None
    assert dt is None

# 잘못된 도시 이름 테스트
def test_forecast_invalid_city_name(capsys):
    params = {
        'city': 'InvalidCity',
        'serviceKey': 'valid_api_key',
        'target_date': '20210101120000',
    }

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_response.reason = 'Not Found'

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        temp, sky, dt = forecast(params)
        captured = capsys.readouterr()
        assert "Error: 도시 'InvalidCity'를 찾을 수 없습니다." in captured.out
        assert temp is None
        assert sky is None
        assert dt is None

# 잘못된 API 키 테스트
def test_forecast_invalid_api_key(capsys):
    params = {
        'city': 'Seoul',
        'serviceKey': 'invalid_api_key',
        'target_date': '20210101120000',
    }

    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_response.reason = 'Unauthorized'

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        temp, sky, dt = forecast(params)
        captured = capsys.readouterr()
        assert "Error: 잘못된 API 키입니다." in captured.out
        assert temp is None
        assert sky is None
        assert dt is None

# fetch_current_weather 함수 직접 테스트
def test_fetch_current_weather():
    city = 'Seoul'
    api_key = 'valid_api_key'
    lang = 'kr'
    units = 'metric'
    fixed_now = datetime(2021, 1, 1, 12, 0, 0)

    sample_response = {
        'main': {'temp': 20},
        'weather': [{'description': '맑음'}],
    }
    mock_response = Mock()
    mock_response.json.return_value = sample_response
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        with patch('pyWeather.weather.get_current_datetime', return_value=fixed_now):
            temp, sky, dt = fetch_current_weather(city, api_key, lang, units)
            assert temp == 20
            assert sky == '맑음'
            assert dt == fixed_now

# fetch_forecast_weather 함수 직접 테스트
def test_fetch_forecast_weather():
    city = 'Seoul'
    api_key = 'valid_api_key'
    lang = 'kr'
    units = 'metric'
    target_date = datetime(2021, 1, 2, 12, 0, 0)

    sample_response = {
        'list': [
            {
                'dt': int(target_date.timestamp()),
                'main': {'temp': 15},
                'weather': [{'description': '구름 조금'}],
            }
        ]
    }
    mock_response = Mock()
    mock_response.json.return_value = sample_response
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        temp, sky, dt = fetch_forecast_weather(city, api_key, lang, units, target_date)
        assert temp == 15
        assert sky == '구름 조금'
        assert dt == target_date

# 예보 데이터 미존재 테스트
def test_forecast_no_matching_forecast(capsys):
    fixed_now = datetime(2021, 1, 1, 12, 0, 0)
    target_date = fixed_now + timedelta(days=1)
    params = {
        'city': 'Seoul',
        'serviceKey': 'valid_api_key',
        'target_date': target_date.strftime("%Y%m%d%H%M%S"),
    }

    sample_response = {
        'list': [
            {
                'dt': int((target_date + timedelta(hours=3)).timestamp()),
                'main': {'temp': 15},
                'weather': [{'description': '구름 조금'}],
            }
        ]
    }
    mock_response = Mock()
    mock_response.json.return_value = sample_response
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    with patch('pyWeather.weather.requests.get', return_value=mock_response):
        with patch('pyWeather.weather.set_api_datetime', return_value=target_date):
            temp, sky, dt = forecast(params)
            captured = capsys.readouterr()
            assert "지정된 날짜와 시간에 대한 예보를 찾을 수 없습니다." in captured.out
            assert temp is None
            assert sky is None
            assert dt is None
