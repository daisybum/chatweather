# test_config.py
import os
import pytest
from unittest.mock import patch

# 테스트할 모듈 임포트
from chatweather.config import get_openai_api_key, get_weather_api_key

def test_get_openai_api_key():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}):
        assert get_openai_api_key() == "test_openai_key", "get_openai_api_key 함수가 예상 값을 반환하지 않습니다."

def test_get_weather_api_key():
    with patch.dict(os.environ, {"WEATHER_API_KEY": "test_weather_key"}):
        assert get_weather_api_key() == "test_weather_key", "get_weather_api_key 함수가 예상 값을 반환하지 않습니다."
