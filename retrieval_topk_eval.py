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
    기능 : 전체 검색된 쿼리의 의도에 맞는 문서가 검색된 K개의 요약문이 얼마나 뽑혔나 확인
    args : 
        retrieved_docs : 모든 쿼리에 대한 리트리버 검색 결과 문서 집합
        relevant_docs : 모든 쿼리에 대한 정답 문서 집합
        k : TOP k 개
    
    returns :
        hit_rate_k : hit_k에 대한 평균

    
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
        
def mean_reciprocal_rank(retrieved_docs, relevant_docs, k) :
    """
    기능 : 검색된 문서 중 처음 등장하는 관련 요약의 순위 기반 평가
    args : 
        retrieved_docs : 모든 쿼리에 대한 리트리버 검색 결과 문서 집합
        relevant_docs : 모든 쿼리에 대한 정답 문서 집합
    :return
        total_mrr_score : mrr_score에 대한 쳥균
    """
    rank_list = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        top_k_docs = retrieved[:k]  
        for rank, doc in enumerate(top_k_docs, start=1):
            if doc in relevant:
                rank_list.append( 1 / rank )
                break
    mrr_score = sum(rank_list) /  len(retrieved_docs)
    return mrr_score


def precision(retrieved_docs, relevant_docs, k):
    """
    기능 : 정밀도. 검색된 요약 중 실제 관련 요약 비율

    args :
        retrieved_docs : 모든 쿼리에 대한 리트리버 검색 결과 문서 집합
        relevant_docs : 모든 쿼리에 대한 정답 문서 집합
        k: Top-k
    return: 
        precision_score : precision에 대한 평균
    """
    total_precision = 0
    num_queries = len(retrieved_docs)

    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        relevant_in_top_k = sum(1 for doc in retrieved[:k] if doc in relevant)
        total_precision += relevant_in_top_k / k

    precision_score = total_precision / num_queries
    return precision_score


def recall_at_k(retrieved_docs, relevant_docs, k):
    """
    기능 : 전체 관련 문서 중에서 실제로 검색된 문서의 비율

    args :
    
        retrieved_docs : 모든 쿼리에 대한 리트리버 검색 결과 문서 집합
        relevant_docs : 모든 쿼리에 대한 정답 문서 집합
        k: Recall@k에서 k 값.
    return: 
        recall_score : 평균
    """
    total_recall = 0
    num_queries = len(retrieved_docs)

    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        relevant_in_top_k = sum(1 for doc in retrieved[:k] if doc in relevant)
        total_recall += relevant_in_top_k / len(relevant)
    recall_score = total_recall / num_queries

    return recall_score


def main(): 
    # 코드 테스트 예시
    #retrieval answer
    retrieved_docs = [
        ["AI 기술이 발전하는 이유는 무엇인가요?", "AI 기술의 혁신적 변화", "AI 발전의 역사"],
        ["2025년 AI 트렌드는 어떤 것들이 있을까요?", "AI의 미래", "AI 기술 전망"],
        ["자율주행차의 발전과 미래 예측", "자율주행차 기술", "자율주행차의 현황"]
    ]
    
    # Test data answer
    relevant_docs = [
        ["AI 기술의 발전, 이유", "AI 기술의 혁신적 변화"],
        ["2025년 AI 기술 트렌드", "AI의 미래"],
        ["자율주행차의 발전과 미래 예측"]
    ]
    
    
    
    
    k = 2 #사용시 수정

    hit_rate_k = hit_rate(retrieved_docs, relevant_docs, k)
    mrr_value = mean_reciprocal_rank(retrieved_docs, relevant_docs, k)
    precision_k = precision(retrieved_docs, relevant_docs, k)
    recall_k = recall_at_k(retrieved_docs, relevant_docs, k)
    
    print(f"Hit Rate@{k}: {hit_rate_k:.2f}")
    print(f"MRR@{k}: {mrr_value}")
    print(f"Precision@{k}: {precision_k:.2f}")    
    print(f"Recall@{k}: {recall_k:.2f}")
    
if __name__ == "__main__":
    main()