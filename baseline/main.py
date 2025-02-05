import os
import pandas as pd
from dotenv import load_dotenv
# UI
import streamlit as st
from streamlit_folium import st_folium
import folium
from typing import Dict, List, Optional
import copy
from datetime import datetime

# geopy util
from utils.geopy_util import getLatLng
from model.Retrieve import Retrieval
from utils.category import Category

# database
from db.database import SQLiteDatabase

# MapAPI
from mapAPI.TMapAPI import Tmap_API

# Model
from model.ChatModel import ClovaXChatModel
from model.Retrieve import Retrieval
from utils.category import Category
from utils.recommend import Recommend

load_dotenv()
TMAP_API_KEY = os.getenv("TMAP_API_KEY")
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
selected = []
candidates_per_category = {}
def get_candidate_place(candidate_places, id):
    for place in candidate_places:
        if place["id"] == int(id):
            return {
                "id": place["id"],
                "address": place["address"],
                "lat": place["latitude"],
                "lng": place["longitude"],
                "rating": place["rating"]
            }

def initialize_session_state() -> None:
    """세션 스테이트 초기화 함수"""
    if "step" not in st.session_state:
        st.session_state.step = "init"
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "current_course" not in st.session_state:
        st.session_state.current_course = None
    if "alternative_locations" not in st.session_state:
        st.session_state.alternative_locations = {}

def show_init() -> None:
    st.title("AI 코스 추천 시스템")

    # 텍스트 입력
    st.text_input(
        label="검색어를 입력하세요",
        key="search_input",
        on_change=on_search_submit,
        placeholder="ex) 레트로한 스타일의 코스를 추천해줘",
        help="Enter 키를 누르면 다음 단계로 넘어갑니다"
    )

    # 예제 쿼리 표시
    with st.expander("추천 검색어 예시", expanded=True):
        example_queries = [
            "데이트 코스 추천해줘",
            "레트로한 스타일의 코스를 추천해줘"
        ]
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.search_input = query
                on_search_submit()

def on_search_submit() -> None:
    """검색어 제출 처리"""
    if not st.session_state.search_input.strip():
        st.warning("검색어를 입력해주세요.")
        return

    st.session_state.user_query = st.session_state.search_input
    st.session_state.search_history.append(st.session_state.search_input)
    st.session_state.step = "details"
    st.rerun()


def searching_engine(input_dict, place) -> None :
    # TODO: 사용자가 입력한 장소에 대한 위, 경도 추출 (call MAP API Module) -> first place init
    """
    1. geopy를 사용해서 입력된 장소에 대한 위,경도를 추출함 -> 사용자가 추천받고싶어하는 위치임
    2. 해당 위치를 기반으로 반경 500M의 place 제한함
    """
    
    start_place_latlng = getLatLng(place) # 위 경도 추출
    # sql DB에서 장소 추출 (위경도 기준 반경 500M 추출)
    candidate_places = database.find_nearby_businesses(start_place_latlng[0], start_place_latlng[1])
    place_ids = [cand["id"] for cand in candidate_places]
    
    
    # TODO: 시간과 요구사항에 맞는 "카테고리 기반 코스 추천" (call ChatModel)
    """
    ChatModel을 사용해서 카테고리 기반 코스를 추출하는 코드
    """
    category_generator = Category(chatModel, "place_info_data_path")
    big_category = category_generator.get_big_category(input_dict) # List[str]
    choosed_category = category_generator.get_small_category(big_category, input_dict) # List[Tuple[str, List[str]]]

    #[(big category), (small category)]
    #[("대분류1", ["소분류1"]), ("대분류2", ["소분류2"])]
    
    # TODO: 카테고리에 맞는 후보지 추출 (call Retrieve Module)
    """
    Retreieve 모듈로 선택된 카테고리들에 대한 후보지들을 불러오기
    -> dictionary로 각 카테고리 별로 후보지들이 들어가도록 만들어주기
    """
    ## Inputs and Paramters (Requirements)
    query = ""
    w = 0.5
    k = 30

    ## Retrieval
    ### Load retrieval module
    retrieval = Retrieval(query, w, k)

    ### Search
    retrieved_outputs = {}
    for category in choosed_category:
        outputs = retrieval.search(category[0], place_ids) ## candidate_place의 output에서 id만 뽑아서 place_ids로 활용
        retrieved_outputs[category[0]] = outputs
    

    # TODO: 현재 선택된 장소 (좌표) 기반으로 카테고리에 맞는 후보지들 선택 -> 마지막 카테고리까지 선택
    """
    TMap API사용해서 현재 장소(위경도)와 위에서 뽑은 후보지들과의 거리, 시간 추출
    (추가) Naver MAP API를 사용해서 자동차 거리, 시간도 추출, Direction 5
    """
    now_place = {"name": place, "lat": start_place_latlng[0], "lng": start_place_latlng[1],} # init
    global selected, candidates_per_category
    selected = []
    candidates_per_category = {}
    for category in choosed_category:
        selected_candidate = []
        for candidate in retrieved_outputs[category[0]]: # 현재 위치와 후보지들간의 거리 구하기
            """ candidate Data list
            { ## rank-1
                "id": id of place,
                "name": name of place,
                "score": search score,
                "text": review text
            }
            """
            candidate_place_info = get_candidate_place(candidate_places, candidate["id"]) # 후보지 장소 정보
            result = tMAP.get_direction_bet_coords_Tmap(
                [now_place["lat"], now_place["lng"]],
                [candidate_place_info["lat"], candidate_place_info["lng"]],
                now_place["name"],
                candidate["name"],
            ) # 각 후보지 당 distance_walking, time
            sel_info = { # 프롬프트에 줄 정보
                "id": candidate["id"],
                "name": candidate["name"],
                "address": candidate_place_info["address"],
                "description": candidate["text"],
                "distance": result["distance_walking"],
                "time": result["time"],
                "rating": candidate_place_info["rating"],
                "lat": candidate_place_info["lat"],
                "lon": candidate_place_info["lng"]
            }
            selected_candidate.append(sel_info) # 선택된 후보지들과의 거리와 시간 계산한 값들
        candidates_per_category[category[0]] = selected_candidate # 후보지 목록들 추가 (for view)
        # chatX Model을 사용해서 장소 추천
        rec = Recommend(chatModel)
        recommend_query = rec.generate_prompt(now_place["name"], query, selected_candidate)
        response_rec = rec.invoke(recommend_query)
    
        # Parsing Response
        parsing_output = rec.parse_output(response_rec.content)
        recommend_id = parsing_output["id"]
        recommend_place_info = get_candidate_place(candidate_places, recommend_id)

        for candidate in retrieved_outputs[category]:
            if candidate["id"] == int(recommend_id):
                recommend_review = candidate["description"]
                break
        
        # streamlit에 표시할 선택지 저장
        select_place = {
                    "name":parsing_output["recommend_place"],
                    "address":recommend_place_info["address"],
                    "rating":recommend_place_info["rating"],
                    "type": category,
                    "description": recommend_review,
                    "lat" : recommend_place_info["lat"],
                    "lon" : recommend_place_info["lng"]
                    }
        selected.append(select_place)

        # now_place 업데이트
        now_place = {"name":parsing_output["recommend_place"],
                    "lat": recommend_place_info["lat"],
                    "lng": recommend_place_info["lng"]}

        '''
        정보를 가공하여 리턴 해서 추천 페이지에 넘겨 주기 구현 필요
        '''




