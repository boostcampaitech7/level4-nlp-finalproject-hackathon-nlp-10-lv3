import os
import json
import pickle
import time

import pandas as pd
from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_milvus.utils.sparse import BM25SparseEmbedding

def main():
    ## Generate milvus database
    URI = os.path.join("data", "course_rcmd.db")
    client = MilvusClient(URI)

    ## Load places dataset
    places = pd.read_csv(os.path.join("data", "places.csv"))

    ## Get category set for all places
    categories = places["main_category"].tolist()

    ## Set dense embedding model
    dense_embedding = ClovaXEmbeddings(model="clir-emb-dolphin")
    dense_dim = len(dense_embedding.embed_query("example"))
    print("...Dense embedding model succesfully loaded.")

    ## Set sparse embedding model
    sparse_embedding = BM25SparseEmbedding(
        corpus=[text for text in places["review"]],
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
        field_name="id",
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

    ## Make collection name mapping
    coll_name_mapping = {category: f"collection_{i}" for i, category in enumerate(categories)}
    with open('coll_name_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(coll_name_mapping, f, ensure_ascii=False)

    ## Create collections by categories
    for category in categories:
        print(f"**{category}**")
        
        ## Create a collection
        collection_name = coll_name_mapping[category]
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
        places_for_category = places[places["main_category"]==category]
        for _, row in places_for_category.iterrows():
            ### standardization
            pos_emb = dense_embedding.embed_query(row["pos_review"])
            neg_emb = dense_embedding.embed_query(row["neg_review"])

            pos_denominator = sum([element**2 for element in pos_emb])
            pos_emb = [element/pos_denominator for element in pos_emb] ## 이렇게 했을 때, 값이 너무 작아서 0이 될 수도 있으려나?
            neg_denominator = sum([element**2 for element in neg_emb])
            neg_emb = [element/neg_denominator for element in neg_emb]

            ### weighted dense embedding
            w = row["pos_cnt"]/(row["pos_cnt"]+row["neg_cnt"])
            weighted_pos_emb = [element*w for element in pos_emb]
            weighted_neg_emb = [element*(1-w) for element in neg_emb]
            tot_emb = [pos-neg for pos, neg in zip(weighted_pos_emb, weighted_neg_emb)]

            ### make entity
            entity = {
                "id": row["id"],
                "name": row["name"],
                "sub_category": row["category"],
                "dense_vector": tot_emb,
                "sparse_vector": sparse_embedding.embed_query(row["review"]),
                "text": row["review"]
            }
            entities.append(entity)
            time.sleep(2)

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