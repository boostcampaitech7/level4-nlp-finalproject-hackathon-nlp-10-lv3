import os
import pickle

import pandas as pd
from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_milvus.utils.sparse import BM25SparseEmbedding

def main():
    ## Generate milvus database
    URI = os.path.join("data", "dense_recommendation.db")
    client = MilvusClient(URI)

    ## Load places dataset
    info_file_name = "place_info"
    review_file_name = "place_review"
    place_info = pd.read_csv(os.path.join("data", info_file_name))
    place_review = pd.read_csv(os.path.join("data", review_file_name))

    ## Get category set for all places
    categories = place_info["main_category"].tolist()

    ## Set dense embedding model
    dense_embedding = ClovaXEmbeddings(model="clir-emb-dolphin")
    dense_dim = len(dense_embedding.embed_query("example"))
    print("...Dense embedding model succesfully loaded.")

    ## Set sparse embedding model
    sparse_embedding = BM25SparseEmbedding(
        corpus=[text["text"] for text in place_review["reviews"]],
        language="kr"
    )
    EMBEDDING_PATH = os.path.join("model", "sparse_embedding.pkl")
    with open(EMBEDDING_PATH, 'wb') as f:
        pickle.dump(sparse_embedding, f)
    print("...Sparse embedding model succesfully loaded.")

    ## Define schema (field name & data type)
    schema = MilvusClient.create_schema(
        auto_id=False,
        enable_dynamic_field=False,
    )

    schema.add_field(
        field_name="reivew_id",
        datatype=DataType.INT64,
        is_primary=True,
    )
    schema.add_field(
        field_name="name",
        datatype=DataType.VARCHAR,
        max_length=30,
    )
    schema.add_field(
        field_name="category",
        datatype=DataType.VARCHAR,
        max_length=2,  ## (식당, 카페, 기타)
    )
    schema.add_field(
        field_name="dense_vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=dense_dim,
    )
    schema.add_field(
        field_name="sparse_vector",
        datatype=DataType.SPARSE_FLOAT_VECTOR,
    )
    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=65_535,
    )

    ## Define index
    index_params = client.prepare_index_params()

    index_params.add_index(
        field_name="dense_vector",
        index_type="IVF_FLAT",
        metric_type="IP",
    )
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
    )

    ## Create a collection
    collection_name = "User_Reviews"
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        consistency_level="Strong",
    )

    ## Create indexes
    client.create_index(
        collection_name=collection_name,
        index_params=index_params,
    )
    print("...Collection is successfully created")

    ## Insert entities into the collection
    entities = []
    for text in texts:
        entity = {
            "id": text["id"],
            "name": text["name"],
            "category": text["category"],
            "dense_vector": dense_embedding.embed_query(text["text"]),
            "sparse_vector": sparse_embedding.embed_query(text["text"]),
            "text": text["text"]
        }
        entities.append(entity)

    res = client.insert(
        collection_name=collection_name,
        data=entities
    )

    print(f"Result: {res["insert_count"]}/{len(entities)-res["insert_count"]} (Success/Fail)")
    print(f"It takes.. {res["cost"]//60}M {res["cost"]%60}S")

if __name__ == "__main__":
    main()