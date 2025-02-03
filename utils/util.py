import requests
import json
import re
import time
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class CompletionExecutor:
    def __init__(self, host, api_key):
        self._host = host
        self._api_key = api_key

    def execute(self, completion_request, retries=3, wait_time=5):
        """API 요청을 실행하고, 실패 시 최대 3번 재시도"""
        headers = {
            'Authorization': self._api_key,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        for attempt in range(retries):
            response_text = ""
            try:
                with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                                   headers=headers, json=completion_request, stream=True, timeout=30) as r:
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
                        response_text = None

                if response_text:
                    return response_text  # 정상 응답이면 반환
                
                print(f"⚠️ API 요청 실패 (시도 {attempt + 1}/{retries}) - {r.status_code}")
                time.sleep(wait_time)  # 재시도 전 대기

            except requests.RequestException as e:
                print(f"Network Error: {e} (시도 {attempt + 1}/{retries})")
                time.sleep(wait_time)

        return "API 응답 실패 - 요약 생성 불가"  # 모든 재시도 후에도 실패 시 기본 메시지 반환

def read_system_prompt(file_path):
    """시스템 프롬프트 파일을 읽어서 반환"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

def parse_summary(response_text):
    """요약된 텍스트에서 필요한 부분만 추출하여 정제"""
    if not response_text or response_text.strip() == "":
        return "요약 없음", "분위기 정보 없음"

    parts = response_text.split("요약 정보")
    cleaned_text = "요약 정보" + parts[1] if len(parts) > 2 else response_text

    atmosphere_match = re.search(r"\*\*분위기 선택\*\*\n\n- (.+)", cleaned_text)
    atmosphere = atmosphere_match.group(1).strip() if atmosphere_match else "분위기 정보 없음"

    return cleaned_text, atmosphere
