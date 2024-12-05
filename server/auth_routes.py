# auth_routes.py
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db import get_db_connection
import pymysql
import bcrypt

auth_bp = Blueprint('auth', __name__)
##############################################################################################
##############################################################################################
def hash_password(in_pw):       #비밀번호 암호화
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        return bcrypt.hashpw(in_pw.encode('utf-8'), bcrypt.gensalt())
    except Exception as e:
        print("Password hashing error:", e)
        return None
    finally:
        cur.close()
        conn.close()
    
def check_password(in_pw, hashed_password):     #로그인 시 비밀번호 확인
    try:
        return bcrypt.checkpw(in_pw.encode('utf-8'), hashed_password)
    except ValueError as e:
        print("Invalid hashed password or salt:", e)
        return False

 #id 중복 확인
def check_data_exists(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "select 1 from user where user_id = %s limit 1;"
        cur.execute(query, (user_id,))
        result = cur.fetchone()
        if result:
            return True
        else:
            return False
    except Exception as e:
        print("Error : ", e)
    finally:
        cur.close()
        conn.close()
def check_login_info(input_id, input_pw):
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('select * from user where user_id = %s', (input_id,))
        user = cur.fetchone()
    except Exception as e:
        print("Error : ", e)
    finally:
        cur.close()
        conn.close()
        if user:
            stored_pw = user['password'].encode('utf-8')
            if check_password(input_pw, stored_pw):
                session['logged_in'] = True
                session['user_id'] = user['user_id']
                return True
            else:
                return False    
        else:
            return False
        
#회원가입
def regist(user_id, password, name, phone, email):
    conn = get_db_connection()
    cur = conn.cursor()
    check_data_exist_flag = check_data_exists(user_id)
    if check_data_exist_flag:
        print("이미 존재하는 데이터 입니다")
        cur.close()
        conn.close()
        return False
    else:
        hashed_password = hash_password(password)  # 암호화된 비밀번호 생성
        if not hashed_password:  # 암호화 실패 처리
            print("Password hashing failed.")
            return False
        state = {
            "user_id": user_id,
            "password": hashed_password.decode('utf-8'),  # 바이너리를 문자열로 저장
            "name": name,
            "phone": phone,
            "email": email
        }
        parameter = [state["user_id"], state["password"], state["name"], state["phone"], state["email"]]
        SQL = '''
            INSERT INTO user (user_id, password, name, phone, email)    
            VALUES (%s, %s, %s, %s, %s)'''
        try:
            cur.execute(SQL, parameter)
            conn.commit()
        except Exception as e:
            print("Database error:", e)
            return False
        finally:
            cur.close()
            conn.close()
        return True




##############################################################################################
##############################################################################################
@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/create_account', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('id')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        if regist(user_id, password, name, phone, email):
            flash("회원가입이 완료되었습니다", "success")
            return redirect(url_for('auth.login'))

        else:
            flash("이미 존재하는 ID 입니다.", 'error')
            return redirect(url_for('auth.register'))    
    return render_template('create_account.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('id')
        password = request.form.get('password')
        user = check_login_info(user_id, password)
        if user:
            return redirect(url_for('status.KUmbrella'))
        else:
            flash("아이디 또는 비밀번호가 틀렸습니다.")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))
