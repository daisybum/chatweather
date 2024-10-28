import pytest
from unittest.mock import patch
from chatweather.chatbot import (
    make_extracting_prompt,
    extract_city_and_date,
    generate_weather_info,
    generate_weather_response,
    chat_loop,
)
from datetime import datetime


@pytest.fixture
def mock_get_current_datetime():
    with patch('chatweather.chatbot.get_current_datetime') as mock_datetime:
        mock_datetime.return_value = datetime(2023, 10, 27, 12, 0, 0)
        yield mock_datetime


@pytest.fixture
def mock_call_openai_api():
    with patch('chatweather.chatbot.call_openai_api') as mock_api:
        yield mock_api


@pytest.fixture
def mock_forecast():
    with patch('chatweather.chatbot.forecast') as mock_forecast:
        yield mock_forecast


def test_make_extracting_prompt():
    query = "오늘 서울 날씨 어때?"
    prompt = make_extracting_prompt(query, current_time="2023-10-27 12:00:00")
    assert "사용자의 질의에서 도시(영어명)와 날짜를 추출해주세요." in prompt
    assert f'질의: "{query}"' in prompt


def test_extract_city_and_date(mock_get_current_datetime, mock_call_openai_api):
    mock_call_openai_api.return_value = '{"city": "Seoul", "date": "20231027120000"}'
    city, date_str = extract_city_and_date("오늘 서울 날씨 어때?")
    assert city == "Seoul"
    assert date_str == "20231027120000"


def test_generate_weather_info(mock_forecast):
    mock_forecast.return_value = (20.0, "맑음", "2023-10-27 12:00:00")
    temp, sky, date_time = generate_weather_info("Seoul", "20231027120000")
    assert temp == 20.0
    assert sky == "맑음"
    assert date_time == "2023-10-27 12:00:00"


def test_generate_weather_response(mock_call_openai_api):
    conversation_history = []
    mock_call_openai_api.return_value = "오늘 서울은 맑고 기온은 20도입니다. 즐거운 하루 보내세요!"

    with patch('chatweather.chatbot.extract_city_and_date') as mock_extract, \
            patch('chatweather.chatbot.generate_weather_info') as mock_weather_info:
        mock_extract.return_value = ("Seoul", "20231027120000")
        mock_weather_info.return_value = (20.0, "맑음", "2023-10-27 12:00:00")
        response = generate_weather_response("오늘 서울 날씨 어때?", conversation_history)
        assert "오늘 서울은 맑고 기온은 20도입니다." in response


def test_chat_loop(monkeypatch, capsys):
    inputs = iter([
        "안녕",
        "오늘 부산 날씨 알려줘",
        "내일은 어때?",
        "exit"
    ])

    def mock_input(prompt):
        return next(inputs)

    monkeypatch.setattr('builtins.input', mock_input)

    with patch('chatweather.chatbot.call_openai_api') as mock_call_openai_api, \
            patch('chatweather.chatbot.extract_city_and_date') as mock_extract, \
            patch('chatweather.chatbot.generate_weather_info') as mock_weather_info:
        mock_call_openai_api.side_effect = [
            "안녕하세요! 무엇을 도와드릴까요?",
            "부산의 2023-10-28 12:00:00 날씨는 맑음이며, 기온은 22.0도입니다. 즐거운 하루 보내세요!",
            "내일은 좋은 날씨가 예상됩니다.",
        ]
        mock_extract.return_value = ("Busan", "20231028120000")
        mock_weather_info.return_value = (22.0, "맑음", "2023-10-28 12:00:00")

        chat_loop()

    captured = capsys.readouterr()
    expected_outputs = [
        "챗봇을 시작합니다. 'exit'을 입력하여 종료할 수 있습니다.",
        "날씨 정보를 얻기 위해 꼭 %%'날씨'%% 라는 단어를 포함한 질문을 입력하세요.",
        "ex) '서울 날씨 어때?', '내일 부산 날씨 알려줘'",
        "응답: 안녕하세요! 무엇을 도와드릴까요?",
        "응답: 부산의 2023-10-28 12:00:00 날씨는 맑음이며, 기온은 22.0도입니다. 즐거운 하루 보내세요!",
        "응답: 내일은 좋은 날씨가 예상됩니다.",
        "챗봇을 종료합니다.",
    ]
    for expected_output in expected_outputs:
        assert expected_output in captured.out
