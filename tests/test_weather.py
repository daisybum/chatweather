import pytest
from unittest.mock import patch, Mock
import requests

from pyWeather.weather import forecast, get_current_date, get_current_hour

# 모킹을 위한 샘플 XML 응답 데이터
mock_response_success = """
<response>
  <header>
    <resultCode>0000</resultCode>
    <resultMsg>OK</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <category>T1H</category>
        <obsrValue>20</obsrValue>
      </item>
      <item>
        <category>PTY</category>
        <obsrValue>0</obsrValue>
      </item>
    </items>
  </body>
</response>
"""

mock_response_service_key_error = """
<OpenAPI_ServiceResponse>
  <cmmMsgHeader>
    <returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg>
  </cmmMsgHeader>
</OpenAPI_ServiceResponse>
"""

def test_get_current_date():
    """
    현재 날짜를 반환하는지 테스트
    """
    result = get_current_date()
    assert len(result) == 8, f"Expected 8 digits but got {result}"

def test_get_current_hour():
    """
    현재 시간을 반환하는지 테스트
    """
    result = get_current_hour()
    assert len(result) == 4, f"Expected 4 digits but got {result}"

def test_forecast_success():
    """
    API 호출이 성공적으로 기온과 날씨를 반환하는지 테스트
    """
    with patch('requests.get') as mocked_get:
        # Mock response 설정
        mocked_get.return_value = Mock(status_code=200)
        mocked_get.return_value.text = mock_response_success

        # 테스트에 필요한 파라미터 설정
        params = {
            'serviceKey': 'fake_key',
            'pageNo': '1',
            'numOfRows': '10',
            'dataType': 'XML',
            'base_date': '20220101',  # 테스트 날짜를 고정
            'base_time': '0600',      # 테스트 시간을 고정
            'nx': '55',
            'ny': '127'
        }

        result = forecast(params)
        assert result == ('20', '맑음'), f"Expected ('20', '맑음') but got {result}"

def test_forecast_service_key_error():
    """
    API 키가 등록되지 않았을 때 적절한 오류 메시지를 반환하는지 테스트
    """
    with patch('requests.get') as mocked_get:
        # Mock response 설정
        mocked_get.return_value = Mock(status_code=200)
        mocked_get.return_value.text = mock_response_service_key_error

        # 테스트에 필요한 파라미터 설정
        params = {
            'serviceKey': 'invalid_key',
            'pageNo': '1',
            'numOfRows': '10',
            'dataType': 'XML',
            'base_date': '20220101',
            'base_time': '0600',
            'nx': '55',
            'ny': '127'
        }

        result = forecast(params)
        assert result == "API 키가 등록되지 않았거나 올바르지 않습니다.", f"Expected service key error but got {result}"

def test_forecast_response_key_error():
    """
    API 응답에서 'response' 키가 없을 때 적절한 오류 메시지를 반환하는지 테스트
    """
    with patch('requests.get') as mocked_get:
        # Mock response에서 response 키를 제거한 빈 응답 설정
        mocked_get.return_value = Mock(status_code=200)
        mocked_get.return_value.text = '<no_response></no_response>'

        # 테스트에 필요한 파라미터 설정
        params = {
            'serviceKey': 'fake_key',
            'pageNo': '1',
            'numOfRows': '10',
            'dataType': 'XML',
            'base_date': '20220101',
            'base_time': '0600',
            'nx': '55',
            'ny': '127'
        }

        result = forecast(params)
        assert result == "API 응답에서 'response' 키를 찾을 수 없습니다.", f"Expected 'response' key error but got {result}"

def test_forecast_request_exception():
    """
    네트워크 문제 등으로 API 요청이 실패했을 때 적절한 오류 메시지를 반환하는지 테스트
    """
    with patch('requests.get') as mocked_get:
        # Mock network error 발생
        mocked_get.side_effect = requests.exceptions.RequestException("Network error")

        # 테스트에 필요한 파라미터 설정
        params = {
            'serviceKey': 'fake_key',
            'pageNo': '1',
            'numOfRows': '10',
            'dataType': 'XML',
            'base_date': '20220101',
            'base_time': '0600',
            'nx': '55',
            'ny': '127'
        }

        result = forecast(params)
        assert "API 요청 실패" in result, f"Expected network failure message but got {result}"
