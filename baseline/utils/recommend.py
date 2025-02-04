system_prompt = """
당신은 사용자의 요구사항과 후보 장소 정보를 분석해 최적의 장소를 추천하는 전문가입니다.  
다음 규칙에 따라 장소를 선택하고 이유를 설명하세요:

1. **요구사항과 리뷰 유사성 분석**  
   - 사용자의 요구사항과 후보 장소의 리뷰를 비교해 가장 유사한 장소를 선정합니다.  
   - 예: "조용한 카페" 요구 → 리뷰에 "조용함"이 강조된 장소 우선.

2. **거리와 소요시간 최소화**  
   - 유사성 수준이 비슷한 경우, 거리와 소요시간이 더 적은 장소를 선택합니다.

3. **선택 이유 명확히 설명**  
   - 최종 선택 이유를 "요구사항 부합"과 "접근성" 두 가지 측면에서 설명합니다.  
   - 예: "A 장소는 사용자의 요구사항과 리뷰가 가장 유사하며, 거리도 가장 가깝습니다."

[출력 형식]  
- 추천 장소: [장소명]  
- 선택 이유:  
  1. 요구사항 부합: [요구사항과 리뷰의 유사성 설명]  
  2. 접근성: [거리/소요시간 비교]  
  
====================================================================================

현재 위치: 서울시 마포구 연남동  
요구사항: "넓은 야외 공간과 강아지 동반 가능한 카페"  

후보 장소:  
1. **카페 포근**  
   - 소요시간: 12분  
   - 거리: 600m  
   - 리뷰: "야외 테라스가 넓고 강아지 전용 메뉴가 있습니다."  

2. **카페 휴식**  
   - 소요시간: 8분  
   - 거리: 400m  
   - 리뷰: "실내는 좁지만 야외 공간이 있고 강아지 출입 가능."  

3. **카페 그린**  
   - 소요시간: 15분  
   - 거리: 1km  
   - 리뷰: "야외 정원이 아름답고 강아지 동반 시 특별 할인 제공."  

위 조건에 따라 추천할 장소를 선택하고 이유를 설명해 주세요.
"""

class Recommend():
   def __init__(self, model):
      self.model=model
   
   def generate_prompt(current_location, requirements, candidates):
      user_prompt_template = f"""
      현재 위치: {current_location}  
      요구사항: {requirements}  
      후보 장소:
      """
      for i, candidate in enumerate(candidates, start=1):
         user_prompt_template += f"""
         {i}. {candidate['name']}  
         - 소요시간: {candidate['time']}  
         - 거리: {candidate['distance']}  
         - 리뷰: {candidate['rating']}  
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

   def invoke_message(self, user_prompt):
      messages = self.get_template_message(system_prompt, user_prompt)
      response = self.model.invoke(messages)
      return response

   def parsing_message(self, response):
      