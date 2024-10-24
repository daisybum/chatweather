from datetime import datetime

import pytest
from unittest.mock import patch, Mock
from pyWeather.weather import forecast, fetch_current_weather, fetch_forecast_weather

# Sample parameters
valid_params = {
    'city': 'Seoul',
    'serviceKey': 'valid_api_key',
    'lang': 'kr',
    'units': 'metric',
    'target_date': '20231024080000'
}

invalid_api_key_params = {
    'city': 'Seoul',
    'serviceKey': None,
    'lang': 'kr',
    'units': 'metric',
    'target_date': '20231024080000'
}

missing_date_params = {
    'city': 'Seoul',
    'serviceKey': 'valid_api_key',
    'lang': 'kr',
    'units': 'metric',
    'target_date': None
}


# Test for valid current weather request
@patch('pyWeather.weather.requests.get')
def test_fetch_current_weather(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'main': {'temp': 20},
        'weather': [{'description': 'clear sky'}]
    }
    mock_get.return_value = mock_response

    temp, sky, date = fetch_current_weather('Seoul', 'valid_api_key', 'kr', 'metric')

    assert temp == 20
    assert sky == 'clear sky'
    assert date is not None


# Test for valid forecast weather request
@patch('pyWeather.weather.requests.get')
def test_fetch_forecast_weather(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'list': [
            {
                'dt': 1698102000,
                'main': {'temp': 18},
                'weather': [{'description': 'partly cloudy'}]
            }
        ]
    }
    mock_get.return_value = mock_response

    api_datetime = datetime(2023, 10, 24, 8, 0, 0)
    temp, sky, date = fetch_forecast_weather('Seoul', 'valid_api_key', 'kr', 'metric', api_datetime)

    assert temp == 18
    assert sky == 'partly cloudy'
    assert date == api_datetime


# Test for forecast with invalid API key
@patch('pyWeather.weather.requests.get')
def test_forecast_invalid_api_key(mock_get):
    temp, sky, date = forecast(invalid_api_key_params)
    assert temp is None
    assert sky is None
    assert date is None


# Test for forecast with missing target date
def test_forecast_missing_target_date():
    temp, sky, date = forecast(missing_date_params)
    assert temp is None
    assert sky is None
    assert date is None


# Test for 404 city not found
@patch('pyWeather.weather.requests.get')
def test_city_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    temp, sky, date = fetch_current_weather('UnknownCity', 'valid_api_key', 'kr', 'metric')

    assert temp is None
    assert sky is None
    assert date is None
