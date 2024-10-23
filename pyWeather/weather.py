import aiohttp
import asyncio
from config import get_weather_api_key
from datetime import datetime


async def fetch_weather(session, city, api_key, lang, units, date):
    today = datetime.now().date()
    if date == today:
        # 현재 날씨 데이터
        api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang={lang}&units={units}"
    else:
        # 날씨 예보 데이터
        api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&lang={lang}&units={units}"

    async with session.get(api_url) as response:
        return await response.json()


async def forecast(city, date):
    """
    주어진 도시와 날짜에 대한 기온과 날씨 상태를 반환하는 함수입니다.

    Args:
        city (str): 도시 이름
        date (datetime.date): 날짜

    Returns:
        tuple: (temp, sky) 기온과 날씨 상태를 반환합니다.
    """
    api_key = get_weather_api_key()
    lang = 'kr'
    units = 'metric'

    async with aiohttp.ClientSession() as session:
        result = await fetch_weather(session, city, api_key, lang, units, date)

    if 'weather' in result:
        # 현재 날씨 데이터 처리
        sky = result['weather'][0]['description']
        temp = result['main']['temp']
    elif 'list' in result:
        # 날씨 예보 데이터 처리
        forecast_list = result['list']
        forecast_data = None
        for forecast_item in forecast_list:
            forecast_time = datetime.fromtimestamp(forecast_item['dt'])
            if forecast_time.date() == date:
                forecast_data = forecast_item
                break
        if forecast_data:
            sky = forecast_data['weather'][0]['description']
            temp = forecast_data['main']['temp']
        else:
            # 해당 날짜의 데이터가 없는 경우
            return None, None
    else:
        # 데이터 가져오기 실패한 경우
        return None, None

    return temp, sky
