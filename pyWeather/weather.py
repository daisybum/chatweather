import requests
from datetime import datetime
from pyWeather.weather_api_datetime import get_current_datetime, set_api_datetime

def forecast(params):
    """
    주어진 파라미터를 기반으로 날씨 정보를 가져옵니다.

    Args:
        params (dict): 다음 키를 포함하는 딕셔너리:
            - 'city' (str): 도시 이름 (기본값 'Seoul').
            - 'serviceKey' (str): OpenWeatherMap의 API 키.
            - 'lang' (str): 언어 코드 (기본값 'kr').
            - 'units' (str): 측정 단위 (기본값 'metric').
            - 'target_date' (str): 'YYYYMMDDHHMMSS' 형식의 대상 날짜.

    Returns:
        tuple: (기온, 하늘 상태, 날짜시간) 또는 에러 발생 시 (None, None, None).
    """
    # 기본값과 함께 파라미터 추출
    city = params.get('city', 'Seoul')
    api_key = params.get('serviceKey')
    lang = params.get('lang', 'kr')
    units = params.get('units', 'metric')
    target_date_str = params.get('target_date')

    # 필수 파라미터 검증
    if not api_key:
        print("Error: API 키 ('serviceKey')가 필요합니다.")
        return None, None, None

    if not target_date_str:
        print("Error: 'target_date' 파라미터가 필요합니다.")
        return None, None, None

    # 대상 날짜 파싱
    try:
        target_date = datetime.strptime(target_date_str, "%Y%m%d%H%M%S")
    except ValueError as ve:
        print(f"Error: 'target_date' 파싱 중 오류 발생: {ve}")
        return None, None, None

    api_datetime = set_api_datetime(target_date)
    today = datetime.now().date()

    try:
        if today == target_date.date():
            # 현재 날씨 데이터 가져오기
            return fetch_current_weather(city, api_key, lang, units)
        else:
            # 예보 데이터 가져오기
            return fetch_forecast_weather(city, api_key, lang, units, api_datetime)
    except Exception as err:
        print(f"예기치 못한 오류 발생: {err}")
        return None, None, None

def fetch_current_weather(city, api_key, lang, units):
    """지정된 도시의 현재 날씨 데이터를 가져옵니다."""
    api_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&APPID={api_key}&lang={lang}&units={units}"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()
        temp = weather_data['main']['temp']
        sky = weather_data['weather'][0]['description']
        return temp, sky, get_current_datetime()
    except requests.exceptions.HTTPError:
        handle_http_error(response, city)
    except Exception as err:
        print(f"현재 날씨 데이터를 가져오는 중 오류 발생: {err}")
    return None, None, None

def fetch_forecast_weather(city, api_key, lang, units, api_datetime):
    """지정된 도시와 날짜시간의 예보 데이터를 가져옵니다."""
    api_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&APPID={api_key}&lang={lang}&units={units}"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()
        weather_list = weather_data['list']

        # api_datetime과 일치하는 예보 찾기
        for item in weather_list:
            item_datetime = datetime.fromtimestamp(item['dt'])
            if item_datetime == api_datetime:
                temp = item['main']['temp']
                sky = item['weather'][0]['description']
                return temp, sky, api_datetime

        print("지정된 날짜와 시간에 대한 예보를 찾을 수 없습니다.")
    except requests.exceptions.HTTPError:
        handle_http_error(response, city)
    except Exception as err:
        print(f"예보 데이터를 가져오는 중 오류 발생: {err}")
    return None, None, None

def handle_http_error(response, city):
    """HTTP 오류를 처리합니다."""
    if response.status_code == 404:
        print(f"Error: 도시 '{city}'를 찾을 수 없습니다.")
    elif response.status_code == 401:
        print("Error: 잘못된 API 키입니다.")
    else:
        print(f"HTTP 오류 발생: {response.status_code} {response.reason}")
