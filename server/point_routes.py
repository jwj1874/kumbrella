from flask import Blueprint, flash
from db import get_db_connection

point_bp = Blueprint('point', __name__)

@point_bp.route('/deduct_renter_points', methods=['POST'])
def deduct_renter_points(user_id):
    """
    대여자의 포인트를 3점 차감
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        point_update_query = """
            UPDATE user
            SET point = point - 3
            WHERE user_id = %s
        """
        cursor.execute(point_update_query, (user_id,))
        conn.commit()
        print(f"Deducted 3 points from renter {user_id}")
    except Exception as e:
        conn.rollback()
        #flash("An error occurred while deducting points from the renter.")
        print("Error in deduct_renter_points:", e)
    finally:
        cursor.close()
        conn.close()


@point_bp.route('/reward_owner_points', methods=['POST'])
def reward_owner_points(umbrella_id):
    """
    우산 소유자에게 포인트 1점 추가
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 우산 소유자 ID 가져오기
        cursor.execute("""
            SELECT user_id FROM umbrella WHERE umbrella_id = %s
        """, (umbrella_id,))
        owner_id = cursor.fetchone()
        if owner_id and owner_id['user_id']:
            owner_point_update_query = """
                UPDATE user
                SET point = point + 1
                WHERE user_id = %s
            """
            cursor.execute(owner_point_update_query, (owner_id['user_id'],))
            conn.commit()
            print(f"Rewarded 1 point to owner {owner_id['user_id']}")
        else:
            print(f"No owner found for umbrella_id {umbrella_id}")
    except Exception as e:
        conn.rollback()
        #flash("An error occurred while rewarding points to the umbrella owner.")
        print("Error in reward_owner_points:", e)
    finally:
        cursor.close()
        conn.close()
