import os
import pickle
import argparse
from dotenv import load_dotenv

from pymilvus import Collection, WeightedRanker, connections
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_community.chat_models import ChatClovaX
from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main(arg):
    ## arguments
    query = arg.query
    k = arg.top_k
    w = arg.weight

    ## Load API key
    load_dotenv()
    api_key = os.getenv("NCP_CLOVASTUDIO_API_KEY")
    apigw_key = os.getenv("NCP_APIGW_API_KEY")
    embed_url = os.getenv("EMBED_URL")
    chat_url = os.getenv("CHAT_URL")

    ## Connect to VectorDB
    URI = os.path.join("data", "dense_recommendation.db")
    connections.connect(URI)

    collection = Collection("User_Reviews")
    collection.load()

    ## Load embedding models and chat model
    ### chat model
    llm = ChatClovaX(
        model="HCX-003",
        api_key=api_key,
        apigw_api_key=apigw_key,
        base_url=chat_url,
    )

    ### dense embedding
    dense_embedding = ClovaXEmbeddings(
        model="clir-emb-dolphin",
        api_key=api_key,
        apigw_api_key=apigw_key,
        base_url=embed_url,
    )

    ### sparse embedding
    EMBEDDING_PATH = os.path.join("model", "sparse_embedding.pkl")
    with open(EMBEDDING_PATH, 'rb') as f:
        sparse_embedding = pickle.load(f)

    ## Set hybrid retrieval model
    ### Set index parameter
    sparse_search_params = {"metric_type": "IP", "prarms": {"nlist": 128}} ## need to modify
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

    PROMPT_TEMPLATE = """
    **식당**
    {restaurant_retrieval}

    **카페**
    {cafe_retrieval}

    **기타 활동**
    {etc_retrieval}

    Q.
    {user_query}

    A.
    """

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=[
            "restaurant_retrieval",
            "cafe_retrieval",
            "etc_retrieval",
            "user_query"
        ]
    )

    def format_docs(docs):
        return "\n\n".join(doc.metadata["name"] for doc in docs)
    
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