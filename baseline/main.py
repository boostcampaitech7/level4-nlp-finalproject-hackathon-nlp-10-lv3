import os
import pandas as pd
from dotenv import load_dotenv

from model.Retrieve import Retrieval
from utils.category import Category


if __name__ = "__main__":
    """
    main.py
    - Streamlit의 UI 업데이트 담당
    - 각종 모델이나 모듈 호출
    """

    chatModel = ClovaXChatModel()
    naverMAP = NaverMap()
    tMAP = T_Map()
    reviewSearchModel = search_module()


    # TODO: 사용자에게 정보를 입력받기 (in Streamlit)
    """
    streamlit 호출하고 첫페이지를 불러오기
    - 사용자 정보를 입력받으면 해당 정보를 MapAPI나 다른 모듈에 넘기기 위해 처리
    """


    # TODO: 사용자가 입력한 장소에 대한 위, 경도 추출 (call MAP API Module) -> first place init
    """
    geopy를 사용해서 입력된 장소에 대한 위,경도를 추출함 -> 사용자가 추천받고싶어하는 위치임
    - Naver Map API는 왜 안되는가? : 사용자는 Naive하게 입력하는 경우가 많음, 따라서 그거에 맞춰서
    """
    

    # TODO: 시간과 요구사항에 맞는 "카테고리 기반 코스 추천" (call ChatModel)
    """
    ChatModel을 사용해서 카테고리 기반 코스를 추출하는 코드
    """    
    input_dict = {
        'request' : "",
        'age' : '',
        'sex' : '',
        'start_time' : ''
    } # 이거는 윗단에서 어떻게 처리할지 몰라 딕셔너리 형태로 설정
    category_generator = Category(chatModel, "place_info_data_path")
    big_category = category_generator.get_big_category(input_dict) # List[str]
    choosed_category = category_generator.get_small_category(big_category, input_dict) # List[Tuple[str, List[str]]]


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
    

    # TODO: streamlit에 표시
    """
    
    """

    ## Inputs and Paramters (Requirements)
    query = ""
    w = 0.5
    k = 30


    ## Retrieval
    ### Requirements
    category_course = ["A", "B", "C", "D"]
    lat = 113.513515
    log = 68.5645648

    ### Load retrieval module
    retrieval = Retrieval(query, w, k)

    ### Search
    retrieved_outputs = {}
    for category in category_course:
        outputs = retrieval.search(category, lat, log)
        retrieved_outputs[category] = outputs