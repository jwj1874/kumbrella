from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db import get_db_connection
from request_pi_routes import read_qr_pi, rental_box

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
        return None, None  # 함수 종료
    
    # 특정 위치 테이블에서 umbrella_id로 상태 업데이트
    update_return_query = f'''
        UPDATE {current_location}
        SET status = %s WHERE umbrella_id = %s
    '''
    cur.execute(update_return_query, (1, umbrella_id))  # status=1로 설정
    
    # umbrella 테이블에서 umbrella_id의 available 상태 업데이트
    cur.execute('UPDATE umbrella SET available = %s WHERE umbrella_id = %s', (1, umbrella_id))
    cur.execute(f'SELECT slot FROM {current_location} WHERE umbrella_id = %s', (umbrella_id,))
    slot = cur.fetchone()
    if slot:
        slot_result = slot['slot']
    else:
        print("Error: umbrella_id에 해당하는 슬롯을 찾을 수 없습니다.")
        conn.close()
        return None, None

    conn.commit()
    cur.close()
    conn.close()
    return current_location, slot_result

@return_bp.route('/return/scan', methods=['GET'])
def scan_qr_code():
    """
    QR 코드 인식 로딩창 표시
    """
    return render_template('scan.html')

@return_bp.route('/return/process', methods=['GET'])
def return_process():
    """
    QR 코드 인식 및 반납 처리
    """
    # QR 코드 인식 및 처리 로직
    location = 'rental_box_0'
    if location == 'rental_box_0':
        umbrella_id = read_qr_pi(location, rental_box[0]['pi_user'], rental_box[0]['pi_password'])
    else:
        umbrella_id = read_qr_pi(location, rental_box[1]['pi_user'], rental_box[1]['pi_password'])

    if umbrella_id:
        # QR 코드 인식 성공 시 처리
        session['umbrella_id'] = umbrella_id
        location, slot = update_return(umbrella_id)
        if location and slot:
            flash("우산이 성공적으로 반납되었습니다.")
            return redirect(url_for('return.return_success', umbrella_id=umbrella_id, location=location, slot=slot))
        else:
            flash("반납 처리 중 오류가 발생했습니다.")
            return redirect(url_for('status.KUmbrella'))
    else:
        # QR 코드 인식 실패 시 처리
        flash("QR 코드 인식에 실패했습니다.")
        return redirect(url_for('status.KUmbrella'))

@return_bp.route('/return/success', methods=['GET'])
def return_success():
    """
    반납 완료 페이지
    """
    umbrella_id = request.args.get('umbrella_id')
    location = request.args.get('location')
    slot = request.args.get('slot')
    return render_template('return.html', umbrella_id=umbrella_id, location=location, slot=slot)