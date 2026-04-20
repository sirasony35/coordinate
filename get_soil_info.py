import requests
import xml.etree.ElementTree as ET


def test_soil_api():
    # ==========================================
    # 1. 테스트 설정 (API 키 및 주소 코드)
    # ==========================================
    API_KEY = "1rTRcPcrgRX4bckCMPyIIgsMgxqzwZwAKsqCjJe74xrEwdc2rQRZgHAZ60aJdhT6313RnB8znsO2jJONz+ltow=="

    # 테스트할 연천군 전곡읍 은대리 1169번지의 예시
    TEST_PNU_CD = "4180025322111690000"  # 19자리 지번코드 (특정 1개 필지 테스트용)
    TEST_STDG_CD = "4180025322"  # 10자리 법정동코드 (동네 전체 목록 테스트용)

    # 서버 차단(403 Forbidden 등) 방지용 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print("=== 🧪 흙토람 API 통신 테스트 시작 ===\n")

    # ==========================================
    # [테스트 1] 19자리 PNU 코드로 정확한 지번 조회
    # ==========================================
    print(f"▶ [테스트 1] 정확한 지번 조회 (PNU: {TEST_PNU_CD})")
    url_pnu = 'http://apis.data.go.kr/1390802/SoilEnviron/SoilExam/V2/getSoilExam'
    params_pnu = {'serviceKey': API_KEY, 'PNU_CD': TEST_PNU_CD}

    try:
        res1 = requests.get(url_pnu, params=params_pnu, headers=headers)
        print(f" - HTTP 상태 코드: {res1.status_code}")

        if res1.status_code == 200:
            root1 = ET.fromstring(res1.content)
            result_code1 = root1.findtext('.//Result_Code')
            result_msg1 = root1.findtext('.//Result_Msg')
            print(f" - API 응답 메시지: {result_code1} ({result_msg1})")

            if result_code1 == '200':
                item = root1.find('.//item')
                if item is not None:
                    print("   ✅ 데이터 수신 성공!")
                    print(f"      * 주소: {item.findtext('Pnu_Nm')}")
                    print(f"      * 검정연도: {item.findtext('Any_Year')}년")
                    print(f"      * 유기물(OM): {item.findtext('OM')} g/kg")
                else:
                    print("   ⚠️ 응답은 정상이지만, 해당 PNU에 대한 데이터가 없습니다.")
        else:
            print(f"   🚨 서버 에러 내용: {res1.text[:100]}")
    except Exception as e:
        print(f"   🚨 통신 에러 발생: {e}")

    print("\n" + "=" * 50 + "\n")

    # ==========================================
    # [테스트 2] 10자리 법정동코드로 동네 목록 조회
    # ==========================================
    print(f"▶ [테스트 2] 동네 목록 조회 (법정동코드: {TEST_STDG_CD})")
    url_list = 'http://apis.data.go.kr/1390802/SoilEnviron/SoilExam/V2/getSoilExamList'

    # Page_Size를 3으로 설정하여 최근 3건만 잘 가져오는지 확인
    params_list = {'serviceKey': API_KEY, 'STDG_CD': TEST_STDG_CD, 'Page_Size': 3, 'Page_No': 1}

    try:
        res2 = requests.get(url_list, params=params_list, headers=headers)
        print(f" - HTTP 상태 코드: {res2.status_code}")

        if res2.status_code == 200:
            root2 = ET.fromstring(res2.content)
            result_code2 = root2.findtext('.//Result_Code')
            result_msg2 = root2.findtext('.//Result_Msg')
            print(f" - API 응답 메시지: {result_code2} ({result_msg2})")

            if result_code2 == '200':
                items = root2.findall('.//item')
                if items:
                    print(f"   ✅ 데이터 수신 성공! (총 {len(items)}건 표출)")
                    for idx, item in enumerate(items, 1):
                        print(f"      [{idx}] 주소: {item.findtext('PNU_Nm')} | 검정일: {item.findtext('Exam_Day')}")
                else:
                    print("   ⚠️ 응답은 정상이지만, 해당 동네에 등록된 데이터가 없습니다.")
        else:
            print(f"   🚨 서버 에러 내용: {res2.text[:100]}")
    except Exception as e:
        print(f"   🚨 통신 에러 발생: {e}")


if __name__ == "__main__":
    test_soil_api()