import openai
import nltk
import re
import time
from collections import Counter

# NLTK 문장 분리를 위한 패키지 다운로드
nltk.download('punkt')
nltk.download('punkt_tab')
# OpenAI API 키 설정
openai.api_key = "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"

# 감성 분석 함수 (긍정/부정 판별)
def analyze_sentiment(text):
    prompt = f"다음 음식점 리뷰 문장의 감성을 분석해주세요. 긍정이면 'positive', 부정이면 'negative'만 출력하세요:\n{text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0
    )
    
    sentiment = response["choices"][0]["message"]["content"].strip().lower()
    return sentiment

# 요약에서 핵심 키워드 추출
def extract_keywords(summary):
    prompt = f"다음 요약문에서 핵심 키워드를 추출해주세요. 쉼표로 구분하여 출력하세요:\n{summary}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0
    )
    
    keywords = response["choices"][0]["message"]["content"].strip().lower()
    keywords = [kw.strip() for kw in keywords.split(",")]
    return keywords

# 리뷰 데이터에서 키워드 등장 여부 확인
def keyword_match_score(reviews, keywords):
    review_text = " ".join(reviews).lower()  # 모든 리뷰를 하나의 텍스트로 합치고 소문자로 변환
    matched_keywords = [kw for kw in keywords if kw in review_text]  # 리뷰에서 등장하는 키워드 추출
    unmatched_keywords = [kw for kw in keywords if kw not in review_text]  # 리뷰에 없는 키워드 찾기
    match_ratio = len(matched_keywords) / len(keywords) if keywords else 0  # 일치율 계산
    
    return {
        "keywords": keywords,
        "matched_keywords": matched_keywords,
        "unmatched_keywords": unmatched_keywords,
        "match_ratio": match_ratio
    }

# 리뷰 데이터를 문장 단위로 분석하는 함수
def analyze_reviews(reviews):
    sentiments = []
    
    for review in reviews:
        sentences = nltk.sent_tokenize(review)  # 문장 분리
        
        for sentence in sentences:
            sentiment = analyze_sentiment(sentence)
            sentiments.append(sentiment)
            time.sleep(0.5)  # API 호출 간격 조절 (속도 제한 방지)

    # 긍정 / 부정 비율 계산
    positive_count = sentiments.count("positive")
    negative_count = sentiments.count("negative")
    total_count = len(sentiments)
    
    positive_ratio = positive_count / total_count if total_count > 0 else 0
    negative_ratio = negative_count / total_count if total_count > 0 else 0
    
    return positive_ratio, negative_ratio

# 요약 결과의 감성 분석
def analyze_summary(summary):
    return analyze_sentiment(summary)

# 최종 평가 함수
def evaluate_summary(reviews, summary):
    # 감성 분석
    positive_ratio, negative_ratio = analyze_reviews(reviews)
    summary_sentiment = analyze_summary(summary)
    
    # 지배적인 감성 판단
    dominant_sentiment = "positive" if positive_ratio >= negative_ratio else "negative"
    
    # 감성 평가 (1: 일치, 0: 불일치)
    sentiment_evaluation = 1 if summary_sentiment == dominant_sentiment else 0
    
    # 키워드 분석
    keywords_info = keyword_match_score(reviews, extract_keywords(summary))
    
    return {
        "positive_ratio": positive_ratio,
        "negative_ratio": negative_ratio,
        "summary_sentiment": summary_sentiment,
        "dominant_sentiment": dominant_sentiment,
        "sentiment_evaluation": sentiment_evaluation,
        "keywords": keywords_info["keywords"],
        "matched_keywords": keywords_info["matched_keywords"],
        "unmatched_keywords": keywords_info["unmatched_keywords"],
        "match_ratio": keywords_info["match_ratio"]
    }


reviews = [
    "음식이 정말 맛있었어요! 서비스도 훌륭했습니다.",
    "분위기는 괜찮았지만, 음식이 너무 짜서 별로였어요.",
    "최악의 경험이었어요. 음식도 차갑고 직원들도 불친절했습니다.",
    "가격이 조금 비싸긴 하지만, 음식이 정성스럽게 나와서 만족스러웠어요.",
    "한 시간 넘게 기다렸어요. 다시는 안 올 것 같아요."
]


summary = "음식은 대체로 만족스럽지만, 서비스 속도에 대한 불만이 있습니다."


result = evaluate_summary(reviews, summary)
print(result)
