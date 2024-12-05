
'''
from flask import Blueprint, session, redirect, url_for, flash
from db import get_db_connection

broken_bp = Blueprint('broken', __name__)

@broken_bp.route('/broken_process')
def broken_process():
    # 세션에서 대여된 우산 정보 가져오기
    
    
    if not umbrella_id or not slot or not original_location or not original_slot:
        print("우산 대여 정보가 존재하지 않습니다.")
        return redirect(url_for('status.KUmbrella'))
    
    # original_location이 딕셔너리 형태라면, 실제 location 값은 original_location['location']입니다.
    location = original_location.get('location') if isinstance(original_location, dict) else original_location
    
    if not location:
        print("원래 위치 정보가 없습니다.")
        return redirect(url_for('status.KUmbrella'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 원래 대여된 장소의 상태를 4로 변경하여 고장 상태로 처리
        update_query = f"""
            UPDATE {location}
            SET status = 4, umbrella_id = %s, renter_id = NULL
            WHERE umbrella_id = %s AND slot = %s
        """
        cursor.execute(update_query, (umbrella_id, umbrella_id, original_slot))
        conn.commit()
        print("원래 대여 장소 정보", location, umbrella_id, original_slot)
        
        # 반납될 장소의 상태를 5로 변경하여 우산을 등록할 수 있는 상태로 만듦
        # 반납 위치는 대여 페이지에서 저장된 정보에서 destination을 사용하여 결정
        destination = session.get('destination')  # 반납 위치
        slot = session.get('destination_slot')
        print(destination, slot)
        ##cursor.execute(f"update {destination} set status = 5, umbrella_id = NULL, renter_id = NULL where slot = %s", (slot,))

        # 우산이 고장 난 상태로 변경된 것에 대한 정보 업데이트 (available 컬럼 업데이트)
        ##cursor.execute("UPDATE umbrella SET available = 0 WHERE umbrella_id = %s", (umbrella_id,))
        
        # 사용자가 대여 중인 우산 정보 업데이트
        ##cursor.execute("UPDATE user SET rp = FALSE WHERE user_id = %s", (session['user_id'],))
        
        conn.commit()
        print("고장 처리되었습니다. 우산을 반납할 수 있는 장소로 이동하세요.")
        
    except Exception as e:
        conn.rollback()
        print("고장 처리 중 오류가 발생했습니다.")
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()
    
    # 우산을 반납할 장소로 이동
    return redirect(url_for('status.KUmbrella', location=destination))

'''
from flask import Blueprint, session, redirect, url_for, flash
from db import get_db_connection

broken_bp = Blueprint('broken', __name__)

@broken_bp.route('/broken_process', methods=['GET', 'POST'])
def broken_process():
    # 세션에서 대여된 우산의 정보 가져오기
    original_umbrella_id = session.get('original_umbrella_id')
    original_location = session.get('original_location')  # 우산이 대여되었던 위치
    destination_location = session.get('destination_location')  # 반납할 예정이었던 위치
    destination_slot = session.get('destination_slot')  # 반납할 예정이었던 슬롯
    
    if not original_umbrella_id or not original_location or not destination_location:
        #flash("잘못된 요청입니다. 대여 정보를 확인해주세요.")
        return redirect(url_for('status.KUmbrella'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. 고장난 우산의 상태를 4 (고장 상태)로 변경
        update_query = f"""
            UPDATE {original_location['location']}
            SET status = 4, renter_id = NULL
            WHERE umbrella_id = %s
        """
        cursor.execute(update_query, (original_umbrella_id,))
        
        # 2. 반납 예정이었던 위치의 상태를 5 (등록 가능한 상태)로 변경
        update_query = f"""
            UPDATE {destination_location}
            SET status = 5, umbrella_id = NULL, renter_id = NULL
            WHERE slot = %s AND status = 3
        """
        cursor.execute(update_query, (destination_slot,))
        
        conn.commit()

        # 3. 우산 상태를 고장 상태로 업데이트 (umbrella 테이블)
        cursor.execute("""
            UPDATE umbrella
            SET status = 4
            WHERE umbrella_id = %s
        """, (original_umbrella_id,))

        # 고장 처리 완료 후 사용자에게 알림
        #flash("우산이 고장으로 처리되었습니다. 반납 장소로 이동해주세요.")
    except Exception as e:
        conn.rollback()
        #flash(f"고장 처리 중 오류가 발생했습니다: {e}")
        print("Error during broken process:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('status.KUmbrella'))