def show_details() -> None:
    """상세 정보 입력 화면"""
    st.title("상세 정보 입력")
    
    # 이전 입력 쿼리 표시
    st.info(f"입력하신 검색어: {st.session_state.user_query}")
    # 입력 폼 생성
    with st.form(key="details_form"):
        # 연령대 선택
        age = st.number_input(
            label = "연령대",
            min_value = 10,
            max_value = 100,
            value = 20,
            step = 1
        )
        
        # 성별 선택
        gender = st.radio(
            "성별",
            options=["남성", "여성", "기타"],
            horizontal=True
        )
        
        # 장소 선택
        place_sel = st.text_area(
            "어디를 가고 싶으신가요?",
            help="구체적인 지명을 자유롭게 입력해주세요", 
            placeholder="예: 경복궁, 홍대"
            )
        
        # 이용시작 시간
        current_datetime = datetime.now()       
        selected_date = st.date_input("코스를 이용할 날짜를 선택해주세요", value=current_datetime.date())
        selected_time = st.time_input("예상 시작 시각을 선택해주세요", value=current_datetime.time())
        selected_datetime = datetime.combine(selected_date, selected_time).strftime('%Y-%m-%d %H:%M')


        submit_button = st.form_submit_button("AI 코스 추천 받기")
        
        if submit_button:
            # 입력값 저장 (UI용 저장 데이터)
            st.session_state.update({
                "age": age,
                "gender": gender,
                "place": place_sel,
                "start_day_and_time": selected_datetime
            })
            # 입력값 저장 (검색용 저장 데이터)
            input_dict = {
                'request' : st.session_state.user_query,
                'age' : age,
                'sex' : gender,
                'start_time' : selected_datetime   
            }
            place = place_sel
            searching_engine(input_dict, place)
            st.session_state.step = "result"
            st.rerun()


def get_alternative_locations(location_type: str) -> List[Dict]:
    """장소 타입별 대체 장소 목록 반환"""
    global candidates_per_category
    alternatives = copy.deepcopy(candidates_per_category)
    for key, places in alternatives.items():
        for place in places:
            place["type"] = key

    return alternatives.get(location_type, [])

def create_course_map(locations: list) -> folium.Map:
    """코스 위치들을 표시하는 지도 생성"""
    center_lat = sum(loc['lat'] for loc in locations) / len(locations)
    center_lon = sum(loc['lon'] for loc in locations) / len(locations)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
    
    # 위치 마커 추가
    for idx, loc in enumerate(locations, 1):
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=loc['name'],
            icon=folium.Icon(color='red', icon='info-sign'),
            tooltip=f"{idx}. {loc['name']}"
        ).add_to(m)
        
    # 경로 선 추가
    points = [[loc['lat'], loc['lon']] for loc in locations]
    folium.PolyLine(points, weight=2, color='blue', opacity=0.8).add_to(m)
        
    return m

