from flask import Flask
from auth_routes import auth_bp
from status_routes import status_bp
from rental_routes import rental_bp
from regist_routes import register_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 블루프린트 등록
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(status_bp)
app.register_blueprint(rental_bp)
app.register_blueprint(register_bp, url_prefix='/register')

if __name__ == '__main__':
    app.run(debug=True)
