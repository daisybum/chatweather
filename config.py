# config.py

# API 키를 하드코딩하여 설정
_openai_api_key = ""  # 이곳에 단독 OpenAI API 키를 설정
_weather_api_key = ""  # 이곳에 단독 날씨 API 키를 설정

def get_openai_api_key():
    """기본 OpenAI API 키를 반환하는 함수"""
    return _openai_api_key

def get_weather_api_key():
    """기본 날씨 API 키를 반환하는 함수"""
    return _weather_api_key
