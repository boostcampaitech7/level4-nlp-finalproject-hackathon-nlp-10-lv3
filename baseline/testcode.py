import os
import pandas as pd
from pprint import pprint
from dotenv import load_dotenv
from loguru import logger

# geopy util
from model.Retrieve import Retrieval
from utils.category import Category

# database
from db.database import SQLiteDatabase

# MapAPI
from mapAPI.TMapAPI import Tmap_API
from mapAPI.NaverSearchAPI import get_lat_lon
# Model
from model.ChatModel import ClovaXChatModel
from model.Retrieve import Retrieval
from utils.category import Category
from utils.recommend import Recommend


load_dotenv()
TMAP_API_KEY = os.getenv("TMAP_API_KEY")
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
SEARCH_API_ID = os.getenv("NAVER_SEARCH_API_ID")
SEARCH_API_KEY = os.getenv("NAVER_SEARCH_API_KEY")

chatModel = ClovaXChatModel(API_KEY=CLOVA_API_KEY)
tMAP = Tmap_API(API_KEY=TMAP_API_KEY)
database = SQLiteDatabase("./db/place_Information.db")
category_generator = Category(chatModel, database)

place = "안국역"

start_place_latlng = get_lat_lon(place, SEARCH_API_ID, SEARCH_API_KEY) # 위 경도 추출
# sql DB에서 장소 추출 (위경도 기준 반경 500M 추출)
candidate_places = database.find_nearby_businesses(start_place_latlng[1], start_place_latlng[0])
place_ids = [cand["id"] for cand in candidate_places]
logger.debug(f"현재 장소로부터 탐색된 갯수 : {len(place_ids)}")

input_dict = {
    "request" : "가성비 좋은 코스로 추천해줘",
    "age": "20대 초반",
    "sex": "남성",
    "start_time" : "14시"
}

logger.debug(f'요구사항 : {input_dict["request"]}, {input_dict["age"]}, {input_dict["sex"]}, {input_dict["start_time"]}')

choosed_category = category_generator.get_all_category(input_dict)
print(choosed_category)

# ## Inputs and Paramters (Requirements)
# query = ""
# w = 0.5
# k = 30

# ## Retrieval
# ### Load retrieval module
# retrieval = Retrieval(query, w, k)

# ### Search
# retrieved_outputs = {}
# for category in choosed_category:
#     outputs = retrieval.search(category[0], place_ids) ## candidate_place의 output에서 id만 뽑아서 place_ids로 활용
#     retrieved_outputs[category[0]] = outputs
# retrieval.close_DB()

