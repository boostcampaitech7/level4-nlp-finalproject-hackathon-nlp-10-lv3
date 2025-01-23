import os
import pickle
import argparse

from pymilvus import Collection, WeightedRanker, connections
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_community.chat_models import ChatClovaX
from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.util import format_docs

def main(arg):
    ## arguments
    query = arg.query
    k = arg.top_k
    w = arg.weight

    ## Connect to VectorDB
    URI = os.path.join("data", "dense_recommendation.db")
    connections.connect(URI)

    collection = Collection("User_Reviews")
    collection.load()

    ## Load embedding models and chat model
    ### chat model
    llm = ChatClovaX(
        model="HCX-003",
        max_tokens=1024
    )

    ### dense embedding
    dense_embedding = ClovaXEmbeddings(model="clir-emb-dolphin")

    ### sparse embedding
    EMBEDDING_PATH = os.path.join("model", "sparse_embedding.pkl")
    with open(EMBEDDING_PATH, 'rb') as f:
        sparse_embedding = pickle.load(f)

    ## Set hybrid retrieval model
    ### Set index parameter
    sparse_search_params = {"metric_type": "IP", "prarms": {"nlist": 3}} ## need to modify
    dense_search_params = {"metric_type": "IP", "params": {"drop_ratio_build": 0.2}} ## need to modify

    ### Get retrieval model
    restaurant_retrieval = MilvusCollectionHybridSearchRetriever(
        collection=collection,
        rerank=WeightedRanker(w, 1-w),
        anns_fields=["dense_vector", "sparse_vector"],
        output_fields=["id", "name"],
        field_embeddings=[dense_embedding, sparse_embedding],
        field_search_params=[dense_search_params, sparse_search_params],
        field_exprs=[
            'category is "식당"',
            f'lat > lat_lb and lat < lat_ub',
            f'log > log_lb and log < log_ub'
        ],
        top_k=k,
        text_field="text",
    )
    cafe_retrieval = MilvusCollectionHybridSearchRetriever(
        collection=collection,
        rerank=WeightedRanker(w, 1-w),
        anns_fields=["dense_vector", "sparse_vector"],
        output_fields=["id", "name"],
        field_embeddings=[dense_embedding, sparse_embedding],
        field_search_params=[dense_search_params, sparse_search_params],
        field_exprs=[
            'category is "카페페"',
            f'lat > lat_lb and lat < lat_ub',
            f'log > log_lb and log < log_ub'
        ],
        top_k=k,
        text_field="text",
    )
    etc_retrieval = MilvusCollectionHybridSearchRetriever(
        collection=collection,
        rerank=WeightedRanker(w, 1-w),
        anns_fields=["dense_vector", "sparse_vector"],
        output_fields=["id", "name"],
        field_embeddings=[dense_embedding, sparse_embedding],
        field_search_params=[dense_search_params, sparse_search_params],
        field_exprs=[
            'category is "기타"',
            f'lat > lat_lb and lat < lat_ub',
            f'log > log_lb and log < log_ub'
        ],
        top_k=k,
        text_field="text",
    )

    QUERY_PROMPT_DIR = os.path.join("prompts", "query_prompt.txt")
    SYSTEM_PROMPT_DIR = os.path.join("prompts", "system_prompt.txt")
    with open(QUERY_PROMPT_DIR, "r") as f:
        QUERY_PROMPT = f.read()
    with open(SYSTEM_PROMPT_DIR, "r") as f:
        SYSTEM_PROMPT = f.read()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", QUERY_PROMPT),
        ]
    )

    rag_chain = (
        {
            "restaurant_retrieval": restaurant_retrieval | format_docs,
            "cafe_retrieval": cafe_retrieval | format_docs,
            "etc_retrieval": etc_retrieval | format_docs,
            "user_query": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print(rag_chain.invoke(query))


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-q",
        "--query",
        type=str,
        help="user query for search",
    )
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