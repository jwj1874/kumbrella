"""
import MySQLdb

def create_database(database_name, rental_box_EA):
    try:
        connection = MySQLdb.connect("localhost", "woojin", "woojin")
        cur = connection.cursor()
        
        cur.execute(f"create database if not exists {database_name}")
        print(f"database '{database_name}' created successfully")
        
        cur.execute(f"use {database_name}")
        cur.execute("create table user (user_id varchar(100), password varchar(100), name varchar(100), phone varchar(100), email varchar(100))")
        print("user table is created")
        #cur.execute("show columns from user")
        
        cur.execute("create table umbrella (umbrella_id int(10), user_id varchar(100), count int(10), available int(10))")
        print("umbrella tabke is created")
        #cur.execute("show columns from umbrella")
        
        cur.execute("create table total (location varchar(10), EA int(10), broken int(10), return_slot int(10))")        
        print("total table is created")
        #cur.execute("show columns from total")
        
        for i in range(rental_box_EA):
            cur.execute(f"create table rental_box_{i}(slot int(10), status int(10), umbrella_id int(10), loaner_id varchar(100))")
            print(f"rental_box{i} is created")
            #cur.execute(f"show columns from rental_box_{i}")
        
        
        
    except MySQLdb.Error as e:
        connection = None
        print("error", e)
    finally:
        if connection:
            connection.close()
            print("Connection closed")
            
def delete_database(database_name):
    try:
        connection = MySQLdb.connect(host = "localhost",
                                     user = "woojin",
                                     passwd = "woojin")
        
        cur = connection.cursor()
        cur.execute(f"drop database if exists {database_name}")
        print(f"database '{database_name}' is deleted successfully")
    except MySQLdb.Error as e:
        connection = None
        print("error", e)
    finally:
        if connection:
            connection.close()
            print("Connection closed")
        
delete_database("KUmbrella")
create_database("KUmbrella", 2)

"""


import pymysql
import uuid
def create_database(database_name, rental_box_EA):
    try:
        # pymysql을 사용하여 MariaDB/MySQL에 연결
        connection = pymysql.connect(
            host="localhost",
            user="woojin",
            password="woojin",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        cur = connection.cursor()
        
        # 데이터베이스 생성
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
        print(f"Database '{database_name}' created successfully")
        
        # 생성한 데이터베이스 사용
        cur.execute(f"USE `{database_name}`")
        
        # user 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user (
                user_id VARCHAR(100),
                password VARCHAR(100),
                name VARCHAR(100),
                phone VARCHAR(100),
                email VARCHAR(100)
            )
        """)
        print("User table is created")
        
        cur.execute('insert into user values ("woojin", "woojin", "전우진", "01000000000", "jonwoojin@gmail.com")')
        cur.execute('insert into user values ("kangmin0310", "min0310", "강민석", "01000000000", "kangmin9370@naver.com")')
        
        # umbrella 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS umbrella (
                umbrella_id VARCHAR(100),
                user_id VARCHAR(100),
                count INT(10),
                available INT(10),
                location varchar(100)
            )
        """)
        print("Umbrella table is created")
        
        # total 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS total (
                location VARCHAR(10),
                EA INT(10),
                broken INT(10),
                return_slot INT(10)
            )
        """)
        print("Total table is created")
        
        # rental_box 테이블 생성
        
        for i in range(rental_box_EA):
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS rental_box_{i} (
                    slot INT(10),
                    status INT(10),
                    umbrella_id VARCHAR(100),
                    loaner_id VARCHAR(100)
                )
            """)
            print(f"Rental box {i} is created")
            
            for slot_num in range(1, 6):  # slot 번호 1에서 5까지
                cur.execute(f"""
                    INSERT IGNORE INTO rental_box_{i} (slot, status, umbrella_id, loaner_id)
                    VALUES (%s, %s, %s, %s)
                """, (slot_num, 5, None, None))  # 기본값으로 None 설정
            connection.commit()
        
        #cur.execute("create table if not exists A (slot INT(10),status INT(10), umbrella_id INT(10),loaner_id VARCHAR(100))")
        #cur.execute("create table if not exists B (slot INT(10),status INT(10), umbrella_id INT(10),loaner_id VARCHAR(100))")
        
    except pymysql.MySQLError as e:
        print("Error:", e)
    finally:
        if connection:
            connection.close()
            print("Connection closed")


def delete_database(database_name):
    try:
        # pymysql을 사용하여 MariaDB/MySQL에 연결
        connection = pymysql.connect(
            host="localhost",
            user="woojin",
            password="woojin",
            charset="utf8mb4"
        )
        
        cur = connection.cursor()
        
        # 데이터베이스 삭제
        cur.execute(f"DROP DATABASE IF EXISTS `{database_name}`")
        print(f"Database '{database_name}' is deleted successfully")
        
    except pymysql.MySQLError as e:
        print("Error:", e)
    finally:
        if connection:
            connection.close()
            print("Connection closed")

# 함수 호출
delete_database("KUmbrella")
create_database("KUmbrella", 2)

import pymysql

