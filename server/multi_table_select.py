import pymysql

db = pymysql.connect(
    host="localhost",
    user="minseok",
    password="minseok",
    database="KUmbrella"
)
cur = db.cursor()

# 조회하고자 하는 테이블 목록
tables = ["user", "umbrella", "total", "a"]

for table in tables:
    print(f"Data from {table} table:")
    cur.execute(f"SELECT * FROM {table}")
    
    # 하나씩 데이터를 가져와서 출력
    while True:
        status = cur.fetchone()
        if not status:
            break
        print(status)
    print("-" * 30)  # 각 테이블 사이 구분선

cur.close()
db.close()