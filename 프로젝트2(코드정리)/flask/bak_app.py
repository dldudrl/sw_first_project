from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from requests_oauthlib import OAuth2Session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 세션을 위한 시크릿 키 설정

# 세션에 저장되는 사용자 정보의 키
SESSION_KEY = 'user_info'

# Kakao API 설정
KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY', '1a32cc25cda2d539a52cbe6823886114')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI', 'http://127.0.0.1:8000/oauth')
KAKAO_AUTHORIZATION_BASE_URL = 'https://kauth.kakao.com/oauth/authorize'
KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
KAKAO_API_BASE_URL = 'https://kapi.kakao.com'

# OAuth2 세션 생성
oauth = OAuth2Session(client_id=KAKAO_REST_API_KEY, redirect_uri=KAKAO_REDIRECT_URI)

@app.route('/')
def index():
    return render_template('ex01_login.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        authorization_url, _ = oauth.authorization_url(KAKAO_AUTHORIZATION_BASE_URL)
        return redirect(authorization_url)
    except Exception as e:
        app.logger.error(f"Error during login: {e}")
        return jsonify({"error": "Failed to start OAuth authorization"}), 500

@app.route('/oauth')
def oauth_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code is missing"}), 400

    try:
        # 액세스 토큰 요청
        token = oauth.fetch_token(KAKAO_TOKEN_URL, authorization_response=request.url, code=code, client_secret=KAKAO_REST_API_KEY)

        # 액세스 토큰을 사용하여 사용자 정보를 가져옵니다.
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
            
            # 세션에 사용자 정보를 저장합니다.
            session[SESSION_KEY] = user_info
            return redirect(url_for('show_user_info'))
        else:
            return jsonify({"error": "Failed to fetch user information"}), response.status_code
    except Exception as e:
        app.logger.error(f"Error during OAuth callback: {e}")
        return jsonify({"error": "Failed to complete OAuth process"}), 500

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
    app.run(debug=True, port=8000)
