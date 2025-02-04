import os
import sys
import json
import pickle

from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker
from langchain_community.embeddings import ClovaXEmbeddings

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
sys.path.append(project_root)
from utils.util import coll_name_mapping

class Retrieval():
    def __init__(
            self,
            query,
            w,
            k,
    ):
        self.w = w
        self.k = k
        
        self.client = self.load_DB()
        self.ranker = WeightedRanker(w, 1-w)
        self.requests = self.make_request(query)
        return
    
    def load_DB(self):
        URI = os.path.join("..", "data", "dense_recommendation.db")
        return MilvusClient(URI)
            
    def call_dense(self):
        return ClovaXEmbeddings(model="clir-emb-dolphin")
    
    def call_sparse(self):
        EMBEDDING_PATH = os.path.join("..", "model", "sparse_embedding.pkl")
        with open(EMBEDDING_PATH, 'rb') as f:
            sparse_embedding = pickle.load(f)
        return sparse_embedding
    
    def make_request(self, query):
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
            "limit": self.k
        }
        sparse_search_params = {
            "data": [sparse_vector],
            "anns_field": "sparse_vector",
            "param": {
                "metric_type": "IP",
                "params": {}
            },
            "limit": self.k
        }

        dense_request = AnnSearchRequest(**dense_search_params)
        sparse_request = AnnSearchRequest(**sparse_search_params)
        return [dense_request, sparse_request]
    
    def search(self, category, place_ids):
        res = self.client.hybrid_serach(
            collection_name=self.coll_name_mapping[category],
            reqs=self.requests,
            ranker=self.ranker,
            limit=self.k,
            filter=f'id in {place_ids}',
            output_fields=["name", "text", "id"]
        )

        outputs = [
            {
                "id": output["id"],
                "name": output["name"],
                "score": output["distance"],
                "text": output["entity"]["text"],
            } for output in res[0]
        ]
        return outputs