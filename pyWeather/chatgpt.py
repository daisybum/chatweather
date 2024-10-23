import json

import openai
from config import get_openai_api_key, get_weather_api_key
from pyWeather.weather import forecast
from pyWeather.weather_api_datetime import get_current_datetime

# OpenAI API 키 설정 (단독 기본 API 키 사용)
openai.api_key = get_openai_api_key()


def extract_city_and_date(query):
    """
    Uses GPT-4.0-mini to infer the city and date from the user's query.
    """
    # Prompt GPT to extract city and date
    prompt = f"""
사용자의 질의에서 도시(영어명)와 날짜를 추출해주세요. 현재 시간, %Y%m%d은 {get_current_datetime()}입니다.

질의: "{query}"

요구사항:
- 'city': 질의에서 언급된 도시 이름을 추출한 후, 영어로 반환하세요. 언급되지 않았다면 기본값으로 'seoul'을 사용하세요.
- 도시 이름의 첫 글짜는 대문자로 변환하고 여러 단어로 이루어진 경우 각 단어의 첫 글자를 대문자로 변환하세요. 그리고 띄어쓰기를 하세요.
- 'date': 질의에서 언급된 날짜를 'YYYYMMDDHHMMSS' 형식으로 변환하여 추출하세요. '오늘', '내일', '모레'와 같은 상대적 날짜도 변환하세요. 언급되지 않았다면 오늘 날짜를 사용하세요.
- 만약 date의 시간을 특정하지 않는 경우 12시 정각으로 설정해주세요.
- JSON 형식으로 출력하되 '''{{...}}''' 형태로 출력해주세요.

결과는 다음 JSON 형식으로 제공해주세요:
{{
  "city": "도시 이름(영어명)",
  "date": "YYYYMMDDHHMMSS"
}}
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "도시와 날짜 추출"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )

    output = response.choices[0].message.content.strip()
    output = '{' + output.split('{')[-1].split('}')[0] + '}'

    # JSON 파싱
    try:
        data = json.loads(output)
        city = data.get('city', 'seoul')
        date_str = data.get('date', get_current_datetime())
    except json.JSONDecodeError:
        # 파싱 실패 시 기본값 사용
        city = 'seoul'
        date_str = get_current_datetime()

    return city, date_str


def query_gpt4_mini(prompt):
    """
    GPT-4.0-mini API를 호출하여 자연어 응답을 생성하는 함수.
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # GPT-4.0-mini 모델 사용
        messages=[
            {"role": "system", "content": "날씨 정보 생성"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_weather_response(query):
    """
    사용자의 질의에서 정보를 추출하고, 해당 정보를 바탕으로 날씨 응답을 생성하는 함수.
    """
    # 질의에서 도시와 날짜 추출
    city, target_date = extract_city_and_date(query)

    params = {
        'city': city,
        'serviceKey': get_weather_api_key(),
        "target_date": target_date,
        "lang": 'kr',  # 한국어 설정,
        "units": 'metric',  # 섭씨로 변경
    }

    # 날씨 정보를 가져옴
    temp, sky, date_time = forecast(params)

    # GPT-4.0-mini로 자연스러운 응답 생성
    weather_info = f"{city}의 {date_time} 날씨는 {sky}이고, 기온은 {temp}도입니다."
    prompt = f"사용자에게 다음 정보에 대해 설명해줘: {weather_info}. "

    gpt_response = query_gpt4_mini(prompt)
    return gpt_response


def query(query_text):
    """
    사용자의 질의에 대해 GPT-4.0-mini와 날씨 API를 사용해 응답하는 함수.
    """
    # 사용자의 질의에서 정보를 추출하고 응답 생성
    return generate_weather_response(query_text)
