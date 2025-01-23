import os
import pickle

from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import ClovaXEmbeddings
from langchain_milvus.utils.sparse import BM25SparseEmbedding

def main():
    ## Generate milvus database
    URI = os.path.join("data", "dense_recommendation.db")
    client = MilvusClient(URI)

    ## Review dataset
    texts = [
        {
            "id": 1,
            "name": "장소1",
            "category": "식당",
            "text": "대체로 음식이 맛있다고 평가되지만, 양이 적다는 후기가 많습니다. 많은 사람이 부모님과 함께 오기 좋은 장소로 꼽고 있습니다다.",
        },
        {
            "id": 2,
            "name": "장소2",
            "category": "카페",
            "text": "커피 향이 좋다는 평이 많고, 조금 비싸다는 후기가 있습니다. 가게 내부는 잔잔한 분위기로 대화를 나누기에 적합합니다.",
        },
        {
            "id": 3,
            "name": "장소3",
            "category": "기타",
            "text": "연인과 함께 즐겁게 시간을 보내기 좋은 장소이며, 찾아오는 길이 복잡하다는 후기가 많습니다.",
        },
        {
            "id": 4,
            "name": "장소4",
            "category": "식당",
            "text": "양이 푸짐하고 가격이 저렴하지만, 음식이 전반적으로 맵다고 평가됩니다. 매운 음식을 좋아하는 사람에게 많이 추천되고 있습니다.",
        },
        {
            "id": 5,
            "name": "장소5",
            "category": "카페",
            "text": "커피의 종류가 다양하고, 특히 로스터리 커피에 대한 좋은 평이 많습니다. 연인과 함께 오기 좋은 공간입니다.",
        },
        {
            "id": 6,
            "name": "장소6",
            "category": "기타",
            "text": "활동적인 프로그램이 많이 준비돼 있고, 직원이 친절합니다. 다만, 가격 부담이 클 수 있습니다.",
        },
        {
            "id": 7,
            "name": "장소7",
            "category": "식당",
            "text": "가게 내부가 지저분하고, 사장님이 불친절하다는 후기가 많습니다.",
        },
        {
            "id": 8,
            "name": "장소8",
            "category": "카페",
            "text": "브라우니가 맛있다는 의견이 많으며, 커피는 대체로 산미가 풍부하다는 평을 받고 있습니다. 가게 내부에 잔잔한 음악이 흘러나와 분위기가 좋습니다.",
        },
        {
            "id": 9,
            "name": "장소9",
            "category": "기타",
            "text": "다양한 테마가 준비돼 있고, 돈이 아깝지 않은 구성이라는 평이 많습니다.",
        },
    ]

    ## Set dense embedding model
    dense_embedding = ClovaXEmbeddings(model="clir-emb-dolphin")
    dense_dim = len(dense_embedding.embed_query("example"))
    print("...Dense embedding model succesfully loaded.")

    ## Set sparse embedding model
    sparse_embedding = BM25SparseEmbedding(corpus=[text["text"] for text in texts], language="kr")
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