import os
import pickle
import argparse

from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker
from langchain_community.embeddings import ClovaXEmbeddings

def main(arg):
    ## Arguments
    w = arg.weigth
    k = arg.top_k

    ## Inputs
    query = "어버이날에 부모님과 함께 할 수 있는 코스를 생성해줘"
    categories = ["식당", "카페", "전시/관람"] ## user query 기반으로 선택된 categories

    ## Loda DB
    URI = os.path.join("data", "dense_recommendation.db")
    client = MilvusClient(URI)

    ## Embeddings
    ### Load dense embedding
    dense_embedding = ClovaXEmbeddings(model="clir-emb-dolphin")

    ### Load sparse embedding
    EMBEDDING_PATH = os.path.join("model", "sparse_embedding.pkl")
    with open(EMBEDDING_PATH, 'rb') as f:
        sparse_embedding = pickle.load(f)

    ### Calculate embeddings
    dense_vector = dense_embedding.embed_query(query)
    sparse_vector = sparse_embedding.embed_query(query)

    ## Set search parameters
    dense_search_params = {
        "data": [dense_vector],
        "anns_field": "dense_vector",
        "param": {
            "metric_type": "IP",
            "params": {}
        },
        "limit": k
    }
    sparse_search_params = {
        "data": [sparse_vector],
        "anns_field": "sparse_vector",
        "param": {
            "metric_type": "IP",
            "params": {}
        },
        "limit": k
    }

    dense_request = AnnSearchRequest(**dense_search_params)
    sparse_request = AnnSearchRequest(**sparse_search_params)
    requests = [dense_request, sparse_request]
    
    ### Dense-sparse ratio
    ranker = WeightedRanker(w, 1-w) ## dense : sparse weight 설정정

    ## Search
    for category in categories:
        res = client.hybrid_search(
            collection_name="User_Reviews",
            reqs=requests,
            ranker=ranker,
            limit=k,
            filter=f"category == {category}" ## 특정 category에 대한 필터링
        )

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-k",
        "--top_k",
        default=5,
        type=int,
        help="# of places to choice (default: 5)",
    )
    args.add_argument(
        "-w",
        "--weight",
        default=0.5,
        type=float,
        help="weight for dense retrieval (default: 0.5)",
    )

    arg = args.parse_args()
    main(arg)