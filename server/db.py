# db.py
import pymysql

total_rental_box = 2

def get_db_connection():
    conn = pymysql.connect(
        host="localhost",
        user="woojin",
        password="woojin",
        database="KUmbrella",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn
