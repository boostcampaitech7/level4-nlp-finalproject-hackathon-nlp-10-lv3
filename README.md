# 개인화 코스 추천 시스템

<p>


<img src="https://img.shields.io/badge/LangChain-0055CC?style=flat&logo=Chainlink&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/HyperCLOVA_X-00C853?style=flat&logo=Naver&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=HTML5&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=CSS3&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Jira-0052CC?style=flat&logo=Jira&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Notion-000000?style=flat&logo=Notion&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/GitHub-181717?style=flat&logo=GitHub&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/SQLite3-orange?style=flat&logo=sqlite&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/TmapAPI-Blue?style=flat&logo=map&logoColor=white"/>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Python-3776AB?style=square&logo=Python&logoColor=white"/>


</p>


## 📌프로젝트 개요

<p align="center">
  <img src="figure/wity_main.png" width="600">

</p>


>기간 |&nbsp;&nbsp;  25년 1월 10일 ~ 25년 2월 10일

>소개 |<br>
    &nbsp;사람의 기본적인 취향은 바뀌지 않지만 하루하루 상황과 기분은 변화할 수 있습니다.<br> 우리의 서비스는 그때 그떄의 유저의 변화를 질문 분석을 통하여 코스를 생성함으로서 새로운 경험을 전달합니다.

> **참고** |&nbsp;  본 프로젝트는 현재 '서울 종로구'를 한정하여 진행되었습니다. 


<br>
<br>

## 👥 팀원 및 역할

이정휘|강경준|김재겸|권지수|박동혁|이인설
:-:|:-:|:-:|:-:|:-:|:-:
<img src='https://avatars.githubusercontent.com/u/55193363?v=4' height=130 width=130></img>|<img src='https://avatars.githubusercontent.com/u/73216281?v=4' height=130 width=130></img>|<img src="https://avatars.githubusercontent.com/u/111946234?s=400&amp;u=faab0892244c59ec8bda612f162ae0d55a8665d7&amp;v=4"  height=130 width=130></img>|<img src="https://avatars.githubusercontent.com/u/83396988?v=4" height=130 width=130></img>|<img src='https://avatars.githubusercontent.com/u/171525486?v=4' height=130 width=130></img>|<img src='https://avatars.githubusercontent.com/u/128824976?v=4' height=130 width=130></img>|
<a href="https://github.com/LeeJeongHwi" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/K-yng" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/rlaworua5667" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/JK624" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/someDeveloperDH" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>|<a href="https://github.com/SnowmanLab" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a>
<a href="mailto:wjdgnl97@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:kangjun205@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:worua5667@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:s006249@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:pangyongpy@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>|<a href="mailto:luns0712@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-EA4335?style&logo=Gmail&logoColor=white"/></a>

<br>

## 팀원 역할

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

## 아키텍처
<p align="center">
  <img src="figure/arch.png" width="600">

>진행방법 | <br>  1) &nbsp;3사에 대한 장소정보와 리뷰 크롤링 후 전처리
<br>  2) &nbsp;각 가게에 대한 리뷰를 요약
<br>  3) &nbsp; 장소 정보 DB와 리뷰 벡터 DB 생성
<br>  4) &nbsp; 사용자로 부터 질문, 나이, 장소, 시작시간, 성별 정보를 받기
<br>  5) &nbsp;  코스 생성
<br>   &nbsp; &nbsp; 5-1) &nbsp; CoT기반의 프롬프트 엔지니어링을 하여 하이퍼 클로버 X로 카테고리 코스 생성
<br>   &nbsp; &nbsp; 5-2) &nbsp; 사용자 질문에 적학한 장소를 리트리버를 통하여 찾기
<br>   &nbsp; &nbsp; 5-3) &nbsp; 사용자에게 입력받은 장소의 위도 경도를 기준으로 리트리버에서 뽑힌 장소들의 거리를 고려하여 코스 생성
<br>  6) &nbsp;  사용자에게 생성된 코스 정보 시각화
<br>
<br>

## 프로젝트 진행 계획

<p align="center">
  <img src="figure/timeline.png" width="600">




<br>
<br>

## 파일구조

