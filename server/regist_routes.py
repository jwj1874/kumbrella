from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
import uuid
from request_pi_routes import create_qr_pi, read_qr_pi, rental_box
from return_routes import update_return
register_bp = Blueprint('register', __name__)

def generate_unique_serial():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        while True:
            serial_number = str(uuid.uuid4())  # UUID로 고유한 일련번호 생성
            cursor.execute("SELECT COUNT(*) FROM umbrella WHERE umbrella_id = %s", (serial_number,))
            
            result = cursor.fetchone()
            print("Query Result:", result)  # 쿼리 결과 확인

            # 딕셔너리 형태의 result에서 'COUNT(*)' 키로 접근
            if result is not None and result['COUNT(*)'] == 0:
                break

    except Exception as e:
        print("Database error:", e)
        return None  # 오류 발생 시 None 반환

    finally:
        cursor.close()
        conn.close()

    return serial_number
    

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        umbrella_id = request.form.get('umbrella_id')
        location = request.form.get('location')
        slot = request.form.get('slot')
        location = 'rental_box_0' if location == 'A' else 'rental_box_1'
        print(umbrella_id, location, slot)
        if not umbrella_id or not location:
            flash("All fields are required.")
            return redirect(url_for('register.register'))
        #일련번호 생성 과정이 필요---
        new_umbrella_id = generate_unique_serial()
        #대여함에서(라즈베리파이에서) qr코드 생성
        
        create_qr_pi(location, rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"], new_umbrella_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        # 등록 정보를 데이터베이스에 추가
        cursor.execute(
            "INSERT INTO umbrella (umbrella_id, user_id, count, available, location) VALUES (%s, %s, %s, %s, %s)",
            (new_umbrella_id, user_id, 0, 0, location)
        )
        #등록 우산을 해당 슬롯에 위치
        cursor.execute(
            f'update {location} set status = 3, umbrella_id = %s, renter_id = %s where slot = %s',
            (new_umbrella_id, user_id, slot,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        #우산 정보가 업데이트 되고 난 후 우산을 거치하는 과정이 필요 -> 이는 반납 과정과 같다.
        
        #카메라 추가시 삭제할 내용#############
        session['temp_location'] = location 
        #####################################
        session['original_umbrella_id'] = new_umbrella_id
        #반납 시 사용할 우산 정보
        
        flash("Umbrella registered successfully!")
    
        return render_template('regist.html', umbrella_id=new_umbrella_id, location=location, slot=slot)
    
    # GET 요청 시 등록 페이지 렌더링
    return render_template('regist.html')

@register_bp.route('/regiser_step_2')
def register_process():
    # qr을 통해 라즈베리파이에서 정보 확인 -> 서버로 umbrella_id 전송 => 이 기능 구현할것
    #qr을 어떻게 구분할것인가..
    #일단은 등록과 반납은 묶어서... 등록을 하면 즉시 반납해야 하니 가능.
    #대여시 카메라를 묶기 전까진 일단 라즈베리파이에서 qr생성후 보관
    #카메라 기능 추가하기 전까진 등록->반납, 대여->반납 무조건 짝지어서 하나씩만
    #대여를 하면 qr코드가 생성되지 않기 때문에 반납 프로세스가 불가능..
    location = session.get('temp_location')
    print("location :", location)
    if location == 'rental_box_0':
        umbrella_id = read_qr_pi(location, rental_box[0]['pi_user'], rental_box[0]['pi_password'], 0)
    else:
        umbrella_id = read_qr_pi(location, rental_box[1]['pi_user'], rental_box[1]['pi_password'], 0)

    if umbrella_id:
        location, slot = update_return(umbrella_id)
        location = 'A' if location == 'rental_box_0' else 'B'
        flash("Umbrella has been successfully register.")
        return render_template('register_step_2.html', 
            umbrella_id=umbrella_id, 
            location=location, 
            slot=slot)
    else:
        flash("No umbrella ID found in QR code.")
        return redirect(url_for('status.KUmbrella'))
