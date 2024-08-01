from datetime import datetime, timedelta
import uuid
from flask import Blueprint, jsonify, request
from app.auth.utils import hash_password, verify_password, generate_jwt, decode_jwt
from app.auth.models import user_table, token_table
from app.auth.schemas import UserSchema, TokenSchema
from boto3.dynamodb.conditions import Key
from app.config import Config
bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    schema = UserSchema()
    user_data = schema.load(data)

    username = user_data['username']
    password = user_data['password']
    hashed_password = hash_password(password)

    response = user_table.query(
        KeyConditionExpression=Key('userId').eq(username)
    )
    if response.get('Items'):
        return jsonify({'error': 'Username already exists'}), 400

    userId = str(uuid.uuid4())
    user_table.put_item(Item={
        'userId': username,
        'username': username,
        'password': hashed_password,
        'first_name': user_data.get('first_name'),
        'last_name': user_data.get('last_name'),
        'created_at': datetime.now().isoformat()
    })

    return jsonify({'message': 'User registered successfully'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    schema = UserSchema(only=['username', 'password'])
    user_data = schema.load(data)

    username = user_data['username']
    password = user_data['password']

    response = user_table.query(
        KeyConditionExpression=Key('userId').eq(username)
    )
    items = response.get('Items')
    if not items:
        return jsonify({'error': 'User not found'}), 404

    user = items[0]
    if not verify_password(user['password'], password):
        return jsonify({'error': 'Incorrect password'}), 401

    device_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_EXPIRATION)
    refresh_expires_at = datetime.utcnow(
    ) + timedelta(seconds=Config.JWT_REFRESH_EXPIRATION)

    # Convert datetime to ISO 8601 string
    expires_at_str = expires_at.isoformat()
    refresh_expires_at_str = refresh_expires_at.isoformat()
    tokenId = str(uuid.uuid4())
    access_token = generate_jwt(user['userId'], device_id, tokenId)
    refresh_token = generate_jwt(
        user['userId'], device_id, tokenId, is_refresh_token=True)
    token_table.put_item(Item={
        'tokenId': tokenId,
        'userId': user['userId'],
        'device_id': device_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at_str,
        'refresh_expires_at': refresh_expires_at_str
    })

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 200


@bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    payload = decode_jwt(refresh_token)
    if not payload:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401

    user_id = payload['user_id']
    device_id = payload['device_id']
    tokenId = payload['tokenId']

    response = token_table.query(
        Key={'tokenId': tokenId}
    )
    items = response.get('Items')
    if not items:
        return jsonify({'error': 'User not found'}), 404

    token_data = next(
        (item for item in items if item['device_id'] == device_id), None)
    if not token_data:
        return jsonify({'error': 'Invalid device ID'}), 401

    new_access_token = generate_jwt(user_id, device_id, tokenId)
    new_refresh_token = generate_jwt(
        user_id, device_id, tokenId, is_refresh_token=True)

    token_table.update_item(
        Key={'tokenId': tokenId},
        ExpressionAttributeValues={
            ':access_token': new_access_token,
            ':refresh_token': new_refresh_token,
            ':expires_at': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_EXPIRATION),
            ':refresh_expires_at': datetime.utcnow() + timedelta(seconds=Config.JWT_REFRESH_EXPIRATION)
        }
    )

    return jsonify({'access_token': new_access_token, 'refresh_token': new_refresh_token}), 200


@bp.route('/logout', methods=['POST'])
def logout():
    # Extract access token from the request headers or body
    access_token = request.headers.get('Authorization')
    if not access_token:
        return jsonify({'error': 'Access token is required'}), 400

    payload = decode_jwt(access_token)
    if not payload:
        return jsonify({'error': 'Invalid or expired access token'}), 401

    # Delete the token from the database
    token_table.delete_item(
        Key={'tokenId': payload['tokenId']}
    )

    return jsonify({'message': 'Logged out successfully'}), 200


@bp.route('/user', methods=['GET'])
def get_user_details():
    access_token = request.headers.get('Authorization')
    if not access_token:
        return jsonify({'error': 'Authorization header is required'}), 401

    payload = decode_jwt(access_token)
    if not payload:
        return jsonify({'error': 'Invalid or expired access token'}), 401

    token_id = payload['tokenId']
    response = token_table.get_item(Key={'tokenId': token_id})
    token_data = response.get('Item')
    if not token_data:
        return jsonify({'error': 'Token not found or has been invalidated'}), 401

    user_id = payload['user_id']
    response = user_table.get_item(Key={'userId': user_id})
    user = response.get('Item')

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'userId': user['userId'],
        'username': user['username'],
        'first_name': user['first_name'],
        'last_name': user['last_name']
    }), 200


def get_user_details_locally(access_token):
    payload = decode_jwt(access_token)
    if not payload:
        return jsonify({'error': 'Invalid or expired access token'}), 401
    user_id = payload['user_id']
    response = user_table.get_item(Key={'userId': user_id})
    user = response.get('Item')

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'userId': user['userId'],
        'username': user['username'],
        'first_name': user['first_name'],
        'last_name': user['last_name']
    }), 200


@bp.route('/cleanup', methods=['POST'])
def cleanup_expired_tokens():
    current_time = datetime.utcnow()
    response = token_table.scan(
        FilterExpression='expires_at < :current_time',
        ExpressionAttributeValues={':current_time': current_time.isoformat()}
    )
    expired_tokens = response.get('Items', [])

    for token in expired_tokens:
        token_table.delete_item(
            Key={'tokenId': token['tokenId']}
        )

    return jsonify({'message': f"Deleted {len(expired_tokens)} expired tokens."}), 200
