import os

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')
    MONGO_URI = os.environ.get('MONGO_URI')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    PORT = int(os.environ.get('PORT', 5000))
