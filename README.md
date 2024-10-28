# ChatWeather

ChatWeather는 OpenAI의 GPT 모델과 OpenWeatherMap API를 통합하여 사용자에게 날씨 정보를 제공하는 챗봇 애플리케이션입니다. 자연어로 된 사용자의 질문을 이해하고, 해당하는 도시와 날짜의 날씨 정보를 친절하게 응답합니다.

## 목적 및 소개

- **자연어 처리**: 사용자의 질문에서 도시와 날짜를 추출하여 정확한 날씨 정보를 제공합니다.
- **날씨 정보 제공**: 현재 날씨 및 예보 데이터를 OpenWeatherMap API를 통해 받아옵니다.
- **대화형 인터페이스**: 이전 대화를 기억하여 보다 자연스럽고 연속적인 대화를 지원합니다.

## 주요 기능

- **실시간 날씨 조회**: 현재 시각의 날씨 정보를 제공합니다.
- **미래 날씨 예보**: 최대 5일까지의 날씨 예보를 제공합니다.
- **다국어 지원**: 한국어를 비롯한 여러 언어로 날씨 정보를 제공합니다.
- **오류 처리**: 잘못된 입력이나 예외 상황에 대한 견고한 오류 처리를 제공합니다.

## 설치 방법

### 요구 사항

- Python 3.8 이상
- OpenAI API 키
- OpenWeatherMap API 키

### 패키지 설치

또는 소스 코드를 클론하여 설치:

```bash
git clone https://github.com/daisybum/pyWeather.git
cd pyWeather
pip install -e .
```

# 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key
WEATHER_API_KEY=your_openweathermap_api_key
```

your_openai_api_key와 your_openweathermap_api_key를 실제 발급받은 API 키로 대체하세요.


`your_openai_api_key`와 `your_openweathermap_api_key`를 실제 발급받은 API 키로 대체하세요.

## 사용 방법

### 챗봇 실행

```bash
python -m chatweather.chatbot
```

이후 콘솔에 나타나는 안내에 따라 질문을 입력하면 챗봇이 응답합니다.

## 예시

```makefile
질문을 입력하세요: 서울의 내일 날씨 알려줘
응답: 서울의 2024-10-29 12:00:00 날씨는 맑음이며, 기온은 18도입니다.

질문을 입력하세요: 부산에서 모레 비 올까?
응답: 부산의 2024-10-30 12:00:00 날씨는 약한 비이며, 기온은 16도입니다.
```

## 모듈 설명

### `config.py`

환경 변수를 로드하고 API 키를 가져오는 함수들을 포함합니다.

- `get_openai_api_key()`: OpenAI API 키를 반환합니다.
- `get_weather_api_key()`: OpenWeatherMap API 키를 반환합니다.

### `weather.py`

날씨 데이터를 가져오는 함수들을 포함합니다.

- `forecast(params)`: 주어진 파라미터에 따라 현재 날씨 또는 예보 데이터를 반환합니다.
- `fetch_current_weather(...)`: 현재 날씨 데이터를 가져옵니다.
- `fetch_forecast_weather(...)`: 예보 데이터를 가져옵니다.

### `weather_api_datetime.py`

날짜와 시간을 처리하는 유틸리티 함수들을 포함합니다.

- `get_current_datetime()`: 현재 날짜와 시간을 반환합니다.
- `set_api_datetime(date_time)`: API 요구 사항에 맞게 시간을 조정합니다.

### `chatbot.py`

챗봇의 메인 로직을 포함합니다.

- `extract_city_and_date(query)`: 사용자의 질문에서 도시와 날짜를 추출합니다.
- `generate_weather_info(city, target_date)`: 날씨 정보를 가져옵니다.
- `generate_weather_response(query, conversation_history)`: 사용자에게 응답할 메시지를 생성합니다.
- `chat_loop()`: 사용자와의 대화 루프를 실행합니다.

## 테스트하기

`pytest`를 사용하여 작성된 테스트 코드를 실행하여 각 모듈의 기능을 검증할 수 있습니다.

```bash
pytest
```

## 패키지 만들기 및 배포

패키지를 배포하기 위해 다음 명령어를 실행하세요.

1. 패키지 만들기

   ```bash
   python setup.py sdist bdist_wheel
    ```
2. PyPI에 업로드

   ```bash
   python -m twine upload dist/*
   ```


## 종속성

- `requests`
- `python-dotenv`
- `openai==1.52.2`
- `pytest==8.3.3`

---

## 라이선스

이 프로젝트는 Apache License 2.0 라이선스 하에 배포됩니다.

---

## 문의

- **작성자**: 박상현
- **이메일**: hirvahapjh@gmail.com
- **GitHub**: [daisybum](https://github.com/daisybum)

---

## 업데이트 내역

- **0.1.9**: 첫 번째 버전 릴리스
