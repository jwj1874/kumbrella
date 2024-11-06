# auth_routes.py
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db import get_db_connection
import pymysql
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/create_account', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('id')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user (user_id, password, name, phone, email)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, password, name, phone, email))
            conn.commit()
            flash("User registered successfully.")
            return redirect(url_for('auth.index'))
        except pymysql.IntegrityError:
            flash("User ID already exists. Please choose a different ID.")
            return redirect(url_for('auth.register'))
        finally:
            cursor.close()
            conn.close()
    return render_template('create_account.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('id')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id = %s AND password = %s", (user_id, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['logged_in'] = True
            session['user_id'] = user_id
            return redirect(url_for('status.KUmbrella'))
        else:
            flash("Invalid credentials. Please try again.")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))
