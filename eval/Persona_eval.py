import openai

# API 키 불러오기 (환경 변수에서 가져오기 권장)
API_KEY = "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"  # OpenAI API 키 입력

openai.api_key = API_KEY  # API 키 설정

# ChatGPT 모델 호출
def chat_with_gpt(prompt, model="gpt-4o", max_tokens=300):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "너는 지정된 페르소나야"},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

# 테스트 실행
# prompt = """
# 코스(맛집,놀거리, 명소, 액티비티, 등) 추천 해주는 AI 시스템을 이용할 사람들의 페르소나를 무작위로 3명을 만들어줘

# <필수포함정보>
# 1. 17세~60대의 연령대
# 2. 취향
# 3. 현재 기분
# 4. 평소 선호하는 장소.
# 5. 개인정보들
# 6. 성격

# 가상의 인물을 만들어줘
# """
prompt = """
너는 다음의 사람이야. 김하늘이 코스(맛집,놀거리, 명소, 액티비티, 등)를 만들기 위해서 검색할 질문을 생성해줘.야야
장소는 종로구이고 하나의 코스를 원해.질문은 페르소나의 취향도 반영해줘줘

### 페르소나 1: 김하늘

1. **연령대**: 25세
2. **취향**: 최신 트렌드와 패션에 민감하며, 인스타그램에 사진을 올리기 좋은 곳을 선호함.
3. **현재 기분**: 설레고 기대에 차 있음. 친구들과의 주말 모임을 계획 중.
4. **평소 선호하는 장소**: 강남의 트렌디한 카페와 핫플레이스, 분위기 있는 루프탑 바.
5. **개인정보들**:
   - 직업: 대학생 겸 패션 블로거
   - 거주지: 서울 강남구
   - 가족: 부모님과 함께 거주
6. **성격**: 외향적이고 사교성이 뛰어나며, 새로운 사람들과의 만남을 즐김. 호기심이 많고 도전을 즐기는 편.
"""
response = chat_with_gpt(prompt)
print(response)
