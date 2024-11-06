from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        umbrella_id = request.form.get('umbrella_id')
        location = request.form.get('location')
        
        if not umbrella_id or not location:
            flash("All fields are required.")
            return redirect(url_for('register.register'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 등록 정보를 데이터베이스에 추가
        cursor.execute(
            "INSERT INTO umbrella (umbrella_id, available, Location) VALUES (%s, %s, %s)",
            (umbrella_id, 1, location)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Umbrella registered successfully!")
        return redirect(url_for('status.status_board', location=location))
    
    return render_template('regist.html')
