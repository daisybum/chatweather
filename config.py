import yaml
import os

# 현재 파일(config.py)의 디렉토리 경로를 기준으로 절대 경로를 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.yaml')

def load_config():
    """YAML 파일을 읽어 설정 값을 반환하는 함수"""
    with open(CONFIG_FILE_PATH, 'r') as file:
        config = yaml.safe_load(file)
    return config

# YAML 파일에서 API 키 불러오기
config = load_config()

def get_openai_api_key():
    """OpenAI API 키를 반환하는 함수"""
    return config['openai_api_key']

def get_weather_api_key():
    """Weather API 키를 반환하는 함수"""
    return config['weather_api_key']
