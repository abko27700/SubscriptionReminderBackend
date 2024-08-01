import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import Config


def hash_password(password):
    return generate_password_hash(password)


def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)


def generate_jwt(user_id, device_id, tokenId, is_refresh_token=False):
    expiration = timedelta(
        seconds=Config.JWT_REFRESH_EXPIRATION if is_refresh_token else Config.JWT_ACCESS_EXPIRATION)
    payload = {
        'user_id': user_id,
        'device_id': device_id,
        'exp': datetime.utcnow() + expiration,
        'iat': datetime.utcnow(),
        'tokenId': tokenId
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def extract_token_from_header(header):
    if header and header.startswith("Bearer "):
        return header[len("Bearer "):]
    return None


def decode_jwt(auth_header):
    try:
        token = extract_token_from_header(auth_header)
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        # print("Invalid token")
        return None
    except Exception as e:
        # print(f"An unexpected error occurred: {e}")
        return None
