from database import SQLiteDatabase
import pandas as pd
from pprint import pprint

# ✅ 실행 예제
db_path = "place_Information.db"

# CSV 파일 로드
file_path = "../../../data/spot_info_latlng.csv"
df = pd.read_csv(file_path)

# 변환된 데이터 준비
business_df = df[['id', 'name', 'business_hours', 'rating', 'price_per_one']].copy()

category_df = df[['id', 'main_category', 'category']].copy()
category_df.rename(columns={'id': 'business_id'}, inplace=True)

location_df = df[['id', 'address', 'latitude', 'longitude']].copy()
location_df.rename(columns={'id': 'business_id'}, inplace=True)

# 데이터베이스 처리
db = SQLiteDatabase(db_path)
db.create_tables()  # 테이블 생성
db.insert_data(business_df, category_df, location_df)  # 데이터 삽입

latitude = 37.572289
longitude = 126.980437
results = db.find_nearby_businesses(latitude, longitude, radius=500)
pprint(results)

db.close()  # 연결 종료