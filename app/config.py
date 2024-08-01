from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dummy_secret_key')
    JWT_ACCESS_EXPIRATION = int(os.environ.get(
        'JWT_ACCESS_EXPIRATION', 86400))  # 24 hours
    JWT_REFRESH_EXPIRATION = int(os.environ.get(
        'JWT_REFRESH_EXPIRATION', 2592000))  # 30 days
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    USERS_TABLE_NAME = os.environ.get('USERS_TABLE_NAME', 'Dummy_Users_Table')
    TOKENS_TABLE_NAME = os.environ.get(
        'TOKENS_TABLE_NAME', 'Dummy_Tokens_Table')
    SUBSCRIPTIONS_TABLE_NAME = os.environ.get(
        'SUBSCRIPTIONS_TABLE_NAME', 'Dummy_Subscriptions_Table')
    # Add other configurations if needed
