import openai
import re
from datetime import datetime, timedelta
from pyWeather.weather import forecast, get_current_date, get_current_hour

# OpenAI API 키 설정 (GPT-4.0-mini 모델을 사용)
openai.api_key = "your_openai_api_key"


def extract_city_and_date(query):
    """
    사용자 질의에서 도시와 날짜를 추출하는 함수.
    """
    # 날짜 패턴 매칭 (오늘, 내일, 모레 등)
    date_match = re.search(r"(오늘|내일|모레)", query)
    date_str = date_match.group(1) if date_match else None

    # 도시 이름 추출 (간단한 패턴 예시)
    city_match = re.search(r"(서울|부산|대구|인천|광주|대전|울산|하와이|뉴욕|런던|파리)", query)
    city = city_match.group(1) if city_match else "서울"  # 도시가 없으면 기본값으로 서울 설정

    # 날짜 계산
    if date_str == "내일":
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    elif date_str == "모레":
        target_date = (datetime.now() + timedelta(days=2)).strftime("%Y%m%d")
    else:
        target_date = get_current_date()

    return city, target_date


def query_gpt4_mini(query):
    """
    GPT-4.0-mini API를 호출하여 자연어 응답을 생성하는 함수.
    """
    response = openai.Completion.create(
        engine="gpt-4.0-mini",  # GPT-4.0-mini 모델 사용
        prompt=query,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


def generate_weather_response(query):
    """
    사용자의 질의에서 정보를 추출하고, 해당 정보를 바탕으로 날씨 응답을 생성하는 함수.
    """
    # 질의에서 도시와 날짜 추출
    city, target_date = extract_city_and_date(query)

    # 날씨 API 호출을 위한 파라미터 설정
    params = {
        'serviceKey': 'your_weather_api_key',  # 기상청 또는 날씨 API 키
        'pageNo': '1',
        'numOfRows': '10',
        'dataType': 'XML',
        'base_date': target_date,
        'base_time': get_current_hour(),
        'nx': '55',  # 서울의 경우, 필요에 따라 좌표 매핑을 추가
        'ny': '127'
    }

    # 날씨 정보를 가져옴
    temp, sky = forecast(params)

    # GPT-4.0-mini로 자연스러운 응답 생성
    weather_info = f"{city}의 {target_date} 날씨는 {sky}이고, 기온은 {temp}도입니다."
    prompt = f"사용자에게 다음 정보에 대해 설명해줘: {weather_info}. "

    gpt_response = query_gpt4_mini(prompt)
    return gpt_response


def query(query_text):
    """
    사용자의 질의에 대해 GPT-4.0-mini와 날씨 API를 사용해 응답하는 함수.
    """
    # 사용자의 질의에서 정보를 추출하고 응답 생성
    return generate_weather_response(query_text)
