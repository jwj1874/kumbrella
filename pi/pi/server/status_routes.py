from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from db import get_db_connection

status_bp = Blueprint('status', __name__)

def clear_session_except_logged_in_user():
    keys_to_keep = ['logged_in', 'user_id']  # 유지할 키 리스트
    keys_to_delete = [key for key in session.keys() if key not in keys_to_keep]

    for key in keys_to_delete:
        session.pop(key, None)  # 키가 존재하지 않아도 에러 없이 삭제

@status_bp.route('/status_board')
def status_board():
    location = request.args.get('location')
    if location not in ['A', 'B']:
        flash("Invalid location.")
        return redirect(url_for('status.KUmbrella'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # location에 따라 조인할 테이블 선택 (테이블 이름만 변경)
    rental_box_table = 'rental_box_0' if location == 'A' else 'rental_box_1'
    
    # 선택된 테이블을 조인하여 대여 가능 여부를 가져옴
    query = f"""
        SELECT r.slot, u.umbrella_id, u.available, r.status
        FROM {rental_box_table} r
        LEFT JOIN umbrella u ON u.umbrella_id = r.umbrella_id
        ORDER BY r.slot
    """
    cursor.execute(query)
    umbrella_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # 총 5개의 슬롯을 확보하고, 슬롯에 따른 상태를 설정
    total_slots = 5
    status_data = []
    
    for slot in range(1, total_slots + 1):
        matching_umbrella = next((u for u in umbrella_data if u['slot'] == slot), None)
        
        if matching_umbrella and matching_umbrella['umbrella_id'] is not None:
            # 각 슬롯의 상태에 따라 표시할 텍스트 설정
            if matching_umbrella['status'] == 0:
                state = "대여중"
            elif matching_umbrella['status'] == 1:
                state = "대여가능"
            elif matching_umbrella['status'] == 3:
                state = "반납예정"
            elif matching_umbrella['status'] == 4:
                state = "고장"
            elif matching_umbrella['status'] == 5:
                state = "우산등록"
            umbrella_id = matching_umbrella['umbrella_id']
        else:
            # umbrella_id가 없을 경우 (빈 슬롯)
            state = "우산등록"
            umbrella_id = None

        status_data.append({'slot': slot, 'umbrella_id': umbrella_id, 'state': state})

    # 대여 가능한 우산의 개수를 계산
    available_count = sum(1 for umbrella in status_data if umbrella['state'] == "대여가능")
    
    return render_template('status_board.html', umbrella_data=status_data, available_count=available_count, location=location)


@status_bp.route('/KUmbrella')
def KUmbrella():
    clear_session_except_logged_in_user()
    if 'logged_in' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # location이 A인 대여 가능한 우산 수 계산 (rental_box_0 테이블 조인)
        query_A = """
            SELECT COUNT(*) AS available_count
            FROM umbrella u
            LEFT JOIN rental_box_0 r ON u.umbrella_id = r.umbrella_id
            WHERE u.available = 1 AND r.status = 1
        """
        cursor.execute(query_A)
        available_count_A = cursor.fetchone()['available_count']
        
        # location이 B인 대여 가능한 우산 수 계산 (rental_box_1 테이블 조인)
        query_B = """
            SELECT COUNT(*) AS available_count
            FROM umbrella u
            LEFT JOIN rental_box_1 r ON u.umbrella_id = r.umbrella_id
            WHERE u.available = 1 AND r.status = 1
        """
        cursor.execute(query_B)
        available_count_B = cursor.fetchone()['available_count']
        
        cursor.close()
        conn.close()
        
        user_id = session['user_id']
        return render_template('KUmbrella.html', available_count_A=available_count_A, available_count_B=available_count_B, user_id=user_id)
    else:
        return redirect(url_for('auth.login'))
