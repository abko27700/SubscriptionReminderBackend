import boto3
from botocore.exceptions import ClientError
from app.config import Config

dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
subscription_table = dynamodb.Table(Config.SUBSCRIPTIONS_TABLE_NAME)
