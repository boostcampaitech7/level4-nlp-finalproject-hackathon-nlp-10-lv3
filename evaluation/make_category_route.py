import os
import time
import pandas as pd
from tqdm import tqdm
from langchain_community.chat_models import ChatClovaX # pip install langchain, langchain-community


os.environ["NCP_CLOVASTUDIO_API_KEY"] = ""

def get_llm_answer(system_prompt, inputs):
    chat = ChatClovaX(
        model="HCX-003", 
        max_tokens= 4096,
    )
    messages = [
        ("system", system_prompt),
        ("human", inputs)
    ]
    outputs = chat.invoke(messages)
    time.sleep(5)

    return outputs.content

def get_big_category_fewshot(system_prompt, inputs):
    outputs = get_llm_answer(system_prompt, inputs)
    extracted_outputs = outputs.split("->")
    return extracted_outputs

def get_big_category_cot(system_prompt, inputs):
    outputs = get_llm_answer(system_prompt, inputs)
    reason, result = outputs.split("출력: ")
    result = result.split("->")
    return result, reason

def get_big_category_self_refine(system_prompt, inputs):
    outputs = get_llm_answer(system_prompt, inputs)
    reason, result = outputs.split("4. 최종 일정 : ")
    result = result.split(" -> ")
    return result, reason


system_prompt_fewshot_1 = """
사용자가 실제 일정을 시작할 시작 시간이 주어지면 당일 22시까지의 일정을 계획할 것입니다.
사용자의 요구사항에 따라 일정을 계획할 것이며, 사용자의 연령대와 성별에 맞게 적절한 코스를 만들어야 합니다.

주어진 카테고리 중 요구 사항에 해당되는 카테고리를 선정하고 순서를 정해주세요.

카테고리 : [{category_list}] 

# 예시 1
- 사용자 요구사항: "부모님 결혼기념일을 맞이해서 어떤 이벤트를 해야할까?"
- 연령대: 50대
- 성별: 혼성
- 일정 시작 시각: 12시
- 답변: 점식식사->카페->공연전시->저녁식사

# 예시 2
- 사용자 요구사항: "여자친구와 100일을 맞이해서 데이트를 할건데 장소좀 추천해줘."
- 연령대: 20대
- 성별: 혼성
- 일정 시작 시각: 14시
- 답변: 카페->체험관광->저녁식사->주점

# 예시 3
- 사용자 요구사항: "기분도 우울한데 꿀꿀함을 달랠 곳 없나?"
- 연령대: 30대
- 성별: 남성
- 일정 시작 시각: 18시
- 답변: 공원->저녁식사->카페

출력 형식을 지키며, 추가적인 설명 없이 카테고리 순서만 생성하세요.
"""

system_prompt_fewshot_2 = """
당신은 사용자의 요구사항을 바탕으로 적절한 카테고리 경로를 생성하는 AI입니다.
사용자의 요구사항을 분석하고, 연령대와 성별을 고려하여 대분류 카테고리 중심의 일정 경로를 생성하세요.

# 규칙
1. 일정 시작 시간부터 최대 22시까지의 일정을 계획하세요.
2. 주어진 카테고리 중, 사용자의 요구에 가장 적합한 카테고리를 선택하고 순서를 정하세요.
3. 연령대 및 성별을 고려하여 적절한 카테고리를 조합하세요.
4. 사용자 요구사항 외에도 추가적으로 추천할 카테고리가 있다면 카테고리 순서에 포함하세요.
5. 출력 형식을 반드시 준수하며, 추가적인 설명 없이 카테고리 순서만 출력하세요.

# 사용 가능한 카테고리
[{category_list}]

# 예시 1
- 사용자 요구사항: 부모님 결혼기념일을 맞이해서 어떤 이벤트를 해야할까?
- 연령대: 50대
- 성별: 혼성
- 일정 시작 시각: 12시
- 답변: 점식식사->카페->공연전시->저녁식사

# 예시 2
- 사용자 요구사항: 여자친구와 100일을 맞이해서 데이트를 할건데 장소좀 추천해줘.
- 연령대: 20대
- 성별: 혼성
- 일정 시작 시각: 14시
- 답변: 카페->체험관광->저녁식사->주점

# 예시 3
- 사용자 요구사항: 기분도 우울한데 꿀꿀함을 달랠 곳 없나?
- 연령대: 30대
- 성별: 남성
- 일정 시작 시각: 18시
- 답변: 공원->저녁식사->카페

이제 위 형식에 맞춰 사용자의 요구사항을 분석하고, 주어진 카테고리 중심의 경로를 생성하세요.
"""

