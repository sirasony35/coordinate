import pandas as pd
# from module.utility import Vworld_Api, LandSoil_Api

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from pyproj import Transformer
import json
import xmltodict


def get_coordinates_from_address(api_key,address, crs):
    url = "https://api.vworld.kr/req/address"
    queryParams = "?" + urlencode({
        "key": api_key,  # API 키 직접 사용
        "service": "address",
        "request": "getcoord",
        # "crs": "epsg:3857",
        "crs": crs,
        "address": address,
        "format": "json",
        "type": "parcel"})

    request = Request(url + queryParams)
    response = urlopen(request)
    print(response.getcode())
    if response.getcode() == 200:
        response_body = response.read()
        text_str = response_body.decode("utf-8")
        print(text_str)
        json_data = json.loads(text_str)
        if json_data['response']['status'] == 'OK':
            x = float(json_data['response']['result']['point']['x'])
            y = float(json_data['response']['result']['point']['y'])
            # ## 좌표 변환
            # transformer = Transformer.from_crs(4326, 3857)
            # x, y = transformer.transform(_lat, _lng)
            pnu_code = json_data['response']['refined']['structure']['level4LC']
            return x, y, pnu_code
        else:
            result = '주소의 좌표값을 찾을 수가 없습니다.'
            return result, None, None
    else:
        result = '주소의 좌표값을 찾을 수가 없습니다.'

        return result, None, None

def get_land_polygon(api_key, crs, x, y, dataset="LP_PA_CBND_BUBUN"):
    geoFilter = f"POINT({x} {y})"
    url = "https://api.vworld.kr/req/data"

    # API 요청 파라미터
    queryParams = "?" + urlencode({
        "key": api_key,  # API 키 직접 사용
        "service": "data",
        "request": "GetFeature",
        "data": dataset,
        "geomFilter": geoFilter,
        "format": "json",
        "geometry": "true",
        "attribute": "true",
        # "crs": "epsg:3857",
        "crs": crs
        # "domain": "www.v-world-test.com"
    })

    request = Request(url + queryParams)
    response = urlopen(request)
    if response.getcode() == 200:
        response_body = response.read()
        text_str = response_body.decode('utf-8')
        json_data = json.loads(text_str)

        _coordinates = json_data['response']['result']['featureCollection']['features'][0]
        # coordinates = _coordinates[0]
        return _coordinates


def get_land_info(api_key, pnu_code):
    url = "https://api.vworld.kr/ned/data/getLandCharacteristics"
    queryParams = "?" + urlencode({
        "key": api_key,
        "pnu": pnu_code,
        "format": "json",
        "numOfRows": "100",
        "pageNo": "1"
        # "domain": "www.v-world-test.com"
    })

    try:
        request = Request(url + queryParams)
        response_body = urlopen(request).read()
        json_data = json.loads(response_body.decode('utf-8'))
        print(json_data)

        if 'landCharacteristicss' in json_data and 'field' in json_data['landCharacteristicss']:
            land_area = json_data['landCharacteristicss']['field'][0].get('lndpclAr', "정보 없음")
            nomination_name = json_data['landCharacteristicss']['field'][0].get('lndcgrCodeNm', "정보 없음")
            return land_area, nomination_name
    except KeyError:
        print(f"⚠️ 필지 정보 조회 실패: {pnu_code} (KeyError 발생)")
    except Exception as e:
        print(f"❌ get_land_info 오류 발생: {e}")
    return None, None  # 오류 발생 시 None 반환

def save_to_geojson(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# V-world API 키 설정
VWORLD_API_KEY = "B1F89909-EC45-3987-BE96-FA7FB918B06F"
PUBLIC_API_KEY = "1rTRcPcrgRX4bckCMPyIIgsMgxqzwZwAKsqCjJe74xrEwdc2rQRZgHAZ60aJdhT6313RnB8znsO2jJONz+ltow=="

#좌표 세팅
crs = "epsg:4326"

# CSV 파일에서 주소 읽기
input_csv = "필지주소.csv"  # CSV 파일 경로
output_file = "result/화성_테스트_필지.geojson"  # 결과 GeoJSON 파일 경로

# 주소 데이터 불러오기
addresses_df = pd.read_csv(input_csv)

# GeoJSON FeatureCollection 초기화
geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

for index, row in addresses_df.iterrows():
    address = row['address']
    owner = row['owner']  # owner 필드 추가
    crop = row['crop']
    # doublecrop = row['double-crop']
    # cultivar = row['cultivar']
    # case = row['CASE']
    print(f"Processing address: {address}")

    # 주소를 좌표로 변환
    lng, lat, pnu_code = get_coordinates_from_address(VWORLD_API_KEY, address, crs)
    print(f"pnucode: {address}", pnu_code)

    if lng and lat:
        # 좌표를 사용하여 폴리곤 데이터 가져오기
        polygon_data = get_land_polygon(VWORLD_API_KEY,crs, lng, lat)

        if polygon_data:

            # Land info 추가
            land_area, nomination_name = get_land_info(VWORLD_API_KEY, pnu_code)

            # 속성테이블
            polygon_data['properties']['owner'] = owner
            polygon_data['properties']['crop'] = crop
            # polygon_data['properties']['double_crop'] = doublecrop
            # polygon_data['properties']['cultivar'] = cultivar
            polygon_data['properties']['land_area'] = land_area
            polygon_data['properties']['nomination_name'] = nomination_name
            # polygon_data['properties']['CASE'] = case

            # Feature 추가
            geojson_data["features"].append(polygon_data)
            print(f"Added polygon for address: {address} with owner: {owner}")
        else:
            print(f"Failed to get polygon data for address: {address}")
    else:
        print(f"Failed to get coordinates for address: {address}")

# GeoJSON 파일로 저장
save_to_geojson(geojson_data, output_file)
print(f"Combined GeoJSON file saved: {output_file}")