```
  📦level4-nlp-finalproject-hackathon-nlp-10-lv3
  ┣ 📂EDA
  ┃ ┣ 📂concat
  ┃ ┃ ┣ 📜cleaning_business_hours_1.ipynb
  ┃ ┃ ┣ 📜cleaning_business_hours_2.ipynb
  ┃ ┃ ┣ 📜eda_all_1.ipynb
  ┃ ┃ ┣ 📜eda_all_2.ipynb
  ┃ ┃ ┗ 📜eda_all_3.ipynb
  ┃ ┣ 📂crawling
  ┃ ┃ ┣ 📜eda_google_1.ipynb
  ┃ ┃ ┣ 📜eda_kakao_1.ipynb
  ┃ ┃ ┣ 📜eda_naver_1-1.ipynb
  ┃ ┃ ┗ 📜eda_naver_1-2.ipynb
  ┃ ┗ 📂figure
  ┃ ┃ ┗ 📜EDA.ipynb
  ┣ 📂baseline
  ┃ ┃ ┗ 📜config.toml
  ┃ ┣ 📂db
  ┃ ┃ ┣ 📜course_rcmd.db
  ┃ ┃ ┣ 📜course_rcmd_pos.db
  ┃ ┃ ┣ 📜database.py
  ┃ ┃ ┣ 📜db_test_code.py
  ┃ ┃ ┣ 📜place_Information.db
  ┃ ┃ ┗ 📜vectordb_test_code.py
  ┃ ┣ 📂mapAPI
  ┃ ┃ ┣ 📜NaverSearchAPI.py
  ┃ ┃ ┗ 📜TMapAPI.py
  ┃ ┣ 📂model
  ┃ ┃ ┣ 📜ChatModel.py
  ┃ ┃ ┣ 📜Retrieve.py
  ┃ ┃ ┗ 📜sparse_embedding.pkl
  ┃ ┣ 📂utils
  ┃ ┃ ┣ 📜category.py
  ┃ ┃ ┣ 📜coll_name_mapping.py
  ┃ ┃ ┣ 📜geopy_util.py
  ┃ ┃ ┗ 📜recommend.py
  ┃ ┣ 📜.env
  ┃ ┗ 📜main.py #실행파일
  ┣ 📂evaluation
  ┃ ┣ 📜configs.yaml
  ┃ ┣ 📜evaluation.py
  ┃ ┣ 📜make_category_route.py
  ┃ ┣ 📜make_scenario.py
  ┃ ┗ 📜summary_evaluation.py
  ┣ 📂model
  ┃ ┗ 📜sparse_embedding.pkl
  ┣ 📂prompts
  ┃ ┣ 📜cate_crs_eval_prmpt.yaml
  ┃ ┣ 📜eval_summary_prompt.txt
  ┃ ┣ 📜prompt_summary.txt
  ┃ ┣ 📜query_prompt.txt
  ┃ ┗ 📜system_prompt.txt
  ┣ 📂temps
  ┃ ┗ 📜imagetomood.py
  ┣ 📂utils
  ┃ ┣ 📜__init__.py
  ┃ ┗ 📜util.py
  ┣ 📜construct_vectorDB.py
  ┣ 📜requirements.txt
  ┗ 📜review_summary.py
```


## How to run

```
#사전 준비

python baseline/db/db_test_code.py #SQLlite DB생성
python baseline/db/vectordb_test_code.py # 벡터 DB 생성
```

```
#서비스 코드 실행

cd baseline
streamlit run main.py # 스트림릿 UI실행
```


<br>
<br>

## 평가
* 요약에 대한 평가

<p align="center">
  <img src="figure/eval1.png" width="600" >

>G_eval 평가 방식과 독립표본-t 검정을 참고하여  긍정과 부정 리류 요약 결과에 대한 평가를 진행 하였고 평가 항목은 다음과 같습니다.

> Coherence (일관성, 1~5점): 긍정/부정 요약과 전체 요약이 논리적으로 연결되는가?<br>
Consistency (사실성, 1~5점): 원본 리뷰에 기반한 사실적 일치 여부, 환각 정보 여부<br>
Fluency (유창성, 1~3점): 문법, 맞춤법, 문장 구조 등의 자연스러움<br>
Relevance (관련성, 1~5점): 원문의 핵심 내용을 명확히 반영하는가?

> 결과 : 리뷰의 갯수가 많아 질 수록 ,특히 부정적, 요약의 품질이 떨어짐에 최근 달린 리뷰들로 갯수 한정 지어 요약을 진행하였습니다.

<br>

* 경로 생성에 대한 평가

<p align="center">
  <img src="figure/eval2.png" width="600">

>아래와 같이 시나리오 데이터 셋을 GPT-4o를 통하여 진행하였습니다.
<details>

  <summary>시나리오 데이터</summary>
  <p align="center">
  <img src="figure/data_ex.png" width="600">

</details>
<br>

>결과 :  먼저, Origin의 경우 매우 구체적이고, 디테일한 고객 요구 사항이 주어지는 경우를 상정했습니다. Few-shot과 CoT의 경우 80%에 근접하는 성적을 얻을 수 있었고 다음으로 Strage의 경우, 간결한 요구 사항이 주어지는 경우를 상정했습니다 요구 사항이 많지 않기 때문에 평가할 사항이 많지 않고, orgin과 비교하여 전반적으로 점수가 높은 것을 확인이 됩니다. 추가적으로 두 경우 모두 성능 향상을 위해 Self-Refine을 적용시켰으나, 충분한 향상을 이끌어내지 못하여 추후, Self-Refine을 더욱 고도화 하거나 guide-line을 평가가 아닌 Self-Refine 과정에 포함시켜 더욱 성능을 개선할 수 있을 것으로 기대됩니다.





<br>
<br>

## Commit Rule
<br>

| **유형**  | **설명** |
|----------------|----------------------------------------|
| **feat**       | 기능 (새로운 기능)                     |
| **fix**        | 버그 (버그 수정)                       |
| **refactor**   |리팩토링                                |
| **style**      | 스타일 (코드 형식, 세미콜론 추가: 비즈니스 로직에 변경 없음) |
| **docs**       | 문서 (문서 추가, 수정, 삭제)           |
| **test**       | 테스트 (테스트 코드 추가, 수정, 삭제: 비즈니스 로직에 변경 없음) |
| **chore**      | 기타 변경사항 (빌드 스크립트 수정 등)  |


# 추가 자료

[📄 프로젝트 보고서 (PDF)](report/NLP-10-기업해커톤-wrapupreport.pdf)