system_prompt_cot_1 = """
당신은 사용자의 요구사항을 바탕으로 최적의 하루 일정을 설계하는 AI입니다.
사용자의 요구사항을 분석한 후, 논리적인 사고 과정을 거쳐 가장 적절한 카테고리 중심의 일정 경로를 생성하세요.

# 규칙
1. 일정 시작 시각부터 최대 22시까지의 일정을 계획하세요.
2. 주어진 카테고리 중, 사용자의 요구사항에 가장 적합한 카테고리를 선택하세요.
3. 연령대 및 성별을 고려하여 자연스러운 일정 흐름을 만들고, 시간이 늦어질수록 저녁에 적합한 활동을 배치하세요.
4. CoT 기법을 적용하여, 단계별 논리적 사고 과정을 포함한 후 최종적으로 카테고리 순서만 출력하세요.

# CoT 사고 과정
1. 사용자의 요구를 분석하여 핵심 키워드 추출
    - 감정 상태(예: 기분이 우울함, 스트레스 해소 필요)
    - 특별한 이벤트(예: 부모님 결혼기념일, 연인과 100일 기념)
    - 선호하는 환경(예: 조용한 곳, 야외 활동)
    - 신체적 제약(예: 휠체어 이용 가능, 거동이 불편함, 알러지)
2. 주어진 카테고리에서 사용자의 요구사항과 가장 잘 맞는 카테고리를 선정
    - [{category_list}] 중에서 적절한 선택
3. 일정 시작 시각을 고려하여 자연스러운 흐름으로 경로를 배치
4. 최종적으로 카테고리 순서만 출력

# 예시 1
- 사용자 요구사항: 부모님 결혼기념일을 맞이해서 어떤 이벤트를 해야 할까?
- 연령대: 50대  
- 성별: 혼성  
- 일정 시작 시각: 12시  
- CoT 사고 과정:  
  1. 부모님이 함께하는 일정이므로, 조용하고 품격 있는 활동이 필요함.  
  2. 점심식사는 한식 또는 전통적인 분위기의 레스토랑이 적합함.  
  3. 식사 후에는 부모님이 즐길 수 있는 문화 활동(전시회, 공연 등)이 적절함.  
  4. 저녁에는 차분한 분위기의 카페에서 대화를 나누는 것이 좋음.  
  5. 마지막으로 저녁 식사는 가족 분위기에 어울리는 정찬 레스토랑이 적합함.  
- 출력: 점심식사->공연전시->카페->저녁식사

# 예시 2
- 사용자 요구사항: 여자친구와 100일을 맞이해서 데이트를 할 건데 장소 좀 추천해줘.  
- 연령대: 20대  
- 성별: 혼성  
- 일정 시작 시각: 14시  
- CoT 사고 과정:  
  1. 연인이 함께하는 기념일이므로, 로맨틱한 분위기가 중요함.  
  2. 오후 일정이므로 가볍게 즐길 수 있는 활동이 먼저 필요함 (카페).  
  3. 이색적인 체험 활동(예: 쿠킹 클래스, 도예 체험)으로 분위기를 더할 수 있음.  
  4. 저녁에는 분위기 좋은 레스토랑에서 식사하며 기념일을 보낼 수 있음.  
  5. 식사 후 분위기를 이어갈 수 있는 주점이 적절함.  
- 출력: 카페->체험관광->저녁식사->주점

# 예시 3
- 사용자 요구사항: 기분이 우울한데 꿀꿀함을 달랠 곳 없나?
- 연령대: 30대  
- 성별: 남성  
- 일정 시작 시각: 18시  
- CoT 사고 과정:  
  1. 우울한 기분을 전환하려면 야외 활동이나 편안한 분위기가 필요함.  
  2. 시간이 저녁이라 낮보다는 야경이 있는 장소나 조용한 산책로가 적절함.  
  3. 기분 전환 후에는 맛있는 저녁식사가 중요함.  
  4. 마지막으로 차분하게 마무리할 수 있는 카페를 선택.  
- 출력: 공원->저녁식사->카페  

이제 위 형식에 맞춰 사용자의 요구사항을 분석하고, 카테고리 중심의 경로를 생성하세요. 
반드시 출력 형식을 지켜주세요.
"""

