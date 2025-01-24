'''
<예상 데이터 형태>

C : 장소 - 요약문
Q : 사용자 질문(분위시)
A : 해당하는 요약문들과 거기에 해당하는 장소들


'''
'''
<평가 지표>
HIT RATE :
MRR
Precision
Recall

'''
'''
리트리버 결과
정답값
쿼리


'''

def hit_rate(retrieved_docs, relevant_docs, k) : 
    '''
    args : 
        retrieved_docs : 모든 쿼리에 대한 리트리버 검색 결과 문서 집합
        relevant_docs : 모든 쿼리에 대한 정답 문서 집합
        k : TOP k 개
    
    returns :
        hit_rate_k : 각 쿼리에 해당하는 관련 문서 포함 여부의 전체 쿼리에서의 확률. 높아야 좋음

    
    '''
    query_hit = []  # 0,1,0,1,1,1 ...

    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        top_k_docs = retrieved[:k]
        hit = 0
        for doc in relevant:
            if doc in top_k_docs:
                hit = 1
                break

        query_hit.append(hit)
        
    
    
    hit_rate_k = sum(query_hit) / len(query_hit)
    
    return hit_rate_k
        
def mean_reciprocal_rank(retrieved_docs, relevant_docs) :
    """
    기능 : 
    args : 
        retrieved_docs : 모든 쿼리에 대한 리트리버 검색 결과 문서 집합
        relevant_docs : 모든 쿼리에 대한 정답 문서 집합
    :return:
        total_mrr_score : 스코어
    """
    rank_list = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):

                
        for rank, doc in enumerate(retrieved, start=1):
            if doc in relevant:
                rank_list.append( 1 / rank )
                break
    mrr_score = sum(rank_list) /  len(retrieved_docs)
    return mrr_score

def main(): 
    # 코드 테스트 예시
    retrieved_docs = [
        ["AI 기술이 발전하는 이유는 무엇인가요?", "AI 기술의 혁신적 변화", "AI 발전의 역사"],
        ["2025년 AI 트렌드는 어떤 것들이 있을까요?", "AI의 미래", "AI 기술 전망"],
        ["자율주행차의 발전과 미래 예측", "자율주행차 기술", "자율주행차의 현황"]
    ]
    
    relevant_docs = [
        ["AI 기술의 발전, 이유", "AI 기술의 혁신적 변화"],
        ["2025년 AI 기술 트렌드", "AI의 미래"],
        ["자율주행차의 발전과 미래 예측"]
    ]
    
    
    
    
    k = 2 #사용시 수정

    hit_rate_k = hit_rate(retrieved_docs, relevant_docs, k)
    mrr_value = mean_reciprocal_rank(retrieved_docs, relevant_docs)
    
    print(f"Hit Rate@{k}: {hit_rate_k:.2f}")
    print(f"MRR: {mrr_value}")
    

if __name__ == "__main__":
    main()