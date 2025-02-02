import os
import pickle

import pandas as pd
from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_milvus.utils.sparse import BM25SparseEmbedding

def main():
    ## Generate milvus database
    URI = os.path.join("data", "course_rcmd_ns.db")
    client = MilvusClient(URI)

    ## Load places dataset
    info_file_name = "place_info.csv"
    review_file_name = "place_review.csv"
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
        field_name="sub_category",
        datatype=DataType.VARCHAR,
        max_length=30,
    )
    schema.add_field(
        field_name="latitude",
        datatype=DataType.FLOAT,
    )
    schema.add_field(
        field_name="longitude",
        datatype=DataType.FLOAT,
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
        index_type="FLAT",
        metric_type="IP",
    )
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
    )

## Create collections by categories
    for category in categories:
        print(f"**{category}**")
        
        ## Create a collection
        collection_name = category
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
        print(f"...Collection for category-{category} is successfully created")

        ## Insert entities into the collection
        entities = []
        category_ids = place_info[place_info["main_category"]==category]["id"]
        review_df = place_review[place_review["id"] in category_ids]
        for _, row in review_df.iterrows():
            info = place_info[place_info["id"]==row["id"]]
            entity = {
                "review_id": info["id"],
                "name": info["name"],
                "sub_category": info["category"],
                "latitude": info["latitude"],
                "longitude": info["longitude"],
                "dense_vector": dense_embedding.embed_query(row["reviews"]),
                "sparse_vector": sparse_embedding.embed_query(row["reviews"]),
                "text": row["reviews"]
            }
            entities.append(entity)

        res = client.insert(
            collection_name=collection_name,
            data=entities
        )

        insert_count = res["insert_count"]
        cost = res["cost"]
        print(f"Result: {insert_count}/{len(entities)-insert_count} (Success/Fail)")
        print(f"It takes.. {cost//60}M {cost%60}S\n")

if __name__ == "__main__":
    main()