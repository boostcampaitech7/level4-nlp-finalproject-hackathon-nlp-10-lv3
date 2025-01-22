import os
import pickle
from dotenv import load_dotenv

from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_milvus.utils.sparse import BM25SparseEmbedding

def main():
    ## Load API key
    load_dotenv()
    api_key = os.getenv("NCP_CLOVASTUDIO_API_KEY")
    apigw_key = os.getenv("NCP_APIGW_API_KEY")
    embed_url = os.getenv("EMBED_URL")

    ## Generate milvus database
    URI = os.path.join("data", "dense_recommendation.db")
    client = MilvusClient(URI)

    ## Review dataset
    texts = []

    ## Set dense embedding model
    dense_embedding = ClovaXEmbeddings(
        model="clir-emb-dolphin",
        api_key=api_key,
        apigw_api_key=apigw_key,
        base_url=embed_url,
    )
    dense_dim = 0 ## need to modify

    ## Set sparse embedding model
    sparse_embedding = BM25SparseEmbedding(corpus=texts, language="kr")
    EMBEDDING_PATH = os.path.join("model", "sparse_embedding.pkl")
    with open(EMBEDDING_PATH, 'wb') as f:
        pickle.dump(sparse_embedding, f)

    ## Define schema (field name & data type)
    schema = MilvusClient.create_schema(
        auto_id=False,
        enable_dynamic_field=False,
    )

    schema.add_field(
        field_name="id",
        dtype=DataType.INT64,
        is_primary=True,
    )
    schema.add_field(
        field_name="name",
        dtype=DataType.VARCHAR,
        max_length=30,
    )
    schema.add_field(
        field_name="category",
        dtype=DataType.VARCHAR,
        max_length=2,  ## (식당, 카페, 기타)
    )
    schema.add_field(
        field_name="dense_vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=dense_dim,
    )
    schema.add_field(
        field_name="sparse_vector",
        dtype=DataType.FLOAT_VECTOR,
    )
    schema.add_field(
        field_name="text",
        dtype=DataType.VARCHAR,
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

    ## Insert entities into the collection
    entities = []
    for text in texts:
        entity = {
            "id": text["id"],
            "name": text["name"],
            "category": text["category"],
            "dense_vector": dense_embedding.embed_documents([text])[0],
            "sparse_vector": sparse_embedding.embed_documents([text])[0],
            "text": text["text"]
        }
        entities.append(entity)

    res = client.insert(
        collection_name=collection_name,
        data=entities
    )

    print(f"Result: {res.insert_count}/{len(entities)-res.insert_count} (Success/Fail)")
    print(f"It takes.. {res.cost//60}M {res.cost%60}S")

if __name__ == "__main__":
    main()