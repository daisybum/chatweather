# config.py
from dotenv import load_dotenv
import os

# 기본적으로 프로젝트 루트에서 .env 파일을 찾습니다
load_dotenv()

def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

def get_weather_api_key():
    return os.getenv("WEATHER_API_KEY")
