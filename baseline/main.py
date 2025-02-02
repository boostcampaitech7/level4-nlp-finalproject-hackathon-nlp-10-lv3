import os
from dotenv import load_dotenv

# geopy util
from utils.geopy_util import getLatLng

# database
from db.database import SQLiteDatabase

# MapAPI
from mapAPI.TMapAPI import Tmap_API

# Model
from model.ChatModel import ClovaXChatModel

load_dotenv()
TMAP_API_KEY = os.getenv("TMAP_API_KEY")
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")


if __name__ == "__main__":
    """
    main.py
    - Streamlit의 UI 업데이트 담당
    - 각종 모델이나 모듈 호출
    AI Hybrid Agent는 어떨까?
    """

    chatModel = ClovaXChatModel(API_KEY=CLOVA_API_KEY)
    # naverMAP = NaverMap()
    tMAP = Tmap_API(API_KEY=TMAP_API_KEY)
    database = SQLiteDatabase()
    reviewSearchModel = search_module()
    


    # TODO: 사용자에게 정보를 입력받기 (in Streamlit)
    """
    streamlit 호출하고 첫페이지를 불러오기
    - 사용자 정보를 입력받으면 해당 정보를 MapAPI나 다른 모듈에 넘기기 위해 처리
    """


    # TODO: 사용자가 입력한 장소에 대한 위, 경도 추출 (call MAP API Module) -> first place init
    """
    1. geopy를 사용해서 입력된 장소에 대한 위,경도를 추출함 -> 사용자가 추천받고싶어하는 위치임
    2. 해당 위치를 기반으로 반경 500M의 place 제한함
    """
    
    start_place_latlng = getLatLng(start_place) # 위 경도 추출
    # sql DB에서 장소 추출 (위경도 기준 반경 500M 추출)
    candidate_places = SQLiteDatabase.find_nearby_businesses(start_place_latlng[0], start_place_latlng[1])

    # TODO: 시간과 요구사항에 맞는 "카테고리 기반 코스 추천" (call ChatModel)
    """
    ChatModel을 사용해서 카테고리 기반 코스를 추출하는 코드
    """


    # TODO: 카테고리에 맞는 후보지 추출 (call Retrieve Module)
    """
    Retreieve 모듈로 선택된 카테고리들에 대한 후보지들을 불러오기
    -> dictionary로 각 카테고리 별로 후보지들이 들어가도록 만들어주기
    """

    # TODO: 현재 선택된 장소 (좌표) 기반으로 카테고리에 맞는 후보지들 선택 -> 마지막 카테고리까지 선택
    """
    TMap API사용해서 현재 장소(위경도)와 위에서 뽑은 후보지들과의 거리, 시간 추출
    (추가) Naver MAP API를 사용해서 자동차 거리, 시간도 추출, Direction 5
    """
    categories = ["식당1","카페","산책로","식당2"] # example
    now_place = {}
    selected = []
    for category in categories:
        selected_candidate = []
        for candidate in candidate_places_from_review: # 현재 위치와 후보지들간의 거리 구하기
            result = tMAP.get_direction_bet_coords_Tmap(
                [now_place["lat"], now_place["lng"]],
                [candidate["lat"], candidate["lng"]],
                now_place["name"],
                candidate["name"],
                TMAP_API_KEY
            )
            selected_candidate.append(result)
            # ChatModel로 후보지 선택
        

    # TODO: streamlit에 표시
    """
    
    """