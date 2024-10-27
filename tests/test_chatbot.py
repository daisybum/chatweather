import pytest
from unittest.mock import MagicMock
from pyWeather.chatbot import (
    make_extracting_prompt,
    call_openai_api,
    extract_city_and_date,
    generate_weather_info,
    generate_weather_response,
    query
)

def test_make_extracting_prompt(monkeypatch):
    # get_current_datetime 함수를 모의로 설정
    monkeypatch.setattr('pyWeather.chatbot.get_current_datetime', lambda: '20231024120000')
    query = "내일 뉴욕 날씨 어때?"
    prompt = make_extracting_prompt(query)
    # 프롬프트에 질의와 현재 시간이 포함되어 있는지 확인
    assert f'질의: "{query}"' in prompt
    assert "현재 시간은 20231024120000입니다." in prompt

def test_call_openai_api(monkeypatch):
    # OpenAI API 응답을 모의로 설정
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '테스트 응답 내용'

    def mock_create(*args, **kwargs):
        return mock_response

    monkeypatch.setattr('openai.ChatCompletion.create', mock_create)

    prompt = "테스트 프롬프트"
    system_content = "테스트 시스템 컨텐츠"
    response = call_openai_api(prompt, system_content)
    assert response == '테스트 응답 내용'

def test_extract_city_and_date(monkeypatch):
    # get_current_datetime과 call_openai_api 함수를 모의로 설정
    monkeypatch.setattr('pyWeather.chatbot.get_current_datetime', lambda: '20231024120000')

    def mock_call_openai_api(prompt, system_content, max_tokens=150, temperature=0.7):
        return '''
        {
          "city": "New York",
          "date": "20231025120000"
        }
        '''

    monkeypatch.setattr('pyWeather.chatbot.call_openai_api', mock_call_openai_api)

    query = "내일 뉴욕 날씨 어때?"
    city, date_str = extract_city_and_date(query)
    assert city == "New York"
    assert date_str == "20231025120000"

def test_generate_weather_info(monkeypatch):
    # forecast 함수를 모의로 설정
    def mock_forecast(params):
        return 20.0, '맑음', '2023-10-25 12:00:00'

    monkeypatch.setattr('pyWeather.chatbot.forecast', mock_forecast)

    city = 'New York'
    target_date = '20231025120000'
    temp, sky, date_time = generate_weather_info(city, target_date)
    assert temp == 20.0
    assert sky == '맑음'
    assert date_time == '2023-10-25 12:00:00'

def test_generate_weather_response(monkeypatch):
    # 함수들의 반환 값을 모의로 설정
    monkeypatch.setattr('pyWeather.chatbot.extract_city_and_date', lambda query: ('New York', '20231025120000'))
    monkeypatch.setattr('pyWeather.chatbot.generate_weather_info', lambda city, date: (20.0, '맑음', '2023-10-25 12:00:00'))

    def mock_call_openai_api(prompt, system_content, max_tokens=200, temperature=0.7):
        return '뉴욕의 10월 25일 날씨는 맑음이며, 기온은 20도입니다.'

    monkeypatch.setattr('pyWeather.chatbot.call_openai_api', mock_call_openai_api)

    query = "내일 뉴욕 날씨 어때?"
    response = generate_weather_response(query)
    expected_response = '뉴욕의 10월 25일 날씨는 맑음이며, 기온은 20도입니다.'
    assert response == expected_response

def test_query(monkeypatch):
    # generate_weather_response 함수를 모의로 설정
    monkeypatch.setattr('pyWeather.chatbot.generate_weather_response', lambda query: '테스트 날씨 응답입니다.')

    query_text = "내일 뉴욕 날씨 어때?"
    response = query(query_text)
    assert response == '테스트 날씨 응답입니다.'
