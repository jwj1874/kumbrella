from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify
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

def find_umbrella_info(umbrella_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        find_location_query = '''
        select location from umbrella where umbrella_id = %s
        '''
        cur.execute(find_location_query, (umbrella_id,))
        location = cur.fetchone()
        if location:
            return location
        else:
            return None
    except Exception as e:
        print("Error : ", e)
    finally:
        cur.close()
        conn.close()
        
def find_umbrella_slot(umbrella_id, location):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        find_slot_query = '''
        select slot from %s where umbrella_id = %s
        '''
        cur.execute(find_slot_query, (location, umbrella_id,))
        slot = cur.fetchone()
        if slot:
            return slot
        else:
            return None
    except Exception as e:
        print("Error : ", e)
    finally:
        cur.close()
        conn.close()
        

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
    location = 'rental_box_0'
    if location == 'rental_box_0':
        # 첫 번째 카메라에서 QR 코드 인식
        while True:
            print("첫 번째 카메라에 QR 코드를 인식 시키세요")
            umbrella_id = read_qr_pi(location, rental_box[0]['pi_user'], rental_box[0]['pi_password'], 0)
            if umbrella_id:
                break
            flash("첫 번째 카메라에서 QR 코드 인식에 실패했습니다. 다시 시도하세요.")
        
        # 우산 정보 확인
        return_location = find_umbrella_info(umbrella_id)
        print(return_location)
        if return_location:
            return_slot = find_umbrella_slot(umbrella_id, return_location)
            # 보관함 슬롯 위치 함수 호출
            #
            #
            print("슬롯의 위치 이동중")
            # 보관함 뚜껑 여는 함수 호출
            #
            #
            # 두 번째 카메라에서 QR 코드 인식
            while True:
                print("두 번째 카메라에 QR 코드를 인식 시키세요")
                second_umbrella_id = read_qr_pi(location, rental_box[0]['pi_user'], rental_box[0]['pi_password'], 1)
                if second_umbrella_id:
                    if umbrella_id == second_umbrella_id:
                        # 두 번째 카메라 인식 성공
                        print("두 번째 카메라에서 QR 코드 일치 확인 완료")
                        # 보관함 뚜껑 닫는 함수 호출
                        #
                        #
                        print("보관함이 닫힙니다")
                        # QR 코드 인식 성공 시 처리
                        session['umbrella_id'] = umbrella_id
                        location, slot = update_return(umbrella_id)
                        if location and slot:
                            print("반납 성공")
                            flash("우산이 성공적으로 반납되었습니다.")
                            return jsonify({
                                    "umbrella_id": umbrella_id,
                                    "location": location,
                                    "slot": slot
                                }) 
                        else:
                            flash("반납 처리 중 오류가 발생했습니다.")
                            return redirect(url_for('status.KUmbrella'))
                    else:
                        flash("QR 코드가 일치하지 않습니다. 다시 시도하세요.")
                else:
                    flash("두 번째 카메라에서 QR 코드 인식에 실패했습니다. 다시 시도하세요.")
    else:
        # 첫 번째 카메라에서 QR 코드 인식
        while True:
            umbrella_id = read_qr_pi(location, rental_box[1]['pi_user'], rental_box[1]['pi_password'], 0)
            if umbrella_id:
                break
            flash("첫 번째 카메라에서 QR 코드 인식에 실패했습니다. 다시 시도하세요.")
        
        # 우산 정보 확인
        return_location = find_umbrella_info(umbrella_id)
        if return_location:
            return_slot = find_umbrella_slot(umbrella_id, return_location)
            # 보관함 슬롯 위치 함수 호출
            #
            #
            print("슬롯의 위치 이동중")
            # 보관함 뚜껑 여는 함수 호출
            #
            #
            # 두 번째 카메라에서 QR 코드 인식
            while True:
                second_umbrella_id = read_qr_pi(location, rental_box[1]['pi_user'], rental_box[1]['pi_password'], 1)
                if second_umbrella_id:
                    if umbrella_id == second_umbrella_id:
                        # 두 번째 카메라 인식 성공
                        print("두 번째 카메라에서 QR 코드 일치 확인 완료")
                        # 보관함 뚜껑 닫는 함수 호출
                        #
                        #
                        print("보관함이 닫힙니다")
                        # QR 코드 인식 성공 시 처리
                        session['umbrella_id'] = umbrella_id
                        location, slot = update_return(umbrella_id)
                        if location and slot:
                            flash("우산이 성공적으로 반납되었습니다.")
                            return jsonify({
                                    "umbrella_id": umbrella_id,
                                    "location": location,
                                    "slot": slot
                                })                        
                        else:
                            flash("반납 처리 중 오류가 발생했습니다.")
                            return redirect(url_for('status.KUmbrella'))
                    else:
                        flash("QR 코드가 일치하지 않습니다. 다시 시도하세요.")
                else:
                    flash("두 번째 카메라에서 QR 코드 인식에 실패했습니다. 다시 시도하세요.")


@return_bp.route('/return/success', methods=['GET'])
def return_success():
    """
    반납 완료 페이지
    """
    umbrella_id = request.args.get('umbrella_id')
    location = request.args.get('location')
    slot = request.args.get('slot')
    return render_template('return.html', umbrella_id=umbrella_id, location=location, slot=slot)