from pyWeather import chatgpt

def main():
    print("날씨 질문 예시: '내일 서울 날씨 어때?', '오늘 부산 날씨는?', '모레 하와이 날씨 어때?'")
    query_text = input("날씨에 대해 질문해보세요: ")

    # chatgpt 모듈의 query 함수 호출
    response = chatgpt.query(query_text)

    # GPT-4.0-mini의 응답 출력
    print(f"\nAI 응답: {response}")

if __name__ == "__main__":
    main()
