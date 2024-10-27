import json
import openai
from config import get_openai_api_key, get_weather_api_key
from pyWeather.weather import forecast
from pyWeather.weather_api_datetime import get_current_datetime

# OpenAI API 키 설정
openai.api_key = get_openai_api_key()


def make_extracting_prompt(query):
    """
    사용자 질의에서 도시와 날짜를 추출하기 위한 프롬프트를 생성합니다.

    Args:
        query (str): 사용자의 질의 문장.

    Returns:
        str: GPT에 전달할 프롬프트 문자열.
    """
    current_time = get_current_datetime()
    prompt = f"""
사용자의 질의에서 도시(영어명)와 날짜를 추출해주세요. 현재 시간은 {current_time}입니다.

질의: "{query}"

요구사항:
- 'city': 질의에서 언급된 도시 이름을 영어로 반환하세요. 언급되지 않았다면 기본값으로 'Seoul'을 사용하세요.
- 'date': 질의에서 언급된 날짜를 'YYYYMMDDHHMMSS' 형식으로 변환하여 반환하세요. '오늘', '내일', '모레' 등의 상대적 날짜도 변환하세요.
- 결과를 JSON 형식으로 '''{{...}}''' 형태로 출력해주세요.

주의 사항:
- 질의의 띄어쓰기, 맞춤법, 오탈자를 먼저 수정하세요.
- 도시 이름의 각 단어 첫 글자를 대문자로 변환하세요.
- 날짜의 시간이 특정되지 않았다면 12시 정각으로 설정하세요. 날짜가 언급되지 않았다면 현재 날짜를 사용하세요.
- 오늘의 날씨에 대한 질의이면서, 특정 시간을 언급하지 않는 경우 현재 시간을 사용하세요.

결과 예시:
{{
  "city": "Seoul",
  "date": "YYYYMMDDHHMMSS"
}}
"""
    return prompt


def call_openai_api(prompt, system_content, max_tokens=150, temperature=0.7):
    """
    OpenAI ChatCompletion API를 호출하는 함수.

    Args:
        prompt (str): GPT에 전달할 프롬프트.
        system_content (str): 시스템 역할의 컨텐츠.
        max_tokens (int, optional): 최대 토큰 수. 기본값은 150.
        temperature (float, optional): 생성 온도. 기본값은 0.7.

    Returns:
        str: OpenAI의 응답 내용.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        return None


def extract_city_and_date(query):
    """
    사용자의 질의에서 도시와 날짜를 추출하는 함수.

    Args:
        query (str): 사용자의 질의 문장.

    Returns:
        tuple: (city, date_str)
            - city (str): 추출된 도시 이름 (영어).
            - date_str (str): 'YYYYMMDDHHMMSS' 형식의 날짜 문자열.
    """
    prompt = make_extracting_prompt(query)
    current_time = get_current_datetime()
    system_content = "도시와 날짜 추출"

    # OpenAI API 호출
    output = call_openai_api(prompt, system_content)

    if output is None:
        return 'Seoul', current_time

    # 응답에서 JSON 부분만 추출
    try:
        json_str = output.split('{', 1)[1].rsplit('}', 1)[0]
        json_str = '{' + json_str + '}'
        data = json.loads(json_str)
        city = data.get('city', 'Seoul')
        date_str = data.get('date', current_time)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"JSON 파싱 오류: {e}")
        city = 'Seoul'
        date_str = current_time

    return city, date_str


def generate_weather_info(city, target_date):
    """
    날씨 정보를 가져오는 함수.

    Args:
        city (str): 도시 이름.
        target_date (str): 'YYYYMMDDHHMMSS' 형식의 날짜 문자열.

    Returns:
        tuple: (temp, sky, date_time)
            - temp (float): 기온.
            - sky (str): 날씨 상태.
            - date_time (str): 날짜 및 시간 문자열.
    """
    params = {
        'city': city,
        'serviceKey': get_weather_api_key(),
        'target_date': target_date,
        'lang': 'kr',  # 한국어 설정
        'units': 'metric',  # 섭씨로 설정
    }

    # 날씨 정보 가져오기
    temp, sky, date_time = forecast(params)

    if temp is None or sky is None:
        print("날씨 정보를 가져오는 데 실패했습니다.")
        return None, None, None

    return temp, sky, date_time


def generate_weather_response(query):
    """
    사용자의 질의로부터 날씨 정보를 생성하는 함수.

    Args:
        query (str): 사용자의 질의 문장.

    Returns:
        str: 사용자를 위한 날씨 정보 응답.
    """
    # 도시와 날짜 추출
    city, target_date = extract_city_and_date(query)

    # 날씨 정보 가져오기
    temp, sky, date_time = generate_weather_info(city, target_date)

    if temp is None or sky is None:
        return "죄송합니다, 날씨 정보를 가져오는 데 실패했습니다."

    # 사용자에게 전달할 날씨 정보 생성
    weather_info = f"{city}의 {date_time} 날씨는 {sky}이며, 기온은 {temp}도입니다."
    prompt = f"사용자에게 다음 정보에 대해 친절하고 자연스럽게 설명해줘:\n\n{weather_info}"
    system_content = "날씨 정보 생성"

    # GPT를 사용하여 응답 생성
    response = call_openai_api(prompt, system_content, max_tokens=200)

    if response is None:
        return "죄송합니다, 요청을 처리하는 중 오류가 발생했습니다."

    return response


def query(query_text):
    """
    사용자의 질의에 대해 응답을 생성하는 함수.

    Args:
        query_text (str): 사용자의 질의 문장.

    Returns:
        str: 최종 응답 문자열.
    """
    return generate_weather_response(query_text)
