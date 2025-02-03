import pandas as pd
from tqdm import tqdm
import os
from utils import CompletionExecutor, read_system_prompt, parse_summary

if __name__ == '__main__':
    # 환경 변수에서 API 키 가져오기
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise EnvironmentError("API_KEY 환경 변수가 설정되지 않았습니다.")

    # CompletionExecutor 인스턴스 생성
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=f'Bearer {api_key}'
    )

    # 디렉토리 및 파일 경로 설정
    base_dir = os.getcwd()
    prompt_file = os.path.join('prompts', 'prompt_summary.txt')
    data_file = os.path.join('data', 'row_review.csv')
    output_file = os.path.join('data', 'review_summary.csv')

    # 시스템 프롬프트 읽기
    system_prompt = read_system_prompt(prompt_file)

    # 데이터프레임 읽기
    df = pd.read_csv(data_file)

    # 리뷰 요약을 위한 빈 컬럼 추가
    df['review_summary'] = ""

    # 각 리뷰에 대해 CompletionExecutor 실행 및 결과 저장
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Reviews"):
        request_data = {
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': row['reviews']
                }
            ],
            'topP': 0.7,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.1,
            'repeatPenalty': 1.2,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }

        # 요청 실행 및 결과 저장
        response_text = completion_executor.execute(request_data)

        # 파싱 적용
        parsed_text, _ = parse_summary(response_text)

        # 결과를 DataFrame에 저장
        df.at[index, 'review_summary'] = parsed_text

    # 최종 데이터프레임 저장
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"📁 요약된 데이터 저장 완료: {output_file}")
