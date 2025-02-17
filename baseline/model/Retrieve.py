import os
import pickle
from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker
from langchain_community.embeddings import ClovaXEmbeddings
from utils.coll_name_mapping import coll_name_mapping
from loguru import logger

class Retrieval():
    """
    주어진 카테고리 및 사용자 요구사항 기반으로 구체적인 장소 검색

    각 장소별 요약된 리뷰를 카테고리 별로 저장한 vectorDB와 연결
    주어진 카테고리에 맞춰 검색 수행
    사용자 쿼리와 저장된 리뷰 기반으로
    Dense와 Sparse method의 weighted sum을 활용한 Hybrid search 활용

    Args:
        query (str): 사용자 요구사항
        w (float): Dense retrieval score에 적용할 weight값 (0에서 1사이의 값)
        k (int): 검색할 장소의 수
        place_ids (List[int]): 검색 장소 기준 일정 거리 내 장소들의 ID
        api_key (str): Naver Clova Studio API key
    """
    def __init__(
            self,
            query,
            w,
            k,
            place_ids,
            api_key
    ):
        self.w = w
        self.k = k
        self.api_key = api_key
        self.client = self.load_DB()
        self.ranker = WeightedRanker(w, 1-w)
        self.requests = self.make_request(query, place_ids)
        return
    
    def load_DB(self):
        URI = os.path.join(".","db","course_rcmd_pos.db")
        return MilvusClient(URI)
    
    def close_DB(self):
        """
        VectorDB와 연결 해제
        """
        self.client.close()
            
    def call_dense(self):
        """
        Dense Retrieval에 활용할 Clova Studio Embedding model 호출

        Returns:
            ClovaXEmbeddings: Query를 vector 형태의 embedding으로 변환
        """
        return ClovaXEmbeddings(model="clir-emb-dolphin", api_key=self.api_key)
    
    def call_sparse(self):
        """
        Sparse Retrieval에 활용할 BM25 embedding model 호출

        Returns:
            BM25Embedding: Query를 vector 형태의 embedding으로 변환
        """
        EMBEDDING_PATH = os.path.join(".", "model", "sparse_embedding.pkl")
        with open(EMBEDDING_PATH, 'rb') as f:
            sparse_embedding = pickle.load(f)
        return sparse_embedding
    
    def make_request(self, query, place_ids):
        dense_embedding = self.call_dense()
        sparse_embedding = self.call_sparse()
        dense_vector = dense_embedding.embed_query(query)
        sparse_vector = sparse_embedding.embed_query(query)

        dense_search_params = {
            "data": [dense_vector],
            "anns_field": "dense_vector",
            "param": {
                "metric_type": "IP",
                "params": {}
            },
            "limit": self.k,
            "expr": f'id in {place_ids}'
        }
        sparse_search_params = {
            "data": [sparse_vector],
            "anns_field": "sparse_vector",
            "param": {
                "metric_type": "IP",
                "params": {}
            },
            "limit": self.k,
            "expr": f'id in {place_ids}'
        }

        dense_request = AnnSearchRequest(**dense_search_params)
        sparse_request = AnnSearchRequest(**sparse_search_params)
        return [dense_request, sparse_request]
    
    def search(self, category):
        res = self.client.hybrid_search(
            collection_name=coll_name_mapping(category),
            reqs=self.requests,
            ranker=self.ranker,
            limit=self.k,
            output_fields=["name", "text", "id", "positive_text"]
        )

        outputs = [
            {
                "id": output["id"],
                "name": output["entity"]["name"],
                "score": output["distance"],
                "text": output["entity"]["text"],
                "positive_text": output["entity"]["positive_text"],
            } for output in res[0]
        ]
        return outputs