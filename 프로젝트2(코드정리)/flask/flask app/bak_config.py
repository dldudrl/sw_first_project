import os

class Config:
    KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY', 'default_kakao_rest_api_key')

# 로컬에서 실행 시 사용할 개발 설정
class DevelopmentConfig(Config):
    DEBUG = True
    KAKAO_REST_API_KEY = 'your_development_kakao_rest_api_key_here'

# 배포 시 사용할 프로덕션 설정
class ProductionConfig(Config):
    DEBUG = False
