import requests


def debug_api_with_headers():
    API_KEY = "1rTRcPcrgRX4bckCMPyIIgsMgxqzwZwAKsqCjJe74xrEwdc2rQRZgHAZ60aJdhT6313RnB8znsO2jJONz+ltow=="
    TARGET_STDG = "4180025322"  # 은대리

    url_list = 'http://apis.data.go.kr/1390802/SoilEnviron/SoilExam/V2/getSoilExamList'
    params_list = {'serviceKey': API_KEY, 'STDG_CD': TARGET_STDG, 'Page_Size': 10, 'Page_No': 1}

    # 웹 브라우저(크롬)에서 보내는 것처럼 위장
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
    }

    print("\n=== [테스트 3] 헤더 위장 목록 조회 ===")
    try:
        res3 = requests.get(url_list, params=params_list, headers=headers)
        print(f"상태 코드: {res3.status_code}")
        print(res3.text[:500])
    except Exception as e:
        print(f"오류 발생: {e}")
    print("-" * 50)


if __name__ == "__main__":
    debug_api_with_headers()