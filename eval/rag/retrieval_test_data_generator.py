import openai 
import csv
import re
# OpenAI API 키 설정
openai.api_key = "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"


# 요약문 리스트
summaries = [
    '''해당 가게는 맛있는 감자탕과 백반을 제공하며, 
    신선한 고기와 깔끔한 국물로 인기가 있습니다. 
    사장님과 직원들은 친절하며, 편안한 분위기에서 식사를 즐길 수 있습니다.
    다른 메뉴들도 맛있다는 평가가 있어 다양한 음식을 시도해 볼 만 합니다. 
    또한, 저녁에는 삼겹살도 많이 주문한다고 하니 참고 바랍니다. 
    전체적으로 깔끔하고 맛있는 한식 맛집으로 추천할 만 합니다.'''
]

# 결과 저장 리스트
qa_dataset = []

for summary in summaries:
    # 프롬프트 생성
    prompt = f"""
    다음 요약문을 기반으로 3개의 질문을 생성하세요.
    
    질문은 맛집이 찾기나 코스를 짜는 사람이라고 생각하고 만들어줘. 어디를 갈지는 몰라
    
    [질문 예시]
    1. 질문: "편안한 분위기에서 시사를 할 수 있는 곳을 추천해줘"
    2. 질문: "감자탕 맛있는 집 알려줘"
    2. 질문: "식도락 여행을 떠날 건데, 코스를 만들어줘"
    
    
    각 질문에 그렇게 생성한 이유를 요약문 기반으로 말해줘
    
    [요약문:] {summary}

    [결과 형식:]
    1. 질문: [질문1]
        이유 : [이유1]
    2. 질문: [질문2]
        이유 : [이유2]
    3. 질문: [질문3]
        이유 : [이유3]
    """
    # GPT 호출

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you are the assistant that make question from review data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
        
        # GPT 응답 처리
    output = response["choices"][0]["message"]["content"]
    print(response["choices"][0]["message"]["content"])    
        # 질문과 답변 분리
    qa_pairs = output.strip().split("\n")
    for i in range(0, len(qa_pairs), 2):  # 질문과 답변은 두 줄씩 구성됨
        question = qa_pairs[i].replace("질문: ", "").strip()
        text = re.sub(r'\s+', ' ', summary.replace('\n', ' '))
        text = text.replace(',', '')
        qa_dataset.append({"question": question, "answer": text })

    # CSV 파일로 저장
    csv_filename = "qa_dataset_3_per_summary.csv"
    with open(csv_filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["summary", "question", "answer"])
        writer.writeheader()
        writer.writerows(qa_dataset)

    print(f"QA 데이터셋 저장 완료: {csv_filename}")
