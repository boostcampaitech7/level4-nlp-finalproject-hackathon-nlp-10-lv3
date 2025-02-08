import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
# UI
import streamlit as st
from streamlit_folium import st_folium
import folium
from typing import Dict, List, Optional
import copy
from datetime import datetime
from datetime import time

# geopy util
from model.Retrieve import Retrieval
from utils.category import Category

# database
from db.database import SQLiteDatabase

# MapAPI
from mapAPI.TMapAPI import Tmap_API
from mapAPI.NaverSearchAPI import get_lat_lon
# Model
from model.ChatModel import ClovaXChatModel
from model.Retrieve import Retrieval
from utils.category import Category
from utils.recommend import Recommend

load_dotenv()
TMAP_API_KEY = os.getenv("TMAP_API_KEY")
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
NAVER_SEARCH_API_ID = os.getenv("NAVER_SEARCH_API_ID")
NAVER_SEARCH_API_KEY = os.getenv("NAVER_SEARCH_API_KEY")

selected = []
candidates_per_category = {}

#Streamlit basic setting
st.set_page_config(
page_title="AI 코스 추천 시스템",
page_icon="🎯",
layout="wide",
initial_sidebar_state="collapsed"
)

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
    if "saved_courses" not in st.session_state:
        st.session_state.saved_courses = []
def show_init() -> None:
    """초기화면 표시"""
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
                st.session_state.temp_query = query
                on_search_submit()

def on_search_submit() -> None:
    """검색어 제출 처리"""
    
    if hasattr(st.session_state, 'temp_query') and st.session_state.temp_query.strip() : 
        st.session_state.user_query = st.session_state.temp_query
        st.session_state.search_history.append(st.session_state.temp_query)
    elif hasattr(st.session_state, 'search_input') :
        st.session_state.user_query = st.session_state.search_input
        st.session_state.search_history.append(st.session_state.search_input)
    else:
        st.warning("검색어를 입력해주세요.")
        return
    st.session_state.step = "details"
    st.rerun()


def searching_engine(input_dict, place) -> None :
    # TODO: 사용자가 입력한 장소에 대한 위, 경도 추출 (call MAP API Module) -> first place init
    # """
    # 1. geopy를 사용해서 입력된 장소에 대한 위,경도를 추출함 -> 사용자가 추천받고싶어하는 위치임
    # 2. 해당 위치를 기반으로 반경 500M의 place 제한함
    # """
    start_place_latlng = get_lat_lon(place, NAVER_SEARCH_API_ID, NAVER_SEARCH_API_KEY) # 위 경도 추출
    # sql DB에서 장소 추출 (위경도 기준 반경 500M 추출)
    candidate_places = database.find_nearby_businesses(start_place_latlng[1], start_place_latlng[0])
    place_ids = [cand["id"] for cand in candidate_places]
    # TODO: 시간과 요구사항에 맞는 "카테고리 기반 코스 추천" (call ChatModel)
    # """
    # ChatModel을 사용해서 카테고리 기반 코스를 추출하는 코드
    # """
    choosed_category = category_generator.get_all_category(input_dict) # List[Tuple[str, List[str]]]
    
    # TODO: 카테고리에 맞는 후보지 추출 (call Retrieve Module)
    # """ 
    # Retreieve 모듈로 선택된 카테고리들에 대한 후보지들을 불러오기
    # -> dictionary로 각 카테고리 별로 후보지들이 들어가도록 만들어주기
    # """
    ## Inputs and Paramters (Requirements)
    w = 0.5
    k = 30

    ## Retrieval
    ### Load retrieval module
    retrieval = Retrieval(input_dict["request"], w, k, place_ids, CLOVA_API_KEY)

    ### Search
    retrieved_outputs = {}
    for category in choosed_category:
        outputs = retrieval.search(category[0]) ## candidate_place의 output에서 id만 뽑아서 place_ids로 활용
        retrieved_outputs[category[0]] = outputs
    retrieval.close_DB()

    # TODO: 현재 선택된 장소 (좌표) 기반으로 카테고리에 맞는 후보지들 선택 -> 마지막 카테고리까지 선택
    # """
    # TMap API사용해서 현재 장소(위경도)와 위에서 뽑은 후보지들과의 거리, 시간 추출
    # (추가) Naver MAP API를 사용해서 자동차 거리, 시간도 추출, Direction 5
    # """
    now_place = {"name": place, "lat": start_place_latlng[1], "lng": start_place_latlng[0],} # init
    global selected, candidates_per_category
    rec = Recommend(chatModel)
    for category in choosed_category:
        selected_candidate = []
        for i, candidate in enumerate(retrieved_outputs[category[0]]): # 현재 위치와 후보지들간의 거리 구하기
            if i > 5:
                print("Count 5, break")
                break
            candidate_place_info = get_candidate_place(candidate_places, candidate["id"]) # 후보지 장소 정보
            result = tMAP.get_direction_bet_coords_Tmap( # 각 후보지 당 distance_walking, time을 구함
                [now_place["lng"], now_place["lat"]],
                [candidate_place_info["lng"], candidate_place_info["lat"]],
                now_place["name"],
                candidate["name"],
            ) 
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
        recommend_query = rec.generate_prompt(now_place["name"], input_dict["request"], selected_candidate)
        response_rec = rec.invoke(recommend_query)
        # Parsing Response
        parsing_output = rec.parse_output(response_rec.content)
        logger.debug(f'{parsing_output}')
        recommend_id = parsing_output["id"] # id를 가져와서 선택한 후보지 정보 가져옴
        recommend_place_info = get_candidate_place(candidate_places, recommend_id)

        for retrieve_candidate in retrieved_outputs[category[0]]:
            if retrieve_candidate["id"] == int(recommend_id):
                recommend_review = retrieve_candidate["text"]
                recommend_positive = retrieve_candidate["positive_text"]
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
        logger.info(f"Selected place {selected}")
        
    for item in selected:
        if isinstance(item['type'], list):
            item['type'] = item['type'][0]
            
    # for key in candidates_per_category:
    #     for item in candidates_per_category[key]:
    #         if isinstance(item['type'], list):
    #             item['type'] = item['type'][0]
    logger.info(f"candidates_per_category {candidates_per_category}")
    st.session_state.selected = selected
    st.session_state.candidates_per_category = candidates_per_category




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
        selected_time = st.time_input("예상 시작 시각을 선택해주세요", value=time(12, 0))
        selected_datetime = datetime.combine(selected_date, selected_time).strftime('%Y-%m-%d %H:%M')


        submit_button = st.form_submit_button("AI 코스 추천 받기")
        
        if submit_button:
            # 입력값 저장 (UI용 저장 데이터)dhd
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
            st.session_state.input_dict = input_dict
            st.session_state.place = place_sel
            st.session_state.step = "loading"
            st.rerun()


