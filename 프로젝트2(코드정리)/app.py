from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
load_dotenv()
import unittest
from app import app
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 세션을 위한 시크릿 키 설정
csrf = CSRFProtect(app)
# 세션에 저장되는 사용자 정보의 키
SESSION_KEY = 'user_info'

# Kakao API 설정
KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY', '1a32cc25cda2d539a52cbe6823886114')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI', 'http://127.0.0.1:8000/oauth')
KAKAO_AUTHORIZATION_BASE_URL = 'https://kauth.kakao.com/oauth/authorize'
KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
KAKAO_API_BASE_URL = 'https://kapi.kakao.com'

def get_oauth_session(state=None, token=None):
    return OAuth2Session(
        client_id=KAKAO_REST_API_KEY,
        redirect_uri=KAKAO_REDIRECT_URI,
        state=state,
        token=token
    )
    
class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.app.post('/login')
        self.assertEqual(response.status_code, 302)  # Redirect to Kakao

@app.route('/')
def index():
    return render_template('ex01_login.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        oauth = get_oauth_session()
        authorization_url, state = oauth.authorization_url(KAKAO_AUTHORIZATION_BASE_URL)
        session['oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        app.logger.error(f"Error during login: {e}")
        return render_template('error.html', message="Failed to start OAuth authorization"), 500

@app.route('/oauth')
def oauth_callback():
    if 'error' in request.args:
        error = request.args['error']
        return render_template('error.html', message=f"OAuth error: {error}"), 400

    try:
        oauth = get_oauth_session(state=session.get('oauth_state'))
        token = oauth.fetch_token(KAKAO_TOKEN_URL, authorization_response=request.url, client_secret=KAKAO_REST_API_KEY)
        
        response = oauth.get(f"{KAKAO_API_BASE_URL}/v2/user/me", headers={'Authorization': f'Bearer {token["access_token"]}'})
        if response.status_code == 200:
            kakao_data = response.json()
            user_info = {
                "email": kakao_data['kakao_account'].get('email'),
                "gender": kakao_data['kakao_account'].get('gender'),
                "profile_nickname": kakao_data['properties'].get('nickname'),
                "profile_image": kakao_data['properties'].get('thumbnail_image'),
                "birthday": kakao_data['kakao_account'].get('birthday')
            }
            session[SESSION_KEY] = user_info
            return redirect(url_for('show_user_info'))
        else:
            return render_template('error.html', message="Failed to fetch user information"), response.status_code
    except Exception as e:
        app.logger.error(f"Error during OAuth callback: {e}")
        return render_template('error.html', message="Failed to complete OAuth process"), 500

@app.route('/user_info')
def show_user_info():
    user_info = session.get(SESSION_KEY)
    if user_info:
        return render_template('ex02_userinfo.html', user_info=user_info)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop(SESSION_KEY, None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # unittest.main()
    app.run(debug=True, port=8000)
    
