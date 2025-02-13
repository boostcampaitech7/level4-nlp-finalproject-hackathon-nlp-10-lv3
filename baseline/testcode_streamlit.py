import streamlit as st
from streamlit_folium import st_folium
import folium
from typing import Dict, List, Optional
import copy

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

def show_details() -> None:
    """상세 정보 입력 화면"""
    st.title("상세 정보 입력")
    
    # 이전 입력 쿼리 표시
    st.info(f"입력하신 검색어: {st.session_state.user_query}")

    # 입력 폼 생성
    with st.form(key="details_form"):
        # 연령대 선택
        age = st.radio(
            "연령대",
            options=["10대", "20대 초반", "20대 중반", "20대 후반", "30대 초반"],
            index=2,
            horizontal=True
        )
        
        # 성별 선택
        gender = st.radio(
            "성별",
            options=["남성", "여성", "기타"],
            horizontal=True
        )
        
        # 장소 선택
        place = st.selectbox(
            "선호하는 장소",
            options=["실내", "실외", "복합공간"],
            help="활동하고 싶은 장소 유형을 선택해주세요"
        )
        
        # 추가 정보
        preferences = st.text_area(
            "선호하는 활동이나 분위기",
            help="구체적인 선호사항을 자유롭게 입력해주세요"
        )
        
        budget = st.number_input(
            "예산 (만원)",
            min_value=0,
            max_value=100,
            value=10,
            help="예상하는 비용을 입력해주세요"
        )

        submit_button = st.form_submit_button("AI 코스 추천 받기")
        
        if submit_button:
            # 입력값 저장
            st.session_state.update({
                "age": age,
                "gender": gender,
                "place": place,
                "preferences": preferences,
                "budget": budget
            })
            st.session_state.step = "result"
            st.rerun()

def get_alternative_locations(location_type: str) -> List[Dict]:
    """장소 타입별 대체 장소 목록 반환"""
    alternatives = {
        "카페": [
            {
                "name": "성수동 카페거리",
                "lat": 37.5445,
                "lon": 127.0557,
                "description": "힙한 감성의 카페 거리",
                "time": "14:00 - 15:30",
                "type": "카페",
                "recommendation_reason": """
                - 인더스트리얼한 분위기의 독특한 카페들이 밀집
                - SNS에서 인기 있는 포토스팟 다수
                - 로스터리 카페가 많아 커피 맛이 뛰어남
                - 주변 공방과 갤러리들과 함께 둘러보기 좋음
                """
            },
            {
                "name": "연남동 카페거리",
                "lat": 37.5605,
                "lon": 126.9233,
                "description": "아기자기한 분위기의 카페",
                "time": "14:00 - 15:30",
                "type": "카페",
                "recommendation_reason": """
                - 아늑하고 편안한 분위기의 카페들이 즐비
                - 골목골목 숨은 맛집과 카페 탐방 가능
                - 젊은 감각의 디저트 카페가 많음
                - 홍대와 가깝지만 상대적으로 여유로운 분위기
                """
            }
        ],
        "거리": [
            {
                "name": "삼청동 거리",
                "lat": 37.5826,
                "lon": 126.9826,
                "description": "전통과 현대가 어우러진 길",
                "time": "16:00 - 17:30",
                "type": "거리",
                "recommendation_reason": """
                - 한옥과 현대 건물이 조화롭게 어우러진 풍경
                - 다양한 갤러리와 부티크 샵 관람 가능
                - 계절별로 달라지는 거리 분위기를 즐길 수 있음
                - 북촌한옥마을과 인접해 연계 관광 용이
                """
            },
            {
                "name": "가로수길",
                "lat": 37.5514,
                "lon": 127.0228,
                "description": "트렌디한 상점가",
                "time": "16:00 - 17:30",
                "type": "거리",
                "recommendation_reason": """
                - 최신 트렌드를 한눈에 볼 수 있는 패션 거리
                - 유니크한 컨셉의 숍과 맛집이 많음
                - 계절별 테마로 바뀌는 거리 이벤트
                - 감각적인 쇼핑과 문화생활을 동시에 즐길 수 있음
                """
            }
        ],
        "시장": [
            {
                "name": "통인시장",
                "lat": 37.5799,
                "lon": 126.9688,
                "description": "도시락카페로 유명한 전통시장",
                "time": "18:00 - 19:30",
                "type": "시장",
                "recommendation_reason": """
                - 엽전으로 즐기는 특별한 도시락 카페 체험
                - 오래된 맛집들의 진정성 있는 로컬 맛집
                - 전통시장 특유의 활기찬 분위기
                - 경복궁과 가까워 관광하기 좋은 위치
                """
            },
            {
                "name": "망원시장",
                "lat": 37.5559,
                "lon": 126.9108,
                "description": "맛집이 많은 재래시장",
                "time": "18:00 - 19:30",
                "type": "시장",
                "recommendation_reason": """
                - MZ세대에게 인기 있는 새로운 맛집들이 다수
                - 합리적인 가격의 신선한 식재료
                - 시장 상인들과의 정겨운 교류 가능
                - 한강공원과 가까워 산책하기 좋음
                """
            }
        ]
    }
    return alternatives.get(location_type, [])

