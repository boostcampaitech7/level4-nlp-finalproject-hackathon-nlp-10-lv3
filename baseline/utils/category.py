import re
from typing import List, Dict, Tuple
import pandas as pd

class Category:
    
    def __init__(self, chatModel, data_path: str, extract_symbol="$%^&"):
        self.chatModel = chatModel

        place_info = pd.read_csv(data_path)
        # 대분류 리스트
        self.big_category_list = place_info['main_category'].value_counts().index.tolist()
        # 음식점 -> 점심식사, 저녁식사 두 개의 값으로 변경
        self.big_category_list = [item if item != "음식점" else "점심식사" for item in self.big_category_list]
        self.big_category_list = [val for item in self.big_category_list for val in (["점심식사", "저녁식사"] if item == "점심식사" else [item])]

        # 각 대분류에 따른 소분류 목록(dict)
        self.small_category_dict = {}
        for big_category in self.big_category_list:
            if (big_category == "점심식사") or (big_category == "저녁식사"):
                self.small_category_dict[big_category] = place_info[place_info['main_category'] == "음식점"]['category'].value_counts().index.tolist()
            else:
                self.small_category_dict[big_category] = place_info[place_info['main_category'] == big_category]['category'].value_counts().index.tolist()

        self.extract_symbol = extract_symbol
        self.escaped_symbol = re.escape(self.extract_symbol)  # 정규식에서 안전하게 사용하도록 변환

    def get_big_category(self, input_dict: dict) -> List[str]:
        system_prompt = f"""
        사용자가 실제 일정을 시작할 시작 시간이 주어지면 당일 22시까지의 일정을 계획할 것입니다.
        사용자의 요구사항에 따라 일정을 계획할 것이며, 사용자의 연령대와 성별에 맞게 적절한 코스를 만들어야 합니다.

        주어진 카테고리 중 요구 사항에 해당되는 카테고리를 선정하고 순서를 정해주세요.

        카테고리 : [{", ".join(self.big_category_list)}] 

        # 예시 1
        - 사용자 요구사항: "부모님 결혼기념일을 맞이해서 어떤 이벤트를 해야할까?"
        - 연령대: 50대
        - 성별: 혼성
        - 일정 시작 시각: 12시
        - 답변: {self.extract_symbol}점식식사->카페->공연전시->저녁식사{self.extract_symbol}

        # 예시 2
        - 사용자 요구사항: "여자친구와 100일을 맞이해서 데이트를 할건데 장소좀 추천해줘."
        - 연령대: 20대
        - 성별: 혼성
        - 일정 시작 시각: 14시
        - 답변: {self.extract_symbol}카페->체험관광->저녁식사->주점{self.extract_symbol}

        # 예시 3
        - 사용자 요구사항: "기분도 우울한데 꿀꿀함을 달랠 곳 없나?"
        - 연령대: 30대
        - 성별: 남성
        - 일정 시작 시각: 18시
        - 답변: {self.extract_symbol}피크닉->저녁식사->카페{self.extract_symbol}
        """
        
        inputs = f"""
        - 사용자 요구사항: {input_dict['request']}
        - 연령대: {input_dict['age']}
        - 성별: {input_dict['sex']}
        - 일정 시작 시각: {input_dict['start_time']}
        - 답변:
        """

        outputs = ""
        extracted_outputs = []
        while (not outputs) or (not extracted_outputs):
            outputs = self.chatModel.get_answer(system_prompt, inputs)
            match = re.search(fr'{self.escaped_symbol}(.*?){self.escaped_symbol}', outputs)
            try:
                extracted_outputs = match.group(1).split("->")
            except:
                pass
        
        return extracted_outputs


    def get_small_category(self, choosed_big_category_list: List[str], input_dict: Dict[str, str]) -> List[Tuple[str, List[str]]]:
        system_prompt = f"""
        사용자의 요구사항에 맞게 대분류로 일정을 계획했습니다. 대분류 중에서도 요구사항에 맞는 소분류가 있는지 확인해주세요.

        사용자의 요구사항, 대분류, 대분류에 따른 소분류가 들어오면 적절한 소분류를 선택해주세요.
        해당 대분류는 전체 일정 중 일부분에 해당됩니다.

        특별한 요구사항이 없다면 '해당없음'을 선택하세요.

        # 예시 1
        - 사용자 요구사항: "여자친구랑 100일 기념으로 데이트를 할건데 코스 좀 추천해줘. 여자친구가 걷는걸 좋아해."
        - 연령대: 20대
        - 성별: 혼성
        - 일정 시작 시각: 15시
        - 대분류: 공원
        - 소분류: ['해당없음', '근린공원', '도시,테마공원', '산책로', '공원']
        - 선택된 소분류: {self.extract_symbol}'산책로', '공원'{self.extract_symbol}

        # 예시 2
        - 사용자 요구사항: "기분도 꿀꿀한데 달달한 디저트가 먹고 싶어." 
        - 연령대: 30대
        - 성별: 여성
        - 일정 시작 시각: 17시
        - 대분류: 카페
        - 소분류: ['해당없음', '카페,디저트', '카페', '차', '아이스크림', '테이크아웃커피', '한방카페', '과일,주스전문점', '바나프레소', '떡카페', '와플', '초콜릿전문점', '케이크전문', '차,커피', '호떡', '블루보틀', '빙수', '룸카페', '다방', '도넛']
        - 선택된 소분류: {self.extract_symbol}'카페,디저트', '아이스크림', '와플', '초콜릿전문점', '케이크전문', '빙수', '도넛'{self.extract_symbol}

        # 예시 3
        - 사용자 요구사항: "오늘 나 불태울거야. 술집 좀 추천해줘." 
        - 연령대: 20대
        - 성별: 남성
        - 일정 시작 시각: 19시
        - 대분류: 주점
        - 소분류: ['해당없음', '맥주,호프', '요리주점', '바(BAR)', '이자카야', '와인', '포장마차', '술집', '라이브카페', '슈퍼,마트', '유흥주점']
        - 선택된 소분류: {self.extract_symbol}'해당없음'{self.extract_symbol}
        """
        
        input_format = """
        - 사용자 요구사항: "{}"
        - 연령대: {}
        - 성별: {}
        - 일정 시작 시각: {}
        - 대분류: {}
        - 소분류: {}
        - 선택된 소분류:
        """

        results = []
        for big_category in choosed_big_category_list:
            inputs = input_format.format(input_dict['request'],
                                        input_dict['age'],
                                        input_dict['sex'],
                                        input_dict['start_time'],
                                        big_category,
                                        self.small_category_dict[big_category])
            outputs = ""
            extracted_outputs = ""
            while (not outputs) or (not extracted_outputs):
                outputs = self.chatModel.get_answer(system_prompt, inputs)
                match = re.search(fr'{self.escaped_symbol}(.*?){self.escaped_symbol}', outputs)
                try:
                    extracted_outputs = match.group(1).split(", ")
                    extracted_outputs = [o.split("'")[1] for o in extracted_outputs]
                except:
                    pass
            
            if (big_category == "점심식사") or (big_category == "저녁식사"):
                results.append(("음식점", extracted_outputs))
            else:
                results.append((big_category, extracted_outputs))

        return results