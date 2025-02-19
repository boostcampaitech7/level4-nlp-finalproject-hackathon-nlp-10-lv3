# :compass:WITY (What should I do TodaY)



<p>
  <img src="https://img.shields.io/badge/Jira-0052CC?style=flat&logo=Jira&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Confluence-172B4D?style=flat&logo=confluence&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/LangChain-0055CC?style=flat&logo=Chainlink&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/HyperCLOVA_X-00C853?style=flat&logo=Naver&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/SQLite3-orange?style=flat&logo=sqlite&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Milvus-blue?style=flat&logo=milvus&logoColor=white"/>
</p>





## 📌프로젝트 개요

<p align="center">
  <img src="figure/wity_main.png">

</p>

### 소개
우리는 많은 시간을 그저 계획하는 데 사용합니다.  
하루의 일정을 계획하기 위해, 다양한 장소를 검색하고 리뷰를 확인하며 결정하기 까지 지나치게 많은 시간이 소비됩니다.  
  
WITY는 자동 경로 생성 서비스를 통해 이런 문제를 해결합니다.  
사용자의 요구사항을 WITY에게 전달하면, 장소 리뷰 기반으로 적절한 장소들을 선정하여 자동으로 경로를 생성합니다.  
  
이를 통해, 우리는 사용자에게 편리한 사용성과 다양한 경험을 제시하고자 합니다.

- 기간
  - 2025.01.06 - 2025.02.09
- 참고
  - 본 프로젝트는 검색 범위를 '서울 종로구'로 한정하여 진행되었습니다.


<br>
<br>

## 👥 팀원 및 역할
### 팀원

이정휘|강경준|김재겸|권지수|박동혁|이인설
:-:|:-:|:-:|:-:|:-:|:-:
<img src='https://avatars.githubusercontent.com/u/55193363?v=4' height=130 width=130></img>|<img src='https://avatars.githubusercontent.com/u/73216281?v=4' height=130 width=130></img>|<img src="https://avatars.githubusercontent.com/u/111946234?s=400&amp;u=faab0892244c59ec8bda612f162ae0d55a8665d7&amp;v=4"  height=130 width=130></img>|<img src="https://avatars.githubusercontent.com/u/83396988?v=4" height=130 width=130></img>|<img src='https://avatars.githubusercontent.com/u/171525486?v=4' height=130 width=130></img>|<img src='https://avatars.githubusercontent.com/u/128824976?v=4' height=130 width=130></img>|
<a href="https://github.com/LeeJeongHwi" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/K-yng" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/rlaworua5667" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/JK624" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/someDeveloperDH" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/SnowmanLab" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>
<a href="mailto:wjdgnl97@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:kangjun205@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:worua5667@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:s006249@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:pangyongpy@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:luns0712@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>

<br>

### 역할

| 이름   | 역할 및 담당 업무 |
|--------|--------------------------------------------------------------|
| **이정휘** | - Jira를 통한 프로젝트 일정 및 태스크 관리 <br> - 구글 맵 리뷰 데이터 수집 <br> - 여러 Map API 비교 및 테스트 <br> - UI 설계 및 Streamlit Map 구현, 전체 baseline 코드 설계 <br> - LLM, Map API를 활용한 카테고리별 장소 선택 기능 구현 |
| **강경준** | - 요약 데이터 parsing 및 VectorDB 구현 <br> - LLM Prompting 기반 경로 생성 능력 테스트 <br> - 리뷰 및 요구사항 기반 Hybrid Search Model 구현 <br> - 경로에 대한 guideline 기반의 카테고리 코스 생성 능력 LLM 평가 |
| **김재겸** | - 리뷰 요약 기능 구현 <br> - 리뷰 요약 능력 평가 및 리뷰 개수에 따른 점수 차이 검증 <br> - 이미지 업로드 기능 구현 |
| **권지수** | - 네이버 지도 리뷰 데이터 수집 <br> - 데이터 전체 검수 및 EDA <br> - 데이터 전처리 |
| **박동혁** | - 카카오 지도 리뷰 데이터 수집 <br> - Streamlit UI 구성 및 구현 <br> - UI와 검색 시스템간 데이터 송수신 처리 |
| **이인설** | - 네이버 지도 리뷰 데이터 수집 <br> - 사용자 요구에 따른 카테고리 경로 생성 구현 <br> - 다양한 조건에 대한 시나리오 데이터 생성 |



<br>
<br>

## 🏛️ 서비스 아키텍처

<p align="center">
  <img src="figure/arch.png">

