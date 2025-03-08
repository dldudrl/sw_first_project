import os

class Config:
    SECRET_KEY = os.urandom(24)
    KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY', '1a32cc25cda2d539a52cbe6823886114')
    KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI', 'http://127.0.0.1:8000/oauth')
    KAKAO_AUTHORIZATION_BASE_URL = 'https://kauth.kakao.com/oauth/authorize'
    KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
    KAKAO_API_BASE_URL = 'https://kapi.kakao.com'
