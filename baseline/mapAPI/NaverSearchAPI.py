import requests
import os
from dotenv import load_dotenv
from loguru import logger


def get_lat_lon(query, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET):
    url = "https://openapi.naver.com/v1/search/local.json"
    params = {
        "query": query,
        "display": 1,  # 한 개의 결과만 반환
        "start": 1,
        "sort": "random"
    }
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            item = data["items"][0]  # 첫 번째 검색 결과
            title = item["title"].replace("<b>", "").replace("</b>", "")  # HTML 태그 제거
            address = item["address"]  # 주소 정보
            mapx = int(item["mapx"])  # 네이버 지도 x 좌표
            mapy = int(item["mapy"])  # 네이버 지도 y 좌표
            mapx = float(str(mapx)[0:3]+"."+str(mapx)[3:]) # longitude
            mapy = float(str(mapy)[0:2]+"."+str(mapy)[2:]) # latitude
            logger.debug(f"📍 검색된 장소: {title} ({address}, {mapy} / {mapx})")
            return (mapx, mapy)
        else:
            logger.error("❌ 검색 결과가 없습니다.")
            return None
    else:
        logger.error(f"⚠️ API 요청 실패: {response.status_code}")
        return None