유저의 요구사항을 반영한 맞춤형 당일 일정 경로 추천을 목표로 하며, 이를 위해 카테고리 기반 경로 생성 후 최적의 장소 추천 방식을 채택하였습니다.

### 🗺️ 카테고리 기반 추천 코스 생성
- "요구사항", "연령대", "성별", "일정 시작 시간"입력을 바탕으로 적절한 카테고리 기반 경로를 생성
  - ex) `[["음식점"], ["카페"], ["체험관광"], ["음식점"]]`
- LLM기반으로 카테고리 생성 후 파싱
  - [category.py](https://github.com/boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-10-lv3/blob/main/baseline/utils/category.py#L40) 코드 참조

### 🎯 반경 내 장소 필터링
- 사용자가 가고자하는 장소를 입력하면, 반경 500m ~ 1km 내 DB에 등록된 장소만 추출
- Naver Search API를 통해 입력된 장소의 위도 경도를 구함
- 입력된 장소와 DB에 있는 장소들과의 위도 경도 기반으로 Haversine 공식을 적용해 직선거리를 구해서 장소들을 필터링함
  - [database.py](https://github.com/boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-10-lv3/blob/main/baseline/db/database.py#L81) query 참조

### 🔍 카테고리별 후보 장소 탐색
- 사용자 요구사항과 반경 내 장소들의 리뷰 간 유사도 기반 검색을 수행하는 RAG 시스템
- Milvus기반 Hybrid Search 수행
- 요약된 긍정, 부정 리뷰와 요구사항간의 유사도 계산 후 두 값의 차를 이용해 Dense Score 계산
$$\text{Dense Score} = \frac{PosCnt}{PosCnt + NegCnt} PosScore - \frac{NegCnt}{PosCnt+NegCnt} NegScore$$
- [Retrieve.py](https://github.com/LeeJeongHwi/WITY/blob/main/baseline/model/Retrieve.py)
### ⭐ 후보 장소 중 추천장소 선정
- Retrieval로 탐색된 장소들 중에서 가장 리뷰와 유사하고 거리가 가까운 장소 선택
- 각 카테고리별로 장소를 탐색할 때, 이전 카테고리에서 선택된 장소와 후보장소들 간의 거리를 구함
  - TMap API를 사용해 후보 장소와 이전에 선택된 장소와의 거리와 소요시간을 구함
- LLM Prompting으로 후보 장소 reranking 수행
  - [recommend.py](https://github.com/LeeJeongHwi/WITY/blob/main/baseline/utils/recommend.py) 참조

## 📆 프로젝트 타임라인

<p align="center">
  <img src="figure/timeline.png">

<br>
<br>

## 📂 파일구조

```python
  📦level4-nlp-finalproject-hackathon-nlp-10-lv3
  ┣ 📂baseline
  ┃ ┃ ┗ 📜config.toml
  ┃ ┣ 📂db # RDB, VectorDB 생성 
  ┃ ┃ ┣ 📜database.py # Database 연결 및 select 클래스
  ┃ ┃ ┣ 📜rdb_create_code.py # RDB 생성 코드
  ┃ ┃ ┗ 📜vectordb_test_code.py # Vector DB 생성 코드
  ┃ ┣ 📂mapAPI
  ┃ ┃ ┣ 📜NaverSearchAPI.py # Search API
  ┃ ┃ ┗ 📜TMapAPI.py # TMap API request 코드 및 parsing
  ┃ ┣ 📂model
  ┃ ┃ ┣ 📜ChatModel.py # HyperCLOVA X Chat Model 클래스
  ┃ ┃ ┣ 📜Retrieve.py # Retrieval 모델 클래스
  ┃ ┃ ┗ 📜sparse_embedding.pkl
  ┃ ┣ 📂utils
  ┃ ┃ ┣ 📜category.py # 카테고리 기반 경로 생성
  ┃ ┃ ┣ 📜coll_name_mapping.py 
  ┃ ┃ ┣ 📜geopy_util.py 
  ┃ ┃ ┗ 📜recommend.py # 후보 장소 중 추천 장소 선정
  ┃ ┣ 📜.env
  ┃ ┗ 📜main.py # 전체 실행파일 및 Streamlit UI
```

## ▶️How to run
### 0. 데이터 준비, env 설정
-  `[id, domain, name, main_category, category, rating, address, business_hours, price_per_one]` 으로 구성된 "장소 정보 csv 파일" 필요합니다.
- `[id, domain, name, reviews]` 으로 구성된 "장소에 따른 리뷰 csv 파일" 필요합니다.

필요한 API Key는 다음과 같습니다. baseline 폴더 내 `.env` 파일 생성 후 아래 키 설정을 해주세요.
```
NAVER_MAP_API_ID = ""
NAVER_MAP_API_KEY = ""
NAVER_SEARCH_API_ID = ""
NAVER_SEARCH_API_KEY = ""
CLOVA_API_KEY = ""
CLOVA_SERVICE_KEY = ""
TMAP_API_KEY = ""
```

### 1. RDB, VectorDB 생성
```
python baseline/db/rdb_create_code.py #SQLlite DB생성
python baseline/db/vectordb_test_code.py # 벡터 DB 생성
```
- 각 코드 내 경로 수정이 필요합니다.

### 2. UI 실행
```
streamlit run main.py # 스트림릿 UI실행
```


## 📈평가
### 리뷰 요약 모델 평가

| 평가 항목     | 설명                                       | 점수 범위   |
|---------------|--------------------------------------------|------------|
| **Coherence** | 긍정/부정 요약과 전체 요약이 논리적으로 연결되는가? | 1~5점      |
| **Consistency** | 원본 리뷰에 기반한 사실적 일치 여부, 환각 정보 여부 | 1~5점      |
| **Fluency**   | 문법, 맞춤법, 문장 구조 등의 자연스러움       | 1~3점      |
| **Relevance** | 원문의 핵심 내용을 명확히 반영하는가?       | 1~5점      |

- 평가 방법
  - **Hyper Clova X(HCX-003)** 활용한 LLM 기반 평가
  - **LLM prompting** 기반으로 상기의 평가 항목에 대한 평가 진행
  - 리뷰 개수에 따른 요약 성능 차이 분석을 위해, 리뷰 개수 **20개를 기준으로 두 그룹으로 구분**
  - 각 그룹 별로 데이터 300개 샘플링하여 평가 진행
  - 평가 신뢰도를 높이고 continuous한 score를 얻기 위해, **20회 반복 평가 수행**

<p align="center">
  <img src="figure/eval1.png" width="1000" >

- 평가 결과
  - 리뷰 개수 20개 이하인 데이터에서 대체로 높은 성적을 보였고,  
    특히 일관성(Coherence)과 관련성(Relevance) 지표에서 차이가 두드러짐
  - 두 그룹에 대한 독립 표본 t-test 수행 결과,  
    coherence, relevance, consistency 세 항목에서 유의수준 0.05 기준으로 유의미한 차이를 확인
 
- 결론
  - **리뷰 개수가 많을수록 요약 성능이 떨어지는 경향성** 존재
  - 부정적 의견을 요약할 때, 내용이 일부 누락되는 문제 발생
  - 따라서, 적절한 리뷰 개수를 설정하여 요약하는 것이 품질 향상에 도움이 될 것으로 보임
  - 추후에는 적절한 리뷰 개수 설정 방안 및 설정 기준 등에 대한 연구가 필요할 것으로 사료됨

<br>

### 경로 생성 모델 평가

- 시나리오 데이터 생성
  - 실제 사용자 활용성에 대한 평가를 위해, 사용자 요구사항 데이터 생성
  - '성별', '연령대', '일정 시작 시간'을 랜덤하게 생성한 뒤, **'사용자 요구 사항'을 LLM을 통해 생성**
  - '사용자 요구 사항'이 구체적이고 자세한 original dataset과 일부 내용이 생략되거나 글이 간결하게 작성된 strange dataset **두 가지 경우 상정**
 
- 평가 방법
  - **생성하지 말아야 할 경로들의 특성**을 기준으로 평가 guide-line 작성
  - 해당 guide-line을 기준으로 LLM 평가 진행 / **gpt-4o** 활용
  - 경로를 생성하는 **4가지 methods(few-shot(v1), few-shot(v2), CoT, Self-Refine)에** 대해 각각 평가 진행
  - 각 methods별로 전체 데이터 중 guide-line을 모두 만족하는 데이터의 비율 비교
      
      $$Score=\dfrac{\text{number of data points meeting guide-lines}}{\text{number of total data points}}$$

<p align="center">
  <img src="figure/eval2.png" width="600">

- 결과
  - 전반적으로 만족해야 할 조건이 만은 **origin dataset이 strange dataset에서 보다 낮은 성적**을 보여줌
  - Few-shot에서 높은 성적을 보이고 있고, **CoT와 Self-Refine에서는 상대적으로 낮은 성적**을 보임
  - 이러한 문제는 **CoT와 Self-Refine 내부에서 guide-line을 직접적으로 활용**함으로써 성능을 개선할 수 있을 것으로 보임

<br>
<br>

# 📄추가 자료
[📄 프로젝트 보고서 (PDF)](report/NLP-10-기업해커톤-wrapupreport.pdf)


