from flask import Flask
from auth_routes import auth_bp
from status_routes import status_bp
from rental_routes import rental_bp
from regist_routes import register_bp
from return_routes import return_bp
from broken_routes import broken_bp
from point_routes import point_bp
from datetime import timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 세션 파일 시스템 저장
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/path/to/session/files'  # 세션 파일 저장 경로
app.config['SESSION_PERMANENT'] = True  # 세션을 영구적으로 유지
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 세션 만료 시간 1시간 설정
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 세션 쿠키 보안 설정

# 블루프린트 등록
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(status_bp)
app.register_blueprint(rental_bp)
app.register_blueprint(register_bp, url_prefix='/register')
app.register_blueprint(return_bp)
app.register_blueprint(broken_bp, url_prefix='/broken')
app.register_blueprint(point_bp, url_prefix='/point')


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug=True)
