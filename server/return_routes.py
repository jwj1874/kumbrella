from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify
from db import get_db_connection
from request_pi_routes import read_qr_pi, rental_box, remote_slot, servo_close, servo_open
import time
return_bp = Blueprint('return', __name__)

def clear_session_except_logged_in_user():
    keys_to_keep = ['logged_in', 'user_id']  # 유지할 키 리스트
    keys_to_delete = [key for key in session.keys() if key not in keys_to_keep]

    for key in keys_to_delete:
        session.pop(key, None)  # 키가 존재하지 않아도 에러 없이 삭제

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
            return location['location']
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
        find_slot_query = f'''
        select slot from {location} where umbrella_id = %s
        '''
        cur.execute(find_slot_query, (umbrella_id,))
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
        
def first_camera(location): # scan한 우산 id를 리턴
    print("외부 카메라에 QR Code를 인식시키세요")
    if location == 'rental_box_0':
        destination = 0
    else:
        destination = 1
    umbrella_id = read_qr_pi(location, rental_box[destination]['pi_user'], rental_box[destination]['pi_password'], 0)
    if umbrella_id != None:
        print("외부 카메라 인식 성공")
        return umbrella_id
    else:
        print("외부 카메라 인식 실패")
        return None
def second_camera(location):
    if location == 'rental_box_0':
        destination = 0
    else:
        destination = 1
    print("내부 카메라에 QR Code를 인식시키세요")
    umbrella_id = umbrella_id = read_qr_pi(location, rental_box[destination]['pi_user'], rental_box[destination]['pi_password'], 1)
    if umbrella_id != None:
        print("내부 카메라 인식 성공")
        return umbrella_id
    else:
        print("내부 카메라 인식 실패")
        return None

@return_bp.route('/return/scan', methods=['GET'])
def scan_qr_code():
    """
    QR 코드 인식 로딩창 표시
    """
    return render_template('scan.html')

@return_bp.route('/return/process', methods=['GET'])
def return_process():
    try:
        umbrella_id = session['original_umbrella_id'] # 세션에 저장한 umbrella_id 받아오기
        print(umbrella_id)
    except KeyError:
        print("session error")
        return redirect(url_for('status.KUmbrella'))
    
    return_location = find_umbrella_info(umbrella_id) # db에서 반납 위치 가저오기
    print(return_location)
    if umbrella_id == first_camera(return_location):
        slot = find_umbrella_slot(umbrella_id, return_location)
        #슬롯을 위치시키고 뚜껑을 여는 과정
        print(return_location, rental_box[0]["pi_user"], rental_box[0]["pi_password"], slot['slot'])
        remote_slot(return_location,rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"], slot['slot'])
        servo_open(return_location,rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"])
        time.sleep(5)
        if umbrella_id == second_camera(return_location):
            #보관함을 닫는 과정
            servo_close(return_location,rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"])
            init_slot = 10-slot['slot']
            remote_slot(return_location,rental_box[0]["pi_user"], 
                     rental_box[0]["pi_password"], init_slot)
            location, slot = update_return(umbrella_id)
            if location and slot:
                user_id = session['user_id']
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("update user set rp = False where user_id = %s", (user_id,))
                conn.commit()
                cur.close()
                conn.close()
                print("반납 성공")
                #flash("우산 반납이 완료되었습니다")
                return jsonify({
                    "umbrella_id" : umbrella_id,
                    "location" : location,
                    "slot" : slot
                })
            else:
                print("DB에 해당 우산의 정보가 없음")
                return redirect(url_for('status.KUmbrella'))
        else:
            print("내부 카메라에 인식된 QR 코드가 일치하지 않거나 인식 실패")
            return redirect(url_for('status.KUmbrella'))
    else:
        print("외부 카메라에 인식한 QR 코드가 일치하지 않거나 인식 실패")
        return redirect(url_for('status.KUmbrella'))
    

@return_bp.route('/return/success', methods=['GET'])
def return_success():
    """
    반납 완료 페이지
    """
    umbrella_id = request.args.get('umbrella_id')
    location = request.args.get('location')
    slot = request.args.get('slot')
    clear_session_except_logged_in_user()
    return render_template('return.html', umbrella_id=umbrella_id, location=location, slot=slot)