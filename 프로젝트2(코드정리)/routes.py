from flask import Blueprint, app, render_template, request, redirect, url_for, session
from requests_oauthlib import OAuth2Session
import os

main = Blueprint('main', __name__)

# Retrieve Kakao API configuration from environment
KAKAO_REST_API_KEY = os.getenv('1a32cc25cda2d539a52cbe6823886114')
KAKAO_REDIRECT_URI = os.getenv('http://127.0.0.1:8000/oauth')
KAKAO_AUTHORIZATION_BASE_URL = os.getenv('https://kauth.kakao.com/oauth/authorize')
KAKAO_TOKEN_URL = os.getenv('https://kauth.kakao.com/oauth/token')
KAKAO_API_BASE_URL = os.getenv('https://kapi.kakao.com')

def get_oauth_session(state=None, token=None):
    return OAuth2Session(
        client_id=KAKAO_REST_API_KEY,
        redirect_uri=KAKAO_REDIRECT_URI,
        state=state,
        token=token
    )

@main.route('/')
def index():
    return render_template('ex01_login.html')

@main.route('/login', methods=['POST'])
def login():
    try:
        oauth = get_oauth_session()
        authorization_url, state = oauth.authorization_url(KAKAO_AUTHORIZATION_BASE_URL)
        session['oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        app.logger.error(f"Error during login: {e}")
        return render_template('error.html', message="Failed to start OAuth authorization"), 500

@main.route('/oauth')
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
            session['user_info'] = user_info
            return redirect(url_for('.show_user_info'))
        else:
            return render_template('error.html', message="Failed to fetch user information"), response.status_code
    except Exception as e:
        app.logger.error(f"Error during OAuth callback: {e}")
        return render_template('error.html', message="Failed to complete OAuth process"), 500

@main.route('/user_info')
def show_user_info():
    user_info = session.get('user_info')
    if user_info:
        return render_template('ex02_userinfo.html', user_info=user_info)
    else:
        return redirect(url_for('.index'))

@main.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect(url_for('.index'))
