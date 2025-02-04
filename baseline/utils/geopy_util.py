from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from loguru import logger
# TODO: Geopy를 사용해서 장소에 따른 위 경도 구하기

def getLatLng(place):
    """
    parameter:
        place: str # 사용자가 입력폼에 입력한 시작지점 위치
    return
        (lat, lng): tuple # 입력한 위치에 따른 위,경도 값
    """
    # Nominatim 기반 좌표 탐색
    geoloc = Nominatim(user_agent="South Korea", timeout=None)
    geo = geoloc.geocode(place)
    lat = str(geo.latitude)
    lng = str(geo.longitude)
    logger.debug(f"시작지점 : {place} / 위경도 : {lat}, {lng}")
    return (lat, lng)