def show_result() -> None:
    """결과 화면 표시"""
    st.title("AI 추천 코스")

    # 초기 코스 데이터 설정 및 원본 코스 저장
    if st.session_state.current_course is None:
        global selected, candidates_per_category
        ui_course = {
            "locations": copy.deepcopy(selected),

        }
        st.session_state.current_course = ui_course
        # 원본 코스 저장
        st.session_state.original_course = copy.deepcopy(ui_course)

    # 입력 정보 요약
    with st.expander("입력하신 정보", expanded=False):
        st.write("**검색 조건**")
        st.write(f"- 검색어: {st.session_state.user_query}")
        st.write(f"- 연령대: {st.session_state.age}")
        st.write(f"- 성별: {st.session_state.gender}")
        st.write(f"- 장소: {st.session_state.place}")
        st.write(f"- 예상시작시간 : {st.session_state.start_day_and_time}")

    # 좌우 컬럼 생성
    left_col, right_col = st.columns([5, 5])

    # 왼쪽 컬럼: 코스 정보
    with left_col:
        st.subheader("추천 코스 상세")
        course = st.session_state.current_course



        # 각 장소별 상세 정보
        for i, loc in enumerate(course['locations'], 1):
            with st.expander(f"{i}. {loc['name']}", expanded=True):
                st.write(f"🏠 {loc['address']}")
                st.write(f"📍 {loc['description']}")
                # 대체 장소 보기 상태 관리
                location_key = f"show_alternatives_{i}"
                if location_key not in st.session_state:
                    st.session_state[location_key] = False
                
                # 대체 장소 선택 버튼
                if st.button(
                    "다른 장소 보기" if not st.session_state[location_key] else "추천 장소 숨기기", 
                    key=f"change_{i}"
                ):
                    st.session_state[location_key] = not st.session_state[location_key]

                # 대체 장소 목록 표시
                if st.session_state[location_key]:
                    st.write("---")
                    st.write("**다른 추천 장소들:**")
                    
                    # 모든 가능한 장소 목록 생성
                    all_locations = get_alternative_locations(loc['type'])
                    
                    # 원본 코스의 해당 위치 장소 추가
                    original_loc = st.session_state.original_course['locations'][i-1]
                    if not any(alt['name'] == original_loc['name'] for alt in all_locations):
                        all_locations.append(original_loc)
                    
                    # 현재 선택된 장소를 제외한 모든 장소 표시
                    alternatives = [alt for alt in all_locations if alt['name'] != loc['name']]
                    
                    # 각 대체 장소별 상세 정보 표시
                    for alt in alternatives:
                        with st.container():
                            st.markdown(f"#### → {alt['name']}")
                            col1, col2 = st.columns([7, 3])
                            
                            with col1:
                                st.markdown("**추천 이유**")
                                st.write(f"🏠 {alt['address']}")
                                st.write(f"📍 {alt['description']}")
                                st.write(f"⭐ 평점 : {alt['rating']}")
                                
                            with col2:
                                if st.button(
                                    "이 장소로 변경", 
                                    key=f"select_{alt['name']}_{i}",
                                ):
                                    new_course = copy.deepcopy(st.session_state.current_course)
                                    new_course['locations'][i-1] = alt
                                    # 현재 위치의 대체 장소 목록 접기
                                    st.session_state[location_key] = False
                                    st.session_state.current_course = new_course
                                    st.rerun()
                            st.write("---")

    # 오른쪽 컬럼: 지도
    with right_col:
        st.subheader("코스 지도")
        course_map = create_course_map(course['locations'])
        st_folium(course_map, width=None, height=600)

    # 네비게이션 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 검색하기"):
            st.session_state.current_course = None
            st.session_state.step = "init"
            st.rerun()
    with col2:
        if st.button("상세 정보 수정"):
            st.session_state.current_course = None
            st.session_state.step = "details"
            st.rerun()

if __name__ == "__main__":
    """
    main.py
    - Streamlit의 UI 업데이트 담당
    - 각종 모델이나 모듈 호출
    AI Hybrid Agent는 어떨까?
    """
    # naverMAP = NaverMap()
    chatModel = ClovaXChatModel(API_KEY=CLOVA_API_KEY)
    tMAP = Tmap_API(API_KEY=TMAP_API_KEY)
    database = SQLiteDatabase("./db/place_Information.db")

    #Streamlit basic setting
    st.set_page_config(
    page_title="AI 코스 추천 시스템",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
    )
    
    initialize_session_state()
    
    # TODO: 사용자에게 정보를 입력받기 (in Streamlit)
    """
    streamlit 호출하고 첫페이지를 불러오기
    - 사용자 정보를 입력받으면 해당 정보를 MapAPI나 다른 모듈에 넘기기 위해 처리

    """
    
    # 현재 단계에 따른 화면 표시
    current_step = st.session_state.step
    if current_step == "init":
        show_init()
    elif current_step == "details":
        show_details()
    elif current_step == "result":
        show_result()
    

   
