import json
import openai
from config import get_openai_api_key, get_weather_api_key
from chatweather.weather import forecast
from chatweather.weather_api_datetime import get_current_datetime

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


def call_openai_api(messages, max_tokens=150, temperature=0.7):
    """
    OpenAI ChatCompletion API를 호출하는 함수.

    Args:
        messages (list): 대화 메시지의 리스트.
        max_tokens (int, optional): 최대 토큰 수. 기본값은 150.
        temperature (float, optional): 생성 온도. 기본값은 0.7.

    Returns:
        str: OpenAI의 응답 내용.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
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
    current_time = get_current_datetime().strftime("%Y%m%d%H%M%S")
    system_content = "도시와 날짜 추출"

    # OpenAI API 호출
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]
    output = call_openai_api(messages)

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


def generate_weather_response(query, conversation_history):
    """
    사용자의 질의로부터 날씨 정보를 생성하는 함수.

    Args:
        query (str): 사용자의 질의 문장.
        conversation_history (list): 이전 대화 기록.

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

    # 대화 기록을 바탕으로 메시지 생성
    messages = [
        {"role": "system", "content": "당신은 사용자에게 날씨 정보를 제공하는 친절한 어시스턴트입니다."},
    ]
    # 이전 대화 기록 추가
    for entry in conversation_history:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["bot"]})
    # 현재 사용자 입력과 날씨 정보를 포함한 메시지 추가
    user_message = f"{query}\n\n현재 날씨 정보:\n{weather_info}\n\n위의 날씨 정보를 바탕으로 사용자에게 친절하고 자연스러운 답변을 제공해주세요."
    messages.append({"role": "user", "content": user_message})

    # GPT를 사용하여 응답 생성
    response = call_openai_api(messages, max_tokens=200)

    if response is None:
        return "죄송합니다, 요청을 처리하는 중 오류가 발생했습니다."

    return response


def chat_loop():
    """
    사용자가 'exit'을 입력할 때까지 반복적으로 질문을 받고 응답하는 함수.
    사용자의 질문에 '날씨'라는 단어가 들어가면 날씨 정보를 제공하며,
    그렇지 않은 경우 일반 대화로 처리하고 이전 대화를 기억합니다.
    날씨 질문에도 이전 대화를 기억하여 응답에 반영합니다.
    """
    print("챗봇을 시작합니다. 'exit'을 입력하여 종료할 수 있습니다.")
    print("날씨 정보를 얻기 위해 꼭 %%'날씨'%% 라는 단어를 포함한 질문을 입력하세요.")
    print("ex) '서울 날씨 어때?', '내일 부산 날씨 알려줘'")

    # 대화 기록을 저장할 리스트
    conversation_history = []

    while True:
        user_input = input("질문을 입력하세요: ")

        if user_input.lower() == "exit":
            print("챗봇을 종료합니다.")
            break

        # 사용자의 입력에 '날씨'가 포함되어 있는지 확인
        if '날씨' in user_input:
            # generate_weather_response 함수를 사용하여 날씨 정보 응답 생성
            response = generate_weather_response(user_input, conversation_history)
        else:
            # 대화 기록을 바탕으로 메시지 생성
            messages = [
                {"role": "system", "content": "당신은 사용자에게 날씨 정보를 제공하는 친절한 어시스턴트입니다."},
            ]
            for entry in conversation_history:
                messages.append({"role": "user", "content": entry["user"]})
                messages.append({"role": "assistant", "content": entry["bot"]})
            messages.append({"role": "user", "content": user_input})

            # 자유로운 질문에 대한 응답 생성
            response = call_openai_api(messages, max_tokens=200)

        print(f"응답: {response}")

        # 현재 대화를 기록에 추가
        conversation_history.append({"user": user_input, "bot": response})