def show_loading() -> None:
    """로딩 화면 표시"""
    st.empty()
    st.empty()
    st.title("AI 코스 추천 시스템")
    
    st.markdown(
        """
        <div style="text-align: center; font-size: 24px; font-weight: bold; padding: 20px;">
            🤖 AI가 최적의 코스를 찾고 있습니다...
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.spinner("잠시만 기다려 주세요..."):
        # searching_engine 함수 실행
        input_dict = st.session_state.get('input_dict')
        place = st.session_state.get('place')

        if input_dict and place:
            searching_engine(input_dict, place)
            # 검색이 완료되면 결과 페이지로 이동
            st.session_state.step = "result"
            st.rerun()


def get_alternative_locations(location_type: str) -> List[Dict]:
    """장소 타입별 대체 장소 목록 반환"""
    alternatives = copy.deepcopy(st.session_state.candidates_per_category)
    for key, places in alternatives.items():
        for place in places:
            place["type"] = key

    return alternatives.get(location_type, [])

def create_course_map(locations: list) -> folium.Map:
    """코스 위치들을 표시하는 지도 생성"""
    logger.debug(locations)
    center_lat = sum(loc['lat'] for loc in locations) / len(locations)
    center_lon = sum(loc['lon'] for loc in locations) / len(locations)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
    
    # 위치 마커 추가
    number_icon =  [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for idx, loc in enumerate(locations, 0):
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=loc['name'],
            icon=folium.DivIcon(
            icon_size=(20, 20),
            icon_anchor=(10, 10),
            html=f'<div style="font-size: 20px;">{number_icon[idx]}</div>'
        ),
            tooltip=f"{idx+1}. {loc['name']}",
        ).add_to(m)
    return m

def show_result() -> None:
    """결과 화면 표시"""
    st.title("AI 추천 코스")
    

    

    
    # 초기 코스 데이터 설정 및 원본 코스 저장
    if st.session_state.current_course is None:
        ui_course = {
            "locations": copy.deepcopy(st.session_state.selected),

        }
        st.session_state.current_course = ui_course
        # 원본 코스 저장
        st.session_state.original_course = copy.deepcopy(ui_course)
        
    # 코스에서 중복 장소 처리
    seen_names = {}
    alter = st.session_state.candidates_per_category
    key_list = list(alter.keys())

    for i, location in enumerate(st.session_state.current_course["locations"]):
        location_name = location["name"]
        if location_name in seen_names:
            previous_index = seen_names[location_name]
            if alter[key_list[previous_index]][1]:
                tmp = st.session_state.current_course["locations"][previous_index]
                st.session_state.current_course["locations"][previous_index] = alter[key_list[previous_index]][1]
                st.session_state.current_course["locations"][previous_index]["type"] = key_list[previous_index]
                break
        else:
            seen_names[location_name] = i

    # 최종적으로 상태 확인하기
    print("최종 candidates_per_category:")
    print(st.session_state.candidates_per_category)

    print("최종 current_course:")
    print(st.session_state.current_course)

    # 입력 정보 요약
    with st.expander("입력하신 정보", expanded=False):
        st.write("**검색 조건**")
        st.write(f"🔍 검색어: {st.session_state.user_query}")
        st.write(f"👤 연령대: {st.session_state.age}")
        st.write(f"🚹/🚺 성별: {st.session_state.gender}")
        st.write(f"📍 장소: {st.session_state.place}")
        st.write(f"⏰ 예상시작시간 : {st.session_state.start_day_and_time}")

    # 좌우 컬럼 생성
    left_col, right_col = st.columns([5, 5])

    # 왼쪽 컬럼: 코스 정보
    with left_col:
        st.subheader("AI 추천 코스 상세")
        course = st.session_state.current_course



        # 각 장소별 상세 정보
        for i, loc in enumerate(course['locations'], 1):
            with st.expander(f"{i}. {loc['type']}",expanded=True):
                st.markdown(f"#### {i}. {loc['name']}")
                rating= '<p>⭐ 평점: ' + str(loc['rating']) + '</p>' if loc['rating'] is not None else '<p>⭐ 평점: 아직 정보가 없습니다.</p>'
                # Streamlit에서 HTML 출력
                st.markdown(rating, unsafe_allow_html=True)
                st.write(f"🏠 {loc['address']}")
                st.write("**<추천 분석>**")
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
                    st.rerun()

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
                            st.markdown(
                                f"""
                                <div style="
                                    border: 2px solid #ddd; 
                                    border-radius: 10px; 
                                    padding: 15px; 
                                    margin-bottom: 10px;
                                    background-color: #f9f9f9;">
                                    <h4>→ {alt['name']}</h4>
                                    <p>🏠 {alt['address']}</p>
                                    {'<p>⭐ 평점: ' + str(alt['rating']) + '</p>' if alt['rating'] is not None else '<p>⭐ 평점: 아직 정보가 없습니다.</p>'}
                                    <p><b style="color: #555;"><추천 분석></b></p>
                                    <p>📍 {alt['description']}</p>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                            col1, col2 = st.columns([7, 3])
                            with col2:
                                if any(alt['name'] == alt2['name']  for alt2 in st.session_state.current_course['locations']) :
                                     st.write("코스에 존재")
                                else :
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
            if i != len(course['locations']) : 
                st.markdown("<span style='font-size: 25px;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⬇️</span>", unsafe_allow_html=True)

                        

    # 오른쪽 컬럼: 지도
    with right_col:
        st.subheader("코스 지도")
        course_map = create_course_map(course['locations'])
        st_folium(course_map, width=None, height=600)
        number_icon =  [ "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        with st.expander("상세 장소 정보", expanded=True):
            types = [loc['type'] for loc in course['locations']]  # 'type'을 리스트로 추출
            st.write("---")
            st.write("< 코스 순서 >")
            st.write(" ➡️ ".join(types))
            st.write("---")
            st.write("< 장소 이름 >")
            for i in range(len(course['locations'])) :
                st.write(f"{number_icon[i]} : {course['locations'][i]['name']}")
        if st.button("현재 코스 저장"):
            # 현재 코스를 저장
            st.session_state.saved_courses.append(st.session_state.current_course.copy())
            st.success("현재 코스가 저장되었습니다!")
        with st.expander("코스 저장 목록", expanded=True):
            if st.session_state.saved_courses:
                for idx, saved_course in enumerate(st.session_state.saved_courses):
                    if st.button(f"코스 {idx + 1}", key=f"course_button_{idx}"):
                        st.session_state.current_course = saved_course
                        st.rerun()
                    else:
                        st.write(" ")
                
            
                  

            

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
    # naverMAP = NaverMap()
    chatModel = ClovaXChatModel(API_KEY=CLOVA_API_KEY)
    tMAP = Tmap_API(API_KEY=TMAP_API_KEY)
    database = SQLiteDatabase("./db/place_Information.db")
    category_generator = Category(chatModel, database)

    
    initialize_session_state()
    
    # 현재 단계에 따른 화면 표시
    current_step = st.session_state.step
    if current_step == "init":
        show_init()
    elif current_step == "details":
        show_details()
    elif current_step == "loading": 
        show_loading()
    elif current_step == "result":
        show_result()
    

   
