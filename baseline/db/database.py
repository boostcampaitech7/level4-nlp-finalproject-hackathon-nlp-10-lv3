import sqlite3
import pandas as pd

import sqlite3
import math

class BusinessSearch:
    def __init__(self, db_path):
        """
        데이터베이스 연결 및 커서 생성
        """
        self.db_path = db_path

    def find_nearby_businesses(self, lat, lon, radius=500):
        """
        특정 위도(lat), 경도(lon)를 기준으로 반경 radius(m) 이내의 업체를 검색.
        반경 필터링은 Haversine 공식을 사용하여 구현.

        :param lat: 기준 위도 (float)
        :param lon: 기준 경도 (float)
        :param radius: 검색 반경 (미터 단위, 기본값 500m)
        :return: 반경 내의 업체 리스트
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        # ✅ Haversine 공식 적용한 SQL 쿼리
        query = """
        SELECT b.id, b.name, c.main_category, c.category, 
               l.address, l.latitude, l.longitude, b.rating, 
               b.price_per_one, b.business_hours,
               (6371000 * acos(
                   cos(radians(?)) * cos(radians(l.latitude)) * 
                   cos(radians(l.longitude) - radians(?)) + 
                   sin(radians(?)) * sin(radians(l.latitude))
               )) AS distance
        FROM Business b
        JOIN Category c ON b.id = c.business_id
        JOIN Location l ON b.id = l.business_id
        HAVING distance < ?
        ORDER BY distance ASC;
        """

        # SQL 실행 (입력된 값 바인딩)
        cur.execute(query, (lat, lon, lat, radius))
        results = cur.fetchall()

        # 데이터 변환
        columns = ["id", "name", "main_category", "category", "address", 
                   "latitude", "longitude", "rating", "price_per_one", "business_hours", "distance"]
        nearby_businesses = [dict(zip(columns, row)) for row in results]

        # 연결 종료
        conn.close()
        return nearby_businesses


# ✅ 실행 예제
if __name__ == '__main__':
    db_path = "example.db"  # 데이터베이스 경로
    search = BusinessSearch(db_path)

    # 📌 예제: 위도 37.572289, 경도 126.980437 기준 반경 500m 내 업체 검색
    latitude = 37.572289
    longitude = 126.980437
    results = search.find_nearby_businesses(latitude, longitude, radius=500)

    # 결과 출력
    for business in results:
        print(business)


class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")  # 외래키 활성화
        self.cur = self.conn.cursor()

    def create_tables(self):
        """
        Business, Category, Location 테이블을 생성.
        """
        # Business 테이블 생성
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Business (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            business_hours TEXT,
            rating REAL,
            price_per_one TEXT
        );
        """)

        # Category 테이블 생성 (Business.id를 외래키로 사용)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Category (
            business_id INTEGER PRIMARY KEY,
            main_category TEXT NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY (business_id) REFERENCES Business(id)
        );
        """)

        # Location 테이블 생성 (Business.id를 외래키로 사용)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Location (
            business_id INTEGER PRIMARY KEY,
            address TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            FOREIGN KEY (business_id) REFERENCES Business(id)
        );
        """)

        self.conn.commit()

    def insert_data(self, business_df, category_df, location_df):
        # Business 데이터 삽입
        business_sql = """
        INSERT INTO Business (id, name, business_hours, rating, price_per_one)
        VALUES (?, ?, ?, ?, ?)
        """
        self.cur.executemany(business_sql, business_df.values.tolist())

        # Category 데이터 삽입
        category_sql = """
        INSERT INTO Category (business_id, main_category, category)
        VALUES (?, ?, ?)
        """
        self.cur.executemany(category_sql, category_df.values.tolist())

        # Location 데이터 삽입
        location_sql = """
        INSERT INTO Location (business_id, address, latitude, longitude)
        VALUES (?, ?, ?, ?)
        """
        self.cur.executemany(location_sql, location_df.values.tolist())

        self.conn.commit()

    def find_nearby_businesses(self, lat, lon, radius=500):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        # ✅ Haversine 공식 적용한 SQL 쿼리
        query = """
        SELECT b.id, b.name, c.main_category, c.category, 
               l.address, l.latitude, l.longitude, b.rating, 
               b.price_per_one, b.business_hours,
               (6371000 * acos(
                   cos(radians(?)) * cos(radians(l.latitude)) * 
                   cos(radians(l.longitude) - radians(?)) + 
                   sin(radians(?)) * sin(radians(l.latitude))
               )) AS distance
        FROM Business b
        JOIN Category c ON b.id = c.business_id
        JOIN Location l ON b.id = l.business_id
        WHERE distance < ?
        ORDER BY distance ASC;
        """

        # SQL 실행 (입력된 값 바인딩)
        cur.execute(query, (lat, lon, lat, radius))
        results = cur.fetchall()

        # 데이터 변환
        columns = ["id", "name", "main_category", "category", "address", 
                   "latitude", "longitude", "rating", "price_per_one", "business_hours", "distance"]
        nearby_businesses = [dict(zip(columns, row)) for row in results]
        return nearby_businesses

    def close(self):
        """데이터베이스 연결 종료"""
        self.conn.close()