system_prompt_self_fine_1 = """
당신은 사용자의 요구사항을 분석하여 논리적인 사고 과정을 거쳐 적절한 일정(경로)을 생성하는 AI 입니다.
사용자의 연령대, 성별, 일정 시작 시각을 고려하여 자연스럽고 적절한 카테고리 중심의 일정 경로를 생성하세요.

# 규칙
1. 일정 시작 시각부터 최대 22시까지의 일정을 계획하세요.
2. 주어진 카테고리 중, 사용자의 요구사항에 가장 적합한 카테고리를 선택하세요.
3. 연령대 및 성별을 고려하여 자연스러운 일정 흐름을 만들고, 시간이 늦어질수록 저녁에 적합한 활동을 배치하세요.
4. Self-Refine 기법을 적용하여 일정이 논리적으로 개선되도록 하세요.

# 카테고리 목록
다음으로 주어진 목록에 있는 카테고리만을 이용해서 경로를 생성하세요.
[{category_list}]

# Self-Refine 기법
일정을 생성할 때는 '->'를 이용해서 연결하세요(예: 점심식사 -> 카페 -> 공원)
1. 1차 일정을 생성하세요.
2. 1차 일정의 문제점을 분석하세요. 만약 문제가 없다면 1차 일정을 사용하세요.
3. 분석한 문제점을 기반으로 개선 방향을 제시하세요.
4. 개선 방향을 바탕으로 일정이 보다 자연스럽고, 다양한 요소를 포함하도록 최적화하여 최종 일정을 출력하세요. 단, 너무 많은 일정이 포함되지 않도록 하세요.

# 예시
- 사용자 요구사항: 기분이 우울한데 꿀꿀함을 달랠 곳 없나?
- 연령대: 30대  
- 성별: 남성  
- 일정 시작 시각: 15시  
- Self-Refine 적용:
    1. 1차 일정: 공원->저녁식사->카페
    2. 1차 일정의 문제점 분석:
        - 일정이 너무 단순하여 기분 전환을 위한 요소가 부족함.
        - 사용자가 야외 활동을 원할 가능성이 있으므로, 보다 적극적인 활동 추가 필요.
        - 공원에서 단순 산책보다는 야경을 감상할 수 있는 곳이 더 적절할 수 있음.
    3. 개선 방향:
        - 체험형 활동을 포함하여 감정 전환 요소 강화.
        - 저녁식사 후에도 힐링할 수 있는 활동 추가.
        - 공원 대신 야경 감상이 가능한 장소를 추가. 저녁식사 후에 산책하는 것이 좋을 것 같음.
    4. 최종 일정: 체험관광->저녁식사->카페->공원
"""

fewshot_template = """- 사용자 요구사항: {request}
- 연령대: {age}
- 성별: {gender}
- 일정 시작 시각: {start_time}
- 답변:
"""

cot_template = """- 사용자 요구사항: {request}
- 연령대: {age}
- 성별: {gender}
- 일정 시작 시각: {start_time}
- CoT 사고 과정:
""" 

self_refine_template = """- 사용자 요구사항: {request}
- 연령대: {age}
- 성별: {gender}
- 일정 시작 시각: {start_time}
- Self-Refine 적용:
""" 

def make_category_route(method, data_list, system_prompt, input_template, save_path_list):
    for i, data in enumerate(data_list):
        generated_route = [0] * len(data)
        not_generated_index = list(range(len(data)))   

        try_num = 1
        patient = 0
        while not_generated_index:
            print(f"Start {try_num}")
            new_not_generated_index = []
            for j, row in tqdm(data.iterrows()):
                if j in not_generated_index:
                    result = []
                    try:
                        inputs = input_template.format(
                            request = row['request'],
                            age = row['age'],
                            gender = row['gender'],
                            start_time = row['start_time']
                        )
                        if method == "cot":
                            result = get_big_category_cot(system_prompt, inputs)
                        elif method == 'self_refine':
                            result = get_big_category_self_refine(system_prompt, inputs)
                        else:
                            result = get_big_category_fewshot(system_prompt, inputs)
                    except:
                        pass

                    check = [r for r in result if r in big_category_list]
                    if (len(result) >= 1) and (len(check) == len(result)):
                        generated_route[j] = result
                    else:
                        new_not_generated_index.append(j)
                    time.sleep(2)

            if len(new_not_generated_index) >= len(not_generated_index):
                patient += 1
            else:
                patient = 0
            if patient == 5:
                break

            not_generated_index = new_not_generated_index
            print(f"Done {try_num}: Not generated number {len(not_generated_index)}")
            try_num += 1
        
        data['generated_route'] = generated_route
        data.to_csv(save_path_list[i].format(method=method), index=False)


if __name__ == '__main__':
    place_info = pd.read_csv("../data/concat/place_info.csv")
    place_review = pd.read_csv("../data/concat/place_review.csv")

    # 대분류 리스트
    big_category_list = place_info['main_category'].value_counts().index.tolist()
    # 음식점 -> 점심식사, 저녁식사 두 개의 값으로 변경
    big_category_list = [item if item != "음식점" else "점심식사" for item in big_category_list]
    big_category_list = [val for item in big_category_list for val in (["점심식사", "저녁식사"] if item == "점심식사" else [item])]

    evaluate_origin = pd.read_csv("path_to_origin")
    evaluate_strange = pd.read_csv("path_to_strange")
    evaluate_age = pd.read_csv("path_to_age")
    evaluate_gender = pd.read_csv("path_to_gender")
    data_list = [evaluate_origin, evaluate_strange, evaluate_age, evaluate_gender]
    
    save_path_list = [
        "path_to_origin_{method}",
        "path_to_strange_{method}",
        "path_to_age_{method}",
        "path_to_gender_{method}",
    ]

    system_prompt_list = [system_prompt_fewshot_1,
                          system_prompt_fewshot_2,
                          system_prompt_cot_1,
                          system_prompt_self_fine_1]
    input_template_list = [fewshot_template,
                           fewshot_template,
                           cot_template,
                           self_refine_template]
    
    method_list = ['fewshot_1', 'fewshot_2', 'cot', 'self_refine']

    for i, method in enumerate(method_list):
        make_category_route(method, data_list, system_prompt_list[i], input_template_list[i], save_path_list)

