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
def update_count(umbrella_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('update umbrella set count = count + 1 where umbrella_id = %s', (umbrella_id,))
    conn.commit()
    cur.close()
    conn.close()
