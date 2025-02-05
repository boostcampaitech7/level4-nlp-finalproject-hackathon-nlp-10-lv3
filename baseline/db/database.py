import sqlite3
import pandas as pd

import sqlite3
import math

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

    def find_nearby_businesses(self, lat, lng, radius=500):
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
        cur.execute(query, (lat, lng, lat, radius))
        results = cur.fetchall()

        # 데이터 변환
        columns = ["id", "name", "main_category", "category", "address", 
                   "latitude", "longitude", "rating", "price_per_one", "business_hours", "distance"]
        nearby_businesses = [dict(zip(columns, row)) for row in results]
        return nearby_businesses

    def close(self):
        """데이터베이스 연결 종료"""
        self.conn.close()


