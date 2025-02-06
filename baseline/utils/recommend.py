import re
system_prompt = """
당신은 사용자의 요구사항과 후보 장소 정보를 분석해 최적의 장소를 추천하는 전문가입니다.  
다음 규칙과 예시를 참고하여 장소를 선택하고 이유를 설명하세요:
[규칙]  
1. **요구사항과 리뷰 유사성**을 최우선으로 평가합니다.  
2. 유사성이 비슷하면 **거리/소요시간이 적은 장소**를 선택합니다.  
3. 선택 이유는 "요구사항 부합"과 "접근성"으로 구분해 설명합니다.
[예시 1]  
사용자 입력:  
- 현재 위치: 서울시 강남구  
- 요구사항: "조용한 카페에서 작업"  
- 후보 장소:  
  1. 카페 A (id 5234, 소요시간 5분, 거리 300m, 리뷰: "작업하기 좋은 조용한 분위기")  
  2. 카페 B (id 142, 소요시간 3분, 거리 200m, 리뷰: "사람이 많아 시끄러움")  
출력:  
추천 장소: 카페 A  (id 5234)
선택 이유:  
1. 요구사항 부합: "조용한 카페" 요구에 맞춰 리뷰에서 "조용한 분위기"가 강조된 카페 A 선택.  
2. 접근성: 카페 B보다 거리는 100m 더 멀지만, 요구사항 충족도가 높습니다.  
--- 
[예시 2]  
사용자 입력:  
- 현재 위치: 서울시 서초구  
- 요구사항: "강아지와 함께 갈 수 있는 레스토랑"  
- 후보 장소:  
  1. 레스토랑 X (id 13, 소요시간 10분, 거리 500m, 리뷰: "펫 프렌들리, 야외 좌석 제공")  
  2. 레스토랑 Y (id 780, 소요시간 8분, 거리 400m, 리뷰: "강아지 동반 불가")  
출력:  
추천 장소: 레스토랑 X  (id 13)
선택 이유:  
1. 요구사항 부합: "강아지 동반 가능" 조건을 만족하는 유일한 장소입니다.  
2. 접근성: 거리 500m로 접근성은 다소 떨어지지만, 요구사항 필수 조건을 충족합니다.  
--- 
[예시 3]  
사용자 입력:  
- 현재 위치: 서울시 종로구  
- 요구사항: "비오는 날 가기 좋은 실내 북카페"  
- 후보 장소:  
  1. 북카페 M (id 991, 소요시간 7분, 거리 350m, 리뷰: "창가 자리가 비 올 때 분위기 좋음")  
  2. 북카페 N (id 797소요시간 6분, 거리 300m, 리뷰: "좌석이 협소하고 창문 없음")  
출력:  
추천 장소: 북카페 M (991)
선택 이유:  
1. 요구사항 부합: "비오는 날 분위기 좋은 실내" 조건에 맞는 리뷰를 가진 북카페 M 선택.  
2. 접근성: 거리 350m로 차이는 미미하며, 요구사항 충족도가 더 높습니다.  
---
"""

class Recommend():
   def __init__(self, model):
      self.model=model
      
   def generate_prompt(self, current_location, requirements, candidates):
      user_prompt_template = f"""
      현재 위치: {current_location}  
      요구사항: {requirements}  
      후보 장소:
      """
      for i, candidate in enumerate(candidates, start=1):
         user_prompt_template += f"""
         {i}. {candidate['name']} (id : {candidate["id"]})  
         - 소요시간: {candidate['time']}  
         - 거리: {candidate['distance']}  
         - 리뷰: {candidate['text']}  
      """
      user_prompt_template += "\n추천할 장소를 선택하고 이유를 설명해 주세요."
      return user_prompt_template

   def get_template_message(self, system_prompt, user_prompt):
      messages = [
         (
            "system",
            system_prompt
         ),
         (
            "human",
            user_prompt
         )
      ]
      return messages

   def invoke(self, user_prompt):
      messages = self.get_template_message(system_prompt, user_prompt)
      response = self.model.invoke_message(messages)
      return response

   def parse_output(self, text):
      
      pattern = r"추천 장소\s*:\s*(.+?)\s*\(id\s*:\s*(\d+)\)\n선택 이유:\n\s*1\. 요구사항 부합:\s*(.+?)\n\s*2\. 접근성:\s*(.+)"
    
      match = re.search(pattern, text, re.DOTALL)

      if match:
         return {
            "recommend_place": match.group(1).strip(),
            "id": match.group(2).strip(),
            "requirements_match": match.group(3).strip(),
            "access": match.group(4).strip()
         }
      return None