import requests
from PIL import Image

import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration

model_id = "beomi/Llama-3-KoEn-8B-xtuner-llava-preview"

model = LlavaForConditionalGeneration.from_pretrained(
    model_id, 
    torch_dtype='auto', 
    device_map='auto',
    revision='a38aac3', # 'a38aac3' for basic ChatVector, '4f04d1e' for Model diff based merging(ref. https://huggingface.co/blog/maywell/llm-feature-transfer)
)

processor = AutoProcessor.from_pretrained(model_id)

tokenizer = processor.tokenizer
# terminators = [
#     tokenizer.eos_token_id,
#     tokenizer.convert_tokens_to_ids("<|eot_id|>")
# ]
eos_token_id = tokenizer.eos_token_id
eot_token_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")

p = '''
### 작업 설명:
당신은 이미지를 분석하여 분위기를 분류할 수 있는 **비전-언어 모델(VLM)**입니다.  
주어진 이미지를 분석하여 20가지 미리 정의된 분위기 중 **가장 적절한 3가지 분위기**를 선택하세요.  

---

### **가능한 분위기 유형 (20가지)**
1. 감성적인 분위기
2. 레트로한 분위기
3. 신나는 분위기
4. 차분한 분위기
5. 고급스러운 분위기
6. 아늑한 분위기
7. 모던한 분위기
8. 자연 친화적인 분위기
9. 이국적인 분위기
10. 로맨틱한 분위기
11. 예술적인 분위기
12. 활기찬 분위기
13. 웅장한 분위기
14. 신비로운 분위기
15. 따뜻한 분위기
16. 청량한 분위기
17. 고요한 분위기
18. 어두운 분위기
19. 쾌적한 분위기
20. 잔잔한 분위기  

---

### **단계별 분석 (CoT 방식)**
1. **핵심 시각 요소 분석:**  
   - 조명 (밝음/어두움, 색온도)  
   - 색감 (따뜻한 색조, 차가운 색조, 단색 vs 다채로운 색)  
   - 주요 사물 및 배경 요소 (빈티지 가구, 자연 요소, 네온사인 등)  
   - 사람의 행동 및 분위기 (활기참, 고요함, 친근함 등)  

2. **감정적 영향 분석:**  
   - 해당 이미지가 전달하는 감정적 분위기 식별  
   - 편안함, 흥분, 향수, 고요함 등의 감정 요소 평가  

3. **최적의 분위기 유형 매칭:**  
   - 위의 분석을 바탕으로 20가지 분위기 중 가장 적절한 **3가지 분위기**를 선정  
   - 분위기 선택의 근거를 간략히 설명  

---

### **Few-shot 예시**
#### **예시 1: 복고풍 바**
##### **입력 이미지:**  
어두운 조명, 빈티지 가구, 네온사인, 오래된 주크박스가 있는 바  
##### **분석:**  
조명이 어둡고 따뜻한 색조로 향수를 불러일으키는 분위기를 형성함.  
빈티지 가구와 주크박스는 **레트로 감성**을 강조하며, 네온사인은 **신비로운 느낌**을 더함.  
##### **출력:**  
%^&레트로한 분위기, 신비로운 분위기, 어두운 분위기%^&  

---

#### **예시 2: 감성적인 카페**
##### **입력 이미지:**  
부드러운 파스텔톤, 나무 테이블, 전구 장식이 있는 밝은 카페  
##### **분석:**  
따뜻한 색감과 전구 조명이 **감성적인 분위기**를 형성함.  
나무 소재와 조용한 배경이 **아늑한 느낌**을 제공.  
##### **출력:**  
%^&감성적인 분위기, 아늑한 분위기, 차분한 분위기%^&  

---

#### **예시 3: 열대 해변**
##### **입력 이미지:**  
맑은 하늘, 야자수, 형형색색의 칵테일, 푸른 바다  
##### **분석:**  
밝은 자연광과 푸른 바다 색상이 **청량한 분위기**를 강조함.  
야자수와 칵테일이 조화를 이루어 **이국적인 느낌**을 줌.  
##### **출력:**  
%^&청량한 분위기, 이국적인 분위기, 활기찬 분위기%^&  

---

### **당신의 작업:**
주어진 이미지를 분석하여 위의 단계별 과정을 따르세요.  
20가지 분위기 중 **가장 적절한 3가지 분위기**를 선택하세요.  
최종적으로 아래 형식으로 결과를 출력하세요:  

```plaintext
%^&[분위기1, 분위기2, 분위기3]%^&


'''


prompt = (
    "<|start_header_id|>user<|end_header_id|>\n\n"
    "<image>\n"
    f"{p}"  
    "<|eot_id|>\n"
    "<|start_header_id|>assistant<|end_header_id|>\n\n"
)

# image_file = Image.open('/data/ephemeral/home/gyeom/data')

image_path = "/data/ephemeral/home/gyeom/data/test.jpg"
raw_image = Image.open(image_path).convert("RGB")

inputs = processor(prompt, images=raw_image, return_tensors="pt").to("cuda", torch.float16)


output = model.generate(
    **inputs,
    max_new_tokens=100,  # 지나치게 긴 출력을 방지
    do_sample=False,  # 불필요한 랜덤성 제거 (일관된 출력 보장)
    eos_token_id=eos_token_id,  # 단일 EOS 토큰 ID 사용
    pad_token_id=eos_token_id  # pad_token_id 설정
)

print(raw_image)
print(processor.decode(output[0][2:], skip_special_tokens=False))