# 데이터베이스 연결 함수
def get_db_connection():
    return pymysql.connect(
        host="localhost",    # 데이터베이스 호스트 이름
        user="woojin",    # 사용자 이름 (필요에 따라 수정)
        password="woojin",  # 비밀번호 (필요에 따라 수정)
        db="kumbrella",      # 데이터베이스 이름
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

#일련번호 생성
def generate_unique_serial():
    conn = get_db_connection()
    cursor = conn.cursor()

    while True:
        serial_number = str(uuid.uuid4())  # UUID로 고유한 일련번호 생성
        cursor.execute("SELECT COUNT(*) AS count FROM umbrella WHERE umbrella_id = %s", (serial_number,))
        result = cursor.fetchone()
        if result['count'] == 0:  # 데이터베이스에 중복된 일련번호가 없을 때만 사용
            break

    cursor.close()
    conn.close()
    return serial_number

# 데이터 초기화 및 삽입 함수
def initialize_database():
    # 삽입할 샘플 데이터
    user_data = [
        {"user_id": "kangmin0310", "password": "min0310", "name": "강민석", "phone": "010-9370-9686", "email": "kangmin9370@naver.com"}
    ]
    um_id1 = generate_unique_serial()
    um_id2 = generate_unique_serial()
    um_id3 = generate_unique_serial()
    um_id4 = generate_unique_serial()
    um_id5 = generate_unique_serial()
    um_id6 = generate_unique_serial()
    um_id7 = generate_unique_serial()
    umbrella_data = [
        {"umbrella_id": um_id1, "user_id": "ID_1", "count": 4, "available": 0, "location": "rental_box_0"},
        {"umbrella_id": um_id2, "user_id": "ID_2", "count": 7, "available": 1, "location": "rental_box_0"},
        {"umbrella_id": um_id3, "user_id": "ID_3", "count": 2, "available": 1, "location": "rental_box_0"},
        {"umbrella_id": um_id4, "user_id": "ID_4", "count": 2, "available": 1, "location": "rental_box_0"},
        {"umbrella_id": um_id5, "user_id": "konkuk", "count": 5, "available": 1, "location": "rental_box_1"},
        {"umbrella_id": um_id6, "user_id": "ID_5", "count": 1, "available": 1, "location": "rental_box_1"},
        {"umbrella_id": um_id7, "user_id": "ID_6", "count": 5, "available": 0, "location": "rental_box_1"}
    ]

    rental_box_0_data = [
        {"slot": 1, "status": 0, "umbrella_id": um_id1, "loaner_id": "ID_1"},
        {"slot": 2, "status": 1, "umbrella_id": um_id2, "loaner_id": "ID_2"},
        {"slot": 3, "status": 1, "umbrella_id": um_id3, "loaner_id": "ID_3"},
        {"slot": 4, "status": 1, "umbrella_id": um_id4, "loaner_id": "ID_4"},
        {"slot": 5, "status": 5, "umbrella_id": None, "loaner_id": None}
    ]

    rental_box_1_data = [
        {"slot": 1, "status": 1, "umbrella_id": um_id5, "loaner_id": "konkuk"},
        {"slot": 2, "status": 1, "umbrella_id": um_id6, "loaner_id": "ID_5"},
        {"slot": 3, "status": 4, "umbrella_id": um_id7, "loaner_id": "ID_6"},
        {"slot": 4, "status": 5, "umbrella_id": None, "loaner_id": None},
        {"slot": 5, "status": 5, "umbrella_id": None, "loaner_id": None}
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 각 테이블의 기존 데이터 삭제
        cursor.execute("DELETE FROM user")
        cursor.execute("DELETE FROM umbrella")
        cursor.execute("DELETE FROM rental_box_0")
        cursor.execute("DELETE FROM rental_box_1")

        # user 테이블 데이터 삽입
        for item in user_data:
            cursor.execute(
                """
                INSERT INTO user (user_id, password, name, phone, email)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (item["user_id"], item["password"], item["name"], item["phone"], item["email"])
            )

        # umbrella 테이블 데이터 삽입
        for item in umbrella_data:
            cursor.execute(
                """
                INSERT INTO umbrella (umbrella_id, user_id, count, available, location)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (item["umbrella_id"], item["user_id"], item["count"], item["available"], item["location"])
            )

        # rental_box_0 테이블 데이터 삽입
        for item in rental_box_0_data:
            cursor.execute(
                """
                INSERT INTO rental_box_0 (slot, status, umbrella_id, loaner_id)
                VALUES (%s, %s, %s, %s)
                """,
                (item["slot"], item["status"], item["umbrella_id"], item["loaner_id"])
            )

        # rental_box_1 테이블 데이터 삽입
        for item in rental_box_1_data:
            cursor.execute(
                """
                INSERT INTO rental_box_1 (slot, status, umbrella_id, loaner_id)
                VALUES (%s, %s, %s, %s)
                """,
                (item["slot"], item["status"], item["umbrella_id"], item["loaner_id"])
            )

        # 커밋하여 모든 데이터 저장
        conn.commit()
        print("Database initialized successfully.")

    except pymysql.MySQLError as e:
        print("Error initializing database:", e)
    finally:
        cursor.close()
        conn.close()

# 함수 호출
#initialize_database()
