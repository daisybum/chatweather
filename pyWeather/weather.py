import requests
import json
from datetime import datetime
from pyWeather.weather_api_datetime import get_current_datetime, set_api_datetime


def forecast(params):
    """
    날씨 정보를 가져오는 함수.
    주어진 파라미터로 API 요청을 보내고, 날씨와 온도 정보를 반환합니다.
    """
    city = params.get('city', 'Seoul')  # 기본값은 서울
    apiKey = params.get('serviceKey')  # API 키
    lang = params.get('lang', 'kr')  # 언어 설정
    units = params.get('units', 'metric')  # 단위 설정

    # 기상 예보 API에서 사용할 날짜와 시간 설정
    target_date = params.get('target_date')
    target_date = datetime.strptime(target_date, "%Y%m%d%H%M%S")
    api_datetime = set_api_datetime(target_date)
    datetime_str = api_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # OpenWeatherMap API 호출
    today = datetime.now().date()

    # 오늘 날짜인 경우 현재 날씨 정보를 가져옴
    if today == target_date.date():
        api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={apiKey}&lang={lang}&units={units}"
        try:
            # API 요청 보내기
            result = requests.get(api)

            # HTTP 응답 코드 확인
            if result.status_code == 200:
                weather_data = json.loads(result.text)

                # 기온과 날씨 상태 반환
                temp = weather_data['main']['temp']
                sky = weather_data['weather'][0]['description']
                return temp, sky, get_current_datetime()
            elif result.status_code == 404:
                print(f"Error: The city '{city}' was not found.")
            elif result.status_code == 401:
                print(f"Error: Invalid API key.")
            else:
                print(f"Error: Received unexpected response code {result.status_code}.")

        except Exception as e:
            # 요청이 실패했을 때 처리
            print(f"Error fetching weather data: {e}")

        return None, None
    else:
        api = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&APPID={apiKey}&lang={lang}&units={units}"
        try:
            # API 요청 보내기
            result = requests.get(api)

            # HTTP 응답 코드 확인
            if result.status_code == 200:
                weather_data = json.loads(result.text)

                #
                weather_list = weather_data['list']
                for item in weather_list:
                    # API에서 가져온 시간과 가장 가까운 시간을 찾음
                    item_datetime = datetime.fromtimestamp(item['dt'])
                    if item_datetime == api_datetime:
                        temp = item['main']['temp']
                        sky = item['weather'][0]['description']
                        return temp, sky, api_datetime

            elif result.status_code == 404:
                print(f"Error: The city '{city}' was not found.")
            elif result.status_code == 401:
                print(f"Error: Invalid API key.")
            else:
                print(f"Error: Received unexpected response code {result.status_code}.")

        except Exception as e:
            # 요청이 실패했을 때 처리
            print(f"Error fetching weather data: {e}")