def create_course_map(locations: list) -> folium.Map:
    """코스 위치들을 표시하는 지도 생성"""
    center_lat = sum(loc['lat'] for loc in locations) / len(locations)
    center_lon = sum(loc['lon'] for loc in locations) / len(locations)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
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
        example_course = {
            "title": "레트로 감성 데이트 코스",
            "locations": [
                {
                    "name": "을지로 카페거리",
                    "lat": 37.5665,
                    "lon": 126.9780,
                    "description": "빈티지한 분위기의 카페",
                    "time": "14:00 - 15:30",
                    "type": "카페"
                },
                {
                    "name": "익선동 한옥거리",
                    "lat": 37.5724,
                    "lon": 126.9905,
                    "description": "전통과 현대가 어우러진 골목",
                    "time": "16:00 - 17:30",
                    "type": "거리"
                },
                {
                    "name": "광장시장",
                    "lat": 37.5701,
                    "lon": 126.9988,
                    "description": "전통시장 맛집 투어",
                    "time": "18:00 - 19:30",
                    "type": "시장"
                }
            ],
            "total_time": "5시간 30분",
            "budget": "8만원"
        }
        st.session_state.current_course = example_course
        # 원본 코스 저장
        st.session_state.original_course = copy.deepcopy(example_course)

    # 입력 정보 요약
    with st.expander("입력하신 정보", expanded=False):
        st.write("**검색 조건**")
        st.write(f"- 검색어: {st.session_state.user_query}")
        st.write(f"- 연령대: {st.session_state.age}")
        st.write(f"- 성별: {st.session_state.gender}")
        st.write(f"- 선호 장소: {st.session_state.place}")
        st.write(f"- 선호사항: {st.session_state.preferences}")
        st.write(f"- 예산: {st.session_state.budget}만원")

    # 좌우 컬럼 생성
    left_col, right_col = st.columns([5, 5])

    # 왼쪽 컬럼: 코스 정보
    with left_col:
        st.subheader("추천 코스 상세")
        course = st.session_state.current_course
        
        st.markdown(f"### {course['title']}")
        st.markdown(f"**소요시간**: {course['total_time']}")
        st.markdown(f"**예상비용**: {course['budget']}")
        
        # 각 장소별 상세 정보
        for i, loc in enumerate(course['locations'], 1):
            with st.expander(f"{i}. {loc['name']}", expanded=True):
                st.write(f"⏰ 추천 시간: {loc['time']}")
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
                                if 'recommendation_reason' in alt:
                                    st.write(alt['recommendation_reason'])
                                st.write(f"📍 {alt['description']}")
                                st.write(f"⏰ 추천 시간: {alt['time']}")
                                
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



def main() -> None:
    """메인 함수"""
    st.set_page_config(
        page_title="AI 코스 추천 시스템",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    initialize_session_state()

    # 현재 단계에 따른 화면 표시
    current_step = st.session_state.step
    if current_step == "init":
        show_init()
    elif current_step == "details":
        show_details()
    elif current_step == "result":
        show_result()

if __name__ == "__main__":
    main()
