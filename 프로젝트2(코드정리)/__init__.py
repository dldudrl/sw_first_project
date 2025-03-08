from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Secret key for session management
    app.secret_key = os.urandom(24)
    
    # CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Configuration
    app.config['KAKAO_REST_API_KEY'] = os.getenv('KAKAO_REST_API_KEY')
    app.config['KAKAO_REDIRECT_URI'] = os.getenv('KAKAO_REDIRECT_URI')
    app.config['KAKAO_AUTHORIZATION_BASE_URL'] = 'https://kauth.kakao.com/oauth/authorize'
    app.config['KAKAO_TOKEN_URL'] = 'https://kauth.kakao.com/oauth/token'
    app.config['KAKAO_API_BASE_URL'] = 'https://kapi.kakao.com'

    # Register blueprints or routes
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
