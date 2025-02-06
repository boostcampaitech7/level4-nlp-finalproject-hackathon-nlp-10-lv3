import pandas as pd
from tqdm import tqdm
import os
import json
import re
from utils.util import CompletionExecutor, read_system_prompt

def parse_evaluation(response_text: str):
    if not response_text or response_text.strip() == "":
        return {
            "coherence_score": None,
            "consistency_score": None,
            "fluency_score": None,
            "relevance_score": None,
            "comments": "응답 없음"
        }

    # 정규식으로 bullet 포맷 파싱
    coherence_match = re.search(r"coherence_score\s*:\s*(\d+)", response_text)
    consistency_match = re.search(r"consistency_score\s*:\s*(\d+)", response_text)
    fluency_match = re.search(r"fluency_score\s*:\s*(\d+)", response_text)
    relevance_match = re.search(r"relevance_score\s*:\s*(\d+)", response_text)
    comments_match = re.search(r"comments\s*:\s*(.*)", response_text)

    result = {
        "coherence_score": int(coherence_match.group(1)) if coherence_match else None,
        "consistency_score": int(consistency_match.group(1)) if consistency_match else None,
        "fluency_score": int(fluency_match.group(1)) if fluency_match else None,
        "relevance_score": int(relevance_match.group(1)) if relevance_match else None,
        "comments": comments_match.group(1).strip() if comments_match else "comments 미검출"
    }

    return result

if __name__ == '__main__':
    # 1) 환경 변수에서 API 키 가져오기
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise EnvironmentError("API_KEY 환경 변수가 설정되지 않았습니다.")

    # 2) CompletionExecutor 인스턴스 생성
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=f'Bearer {api_key}'
    )

    # 3) 파일 경로 설정
    base_dir = os.getcwd()
    prompt_file = os.path.join('prompts', 'eval_summary_prompt.txt')
    data_file = os.path.join('data', 'eval_summary.csv')  # 이미 요약된 데이터
    output_file = os.path.join('data', 'review_evaluation.csv')

    # 4) 시스템 프롬프트 읽기
    system_prompt = read_system_prompt(prompt_file)

    # 5) CSV 파일 로드 (여기에는 원문, 긍정/부정 요약, 전체 요약 컬럼이 있다고 가정)
    #   예: original_reviews, positive_summary, positive_count, negative_summary, negative_count, overall_summary
    df = pd.read_csv(data_file)

    # 평가 결과를 저장할 컬럼 추가
    df['evaluation_result'] = ""

    # 6) 각 행에 대해 평가 요청
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Evaluating Summaries"):
        original_reviews = row.get('reviews', '')
        positive_summary = row.get('pos_review', '')
        positive_count = row.get('pos_cnt', '')
        negative_summary = row.get('neg_review', '')
        negative_count = row.get('neg_cnt', '')
        overall_summary = row.get('review', '')

        # 6-1) user 메시지 생성
        user_prompt = (
            f"Here are the original reviews:\n{original_reviews}\n\n"
            f"Positive summary:\n{positive_summary}\n\n"
            f"Positive count:\n{positive_count}\n\n"
            f"Negative summary:\n{negative_summary}\n\n"
            f"Negative count:\n{negative_count}\n\n"
            f"Overall summary:\n{overall_summary}\n\n"
        )

        # 6-2) 요청 데이터 구성
        request_data = {
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ],
            'topP': 0.7,
            'topK': 0,
            'maxTokens': 500,
            'temperature': 0.5,
            'repeatPenalty': 5,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }

        # 6-3) LLM 호출
        response_text = completion_executor.execute(request_data)

        eval_result = parse_evaluation(response_text)
        df.at[index, 'evaluation_result'] = str(eval_result)

    # 7) 결과 저장
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ 평가 결과 저장 완료: {output_file}")
