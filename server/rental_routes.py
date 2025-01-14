from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, flash
from db import get_db_connection, update_count
from point_routes import deduct_renter_points, reward_owner_points
from request_pi_routes import remote_slot, servo_open, servo_close, rental_box
rental_bp = Blueprint('rental', __name__)
import time
@rental_bp.route('/rental')
def rental():
    # 대여중인 우산이 존재하는지 확인
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = session['user_id']
    cursor.execute("select rp from user where user_id = %s", (user_id,))
    rp = cursor.fetchone()
    if rp == True:
        print("대여중인 우산이 존재합니다")
        cursor.close()
        conn.close()
        return redirect(url_for('status.KUmbrella'))

    # 대여 페이지 렌더링
    cursor.close()
    conn.close()
    return render_template('rental.html')


@rental_bp.route('/rent_umbrella')
def rent_umbrella():
    umbrella_id = request.args.get('umbrella_id')
    slot = request.args.get('slot')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # umbrella_id와 slot 정보를 사용하여 추가 로직을 처리 가능
    # 예를 들어, 대여 처리 로직 또는 우산 정보를 표시하는 템플릿을 렌더링 가능
    print(f"Renting umbrella ID: {umbrella_id}, Slot: {slot}")
    
    session['original_umbrella_id'] = umbrella_id  # 초기 우산 ID
    session['original_slot'] = slot  # 초기 슬롯
    # 우산을 선택한 시점에 우산의 available은 0이 되어 다른 사람이 선택할 수 없게 설정
    update_query = """
        update umbrella
        set available = 0
        where umbrella_id = %s
    """
    cur.execute(update_query, (umbrella_id,))
    conn.commit()

    cur.execute('select location from umbrella where umbrella_id = %s', (umbrella_id,))
    location = cur.fetchone()
    session['original_location'] = location  # 초기 우산 위치
    cur.close()
    conn.close()

    return render_template('rental.html', umbrella_id=umbrella_id, slot=slot)


@rental_bp.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    # 클라이언트에서 전달된 목적지 가져오기
    destination = request.json.get('destination')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 선택한 목적지에 따라 테이블 이름 결정
    table_name = 'rental_box_0' if destination == 'A' else 'rental_box_1'

    # 반납 가능한 슬롯 조회 쿼리 (status가 5인 슬롯만 조회)
    query = f"""
        SELECT slot FROM {table_name}
        WHERE status = 5
    """
    cursor.execute(query)
    available_slots = [row['slot'] for row in cursor.fetchall()]  # 반납 가능한 슬롯 목록
    cursor.close()
    conn.close()

    # JSON 형태로 반납 가능한 슬롯 반환
    return jsonify(available_slots=available_slots)


@rental_bp.route('/process_rental', methods=['POST'])
def process_rental():
    # 폼 데이터에서 목적지와 슬롯 가져오기
    destination = request.form.get('destination')
    slot = request.form.get('slot')

    # 목적지에 따른 테이블 결정
    table_name = 'rental_box_0' if destination == 'A' else 'rental_box_1'

    # 대여 요청 처리
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        renter_id = session['user_id']
        umbrella_id = session['original_umbrella_id']  # 대여 시점의 우산 ID
        # 기존 보관함 db 업데이트
        original_location = session['original_location']['location']  # 초기 위치
        print("Updating location table:", original_location)  # 디버깅용 출력
        update_query = f"""
            update {original_location}
            set status = 5, umbrella_id = %s, renter_id = %s where umbrella_id = %s AND status = 1
        """
        cursor.execute(update_query, (None, None, umbrella_id,))
        # 슬롯의 상태 업데이트 (예: status = 3로 대여 상태로 변경)
        update_query = f"""
            UPDATE {table_name}
            SET status = 3
            , renter_id = %s
            , umbrella_id = %s
            WHERE slot = %s
        """

        cursor.execute(update_query, (renter_id, umbrella_id, slot,))
        conn.commit()

        update_count(umbrella_id)

        # 우산이 대여중일 때 반납 위치를 destination_location에 저장
        session['destination_location'] = table_name  # 반납할 위치 저장
        session['destination_slot'] = slot  # 반납할 슬롯 저장

        cursor.execute('update umbrella set location = %s', (table_name,))
        
        # 포인트 관련 기능 호출
        deduct_renter_points(renter_id)
        reward_owner_points(umbrella_id)

        # 대여중인 우산이 존재하는 것을 DB에 저장
        cursor.execute("update user set rp = True where user_id = %s", (renter_id,))
        conn.commit()
        #######################################
        slot = session['original_slot']
        print(type(slot))
        init_slot = 10-int(slot)
        print(init_slot)
        remote_slot('rental_box_0',rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"], slot)
        servo_open('rental_box_0',rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"])
        time.sleep(5)
        servo_close('rental_box_0',rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"])
        remote_slot('rental_box_0',rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"], init_slot)
        #######################################
        
        #flash("Rental process completed successfully.")
    except Exception as e:
        conn.rollback()
        #flash("An error occurred during the rental process.")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('status.KUmbrella', location=destination))