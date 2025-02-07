import os
import pickle
from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker
from langchain_community.embeddings import ClovaXEmbeddings
from utils.coll_name_mapping import coll_name_mapping
from loguru import logger

class Retrieval():
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
        URI = os.path.join(".", "db", "course_rcmd_pos.db")
        return MilvusClient(URI)
    
    def close_DB(self):
        self.client.close()
            
    def call_dense(self):
        return ClovaXEmbeddings(model="clir-emb-dolphin", api_key=self.api_key)
    
    def call_sparse(self):
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
        logger.debug(coll_name_mapping(category))
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