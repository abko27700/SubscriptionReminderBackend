import boto3
from botocore.exceptions import ClientError
from app.config import Config

dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
user_table = dynamodb.Table(Config.USERS_TABLE_NAME)
token_table = dynamodb.Table(Config.TOKENS_TABLE_NAME)
