import requests
from loguru import logger

class Tmap_API:
    def __init__(self, API_KEY):
        self.TMAP_API_KEY = API_KEY

    def get_direction_bet_coords_Tmap(self, start, dest, startName, endName):
        try:
            """
            Parameter
                start: tuple # 시작위치의 위경도
                dest: tuple # 도착위치의 위경도
                startName: str # 시작위치의 장소 이름
                endName: str # 도착위치의 장소 이름
                TMAP_API_KEY: str # API KEY
            return
                start: str # 시작위치의 장소 이름
                dest: str # 도착위치의 장소 이름
                distance_walking: str # 도보 거리
                time: str # 도보 시간
            """
            url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"
            headers = {
                "appKey" : self.TMAP_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "startX": start[0],
                "startY": start[1],
                "endX": dest[0],
                "endY": dest[1],
                "reqCoordType": "WGS84GEO",
                "resCoordType": "WGS84GEO",
                "startName": startName,
                "endName": endName
            }
            logger.debug(f"Tmap Payload {payload}")
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            logger.debug(f"Tmap Response : {data}")
            total_distance_of_walking = data["features"][0]["properties"]["totalDistance"]
            total_time = data["features"][0]["properties"]["totalTime"]
            if response.status_code == 200:
                return {
                    "start": startName,
                    "dest": endName,
                    "distance_walking": total_distance_of_walking,
                    "time": total_time
                }
            
            else:
                raise Exception(f"경로 조회 실패 : {data.get('errorMessage', 'Unknown error')}")
        except Exception as e:
            logger.error(f"error {e}")