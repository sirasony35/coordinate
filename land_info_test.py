import requests
import json
from urllib.parse import urlencode


def get_land_info(api_key, pnu_code):
    """
    VWorld API를 이용하여 필지 면적과 용도지구명을 조회합니다.

    Parameters:
        api_key (str): VWorld API 키
        pnu_code (str): 필지의 고유 PNU 코드

    Returns:
        tuple: (면적, 용도지구명) 또는 (None, None)
    """
    url = "https://api.vworld.kr/ned/data/getLandCharacteristics"
    params = {
        "key": api_key,
        "pnu": pnu_code,
        "format": "json",
        "numOfRows": 1,
        "pageNo": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        json_data = response.json()

        # 디버깅용 전체 응답 출력
        print(json.dumps(json_data, indent=2, ensure_ascii=False))

        field_data = json_data.get('landCharacteristicss', {}).get('field', [])

        if field_data:
            land_area = field_data[0].get('lndpclAr', "정보 없음")  # 필지 면적 (㎡)
            land_zone_name = field_data[0].get('lndcgrCodeNm', "정보 없음")  # 용도지역 이름
            return land_area, land_zone_name

        else:
            print("❗ 응답에는 데이터가 없습니다.")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
    except KeyError:
        print("❌ 응답 구조에 예상된 키가 없습니다.")
    except Exception as e:
        print(f"❌ 알 수 없는 오류: {e}")

    return None, None


# ▶ 예제 실행
if __name__ == "__main__":
    API_KEY = "B1F89909-EC45-3987-BE96-FA7FB918B06F"  # ← 실제 승인 받은 키로 대체
    PNU_CODE = "4725025032106360000"

    area, zone = get_land_info(API_KEY, PNU_CODE)
    print(f"면적: {area}㎡")
    print(f"용도지구명: {zone}")

