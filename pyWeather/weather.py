import requests
from datetime import datetime, timedelta
import xmltodict

def get_current_date():
    current_date = datetime.now().date()
    return current_date.strftime("%Y%m%d")

def get_current_hour():
    now = datetime.now()
    # 기상청 초단기예보는 10분 단위로 제공되므로 45분 전의 데이터를 요청합니다.
    if now.minute < 45:
        now -= timedelta(hours=1)
    return now.strftime("%H00")  # 'hh00' 형식으로 반환

int_to_weather = {
    "0": "맑음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "5": "빗방울",
    "6": "빗방울눈날림",
    "7": "눈날림"
}


def forecast(params):
    """
    초단기예보 API를 호출하여 현재 기온과 날씨 상태를 반환합니다.
    """
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    try:
        # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
        res = requests.get(url, params)
        res.raise_for_status()  # API 호출 에러 처리

        # XML -> 딕셔너리로 변환
        xml_data = res.text
        dict_data = xmltodict.parse(xml_data)

        # API 키가 등록되지 않은 경우 확인
        if 'cmmMsgHeader' in dict_data.get('OpenAPI_ServiceResponse', {}):
            error_msg = dict_data['OpenAPI_ServiceResponse']['cmmMsgHeader'].get('returnAuthMsg', '')
            if error_msg == 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR':
                return "API 키가 등록되지 않았거나 올바르지 않습니다."

        # 응답 데이터에서 필요한 키가 존재하는지 확인
        if 'response' not in dict_data:
            return "API 응답에서 'response' 키를 찾을 수 없습니다."

        if 'body' not in dict_data['response']:
            return "API 응답에서 'body' 키를 찾을 수 없습니다."

        if 'items' not in dict_data['response']['body']:
            return "API 응답에서 'items' 키를 찾을 수 없습니다."

        # 데이터가 존재하는지 확인
        if 'item' not in dict_data['response']['body']['items']:
            return "API 응답에서 'item' 데이터를 찾을 수 없습니다."

        temp, sky = None, None
        # 필요한 데이터 추출
        for item in dict_data['response']['body']['items']['item']:
            if item['category'] == 'T1H':
                temp = item['obsrValue']
            if item['category'] == 'PTY':
                sky = int_to_weather.get(item['obsrValue'], "알 수 없음")

        if temp and sky:
            return temp, sky
        else:
            return "필요한 정보를 가져오지 못했습니다."

    except requests.exceptions.RequestException as e:
        return f"API 요청 실패: {e}"

    except KeyError as e:
        return f"예상치 못한 응답 구조입니다. 누락된 키: {e}"

    except Exception as e:
        return f"알 수 없는 오류 발생: {e}"

# API 키
keys = '...'

# 좌표 (서울의 경우)
params = {
    'serviceKey': keys,
    'pageNo': '1',
    'numOfRows': '10',
    'dataType': 'XML',
    'base_date': get_current_date(),
    'base_time': get_current_hour(),
    'nx': '55',  # 예: 서울
    'ny': '127'
}

print(forecast(params))