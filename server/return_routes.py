from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db import get_db_connection
from request_pi_routes import read_qr_pi, rental_box
import pymysql
return_bp = Blueprint('return', __name__)

def update_return(umbrella_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # umbrella_id로 현재 위치(location) 가져오기
    search_info_query = '''
        SELECT location FROM umbrella WHERE umbrella_id = %s
    '''
    cur.execute(search_info_query, (umbrella_id,))
    result = cur.fetchone()
    if result:
        current_location = result['location']
    else:
        print("Error: umbrella_id에 해당하는 위치를 찾을 수 없습니다.")
        conn.close()
        return  None, None# 함수 종료
    
    
    # 특정 위치 테이블에서 umbrella_id로 상태 업데이트
    update_return_query = f'''
        UPDATE {current_location}
        SET status = %s WHERE umbrella_id = %s
    '''
    cur.execute(update_return_query, (1, umbrella_id))  # status=1로 설정
    
    # umbrella 테이블에서 umbrella_id의 available 상태 업데이트
    cur.execute('UPDATE umbrella SET available = %s WHERE umbrella_id = %s', (1, umbrella_id))
    cur.execute(f'select slot from {current_location} where umbrella_id = %s', (umbrella_id,))
    slot = cur.fetchone()
    if slot:
        slot_result = slot['slot']
    else:
        print("Error : umbreela_id 에 해당하는 슬롯을 찾을 수 없습니다.")
        conn.close()
        return None, None
    conn.commit()
    
    cur.close()
    conn.close()
    return current_location, slot_result
        

@return_bp.route('/return')
def return_process():
    # qr을 통해 라즈베리파이에서 정보 확인 -> 서버로 umbrella_id 전송 => 이 기능 구현할것
    #qr을 어떻게 구분할것인가..
    #일단은 등록과 반납은 묶어서... 등록을 하면 즉시 반납해야 하니 가능.
    #대여시 카메라를 묶기 전까진 일단 라즈베리파이에서 qr생성후 보관
    #카메라 기능 추가하기 전까진 등록->반납, 대여->반납 무조건 짝지어서 하나씩만
    #대여를 하면 qr코드가 생성되지 않기 때문에 반납 프로세스가 불가능..
    location = session.get('temp_location')
    print("location :", location)
    if location == 'rental_box_0':
        umbrella_id = read_qr_pi(location, rental_box[0]['pi_user'], rental_box[0]['pi_password'])
    else:
        umbrella_id = read_qr_pi(location, rental_box[1]['pi_user'], rental_box[1]['pi_password'])

    if umbrella_id:
        location, slot = update_return(umbrella_id)
        if location and slot:
            flash("Umbrella has been successfully returned.")
            return render_template('return.html', 
                umbrella_id=umbrella_id, 
                location=location, 
                slot=slot)
        else:
            flash("No Data to return.")
            return redirect(url_for('status.KUmbrella'))

    else:
        flash("No umbrella ID found in QR code.")
        return redirect(url_for('status.KUmbrella'))
    