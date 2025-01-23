import requests
import json
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()

class CompletionExecutor:
    def __init__(self, host, api_key):
        self._host = host
        self._api_key = api_key

    def execute(self, completion_request):
        headers = {
            'Authorization': self._api_key,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        response_text = ""

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                           headers=headers, json=completion_request, stream=True) as r:
            if r.status_code == 200:
                for line in r.iter_lines():
                    if line:
                        try:
                            data = line.decode("utf-8").strip()
                            if data.startswith("data:"):
                                message_data = data[5:].strip()
                                if message_data == "[DONE]":
                                    break
                                
                                token_data = json.loads(message_data)
                                content = token_data.get("message", {}).get("content", "")
                                response_text += content  
                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
                        except Exception as e:
                            print(f"Error decoding line: {line} - {e}")
            else:
                print(f"Error: {r.status_code}, {r.text}")

        return response_text

def read_system_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

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

    # 디렉토리와 파일 경로 설정
    base_dir = os.getcwd()
    prompt_file = os.path.join('prompts', 'prompt_summary.txt')
    data_file = os.path.join('data', 'agsdrasgdfsadfg.csv')

    # 시스템 프롬프트 읽기
    system_prompt = read_system_prompt(prompt_file)

    # 데이터프레임 읽기
    df = pd.read_csv(data_file)

    # 리뷰 요약을 위한 빈 컬럼 추가
    df['리뷰요약'] = ""

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
                    'content': row['리뷰']
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
        df.at[index, '리뷰요약'] = response_text.split('가게 특성 요약:')[-1].strip()


