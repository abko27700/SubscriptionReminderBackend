import uuid
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.auth.utils import decode_jwt
from app.subscriptions.schemas import SubscriptionSchema
from app.config import Config
from boto3.dynamodb.conditions import Key
from datetime import datetime
from app.subscriptions.models import subscription_table
bp = Blueprint('subscriptions', __name__)


@bp.route('/', methods=['POST'])
def create_subscription():
    userDetails = decode_jwt(
        request.headers.get('Authorization'))

    if not userDetails:
        return jsonify({'error': 'Invalid or expired access token'}), 401
    schema = SubscriptionSchema()
    try:
        request_data = request.get_json()
        request_data['userId'] = userDetails['user_id']  # Append the userId
        data = schema.load(request_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    subscriptionId = str(uuid.uuid4())
    subscription_table.put_item(Item={
        'subscriptionId': subscriptionId,
        'userId': data['userId'],
        'name': data['name'],
        'price': data['price'],
        'payment_method': data['payment_method'],
        'date': data['date'].isoformat(),
        'subscription_type': data['subscription_type'],
        'create_reminder': data['create_reminder']
    })

    return jsonify({'message': 'Subscription created successfully'}), 201


@bp.route('/<string:subscriptionId>', methods=['POST'])
def update_subscription(subscriptionId):
    userDetails = decode_jwt(request.headers.get('Authorization'))
    if not userDetails:
        return jsonify({'error': 'Invalid or expired access token'}), 401

    schema = SubscriptionSchema(partial=True)  # Allows partial updates
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('subscriptionId').eq(subscriptionId),
        )
        subscriptions = response.get('Items')
        if not subscriptions:
            return jsonify({'error': 'Subscription not found'}), 404

        subscription = subscriptions[0]
        if subscription['userId'] != userDetails['user_id']:
            return jsonify({'error': 'Forbidden'}), 403

        # Build the update expression and attribute maps
        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        for key, value in data.items():
            if key in ['name', 'price', 'payment_method', 'date', 'started_on', 'subscription_type', 'create_reminder', 'reminder_date']:
                placeholder = f"#{key}"
                update_expression += f"{placeholder} = :{key}, "
                expression_attribute_names[placeholder] = key
                expression_attribute_values[f":{key}"] = value

        # Remove the trailing comma and space
        update_expression = update_expression.rstrip(", ")

        # Update the item
        response = subscription_table.update_item(
            Key={
                'subscriptionId': subscriptionId,
                'userId': userDetails['user_id']  # Include the sort key
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

        return jsonify({'message': 'Subscription updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error updating subscription: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
def get_all_subscriptions():
    userDetails = decode_jwt(
        request.headers.get('Authorization'))
    if not userDetails:
        return jsonify({'error': 'Invalid or expired access token'}), 401
    user_id = userDetails['user_id']

    response = subscription_table.scan(
        FilterExpression=Key('userId').eq(user_id)
    )
    subscriptions = response.get('Items', [])

    return jsonify(subscriptions), 200


@bp.route('/<string:subscriptionId>', methods=['GET'])
def get_subscription(subscriptionId):
    # Decode JWT to get user details
    userDetails = decode_jwt(request.headers.get('Authorization'))
    if not userDetails:
        return jsonify({'error': 'Invalid or expired access token'}), 401

    # Retrieve the subscription item from DynamoDB
    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('subscriptionId').eq(subscriptionId),
        )
        subscriptions = response.get('Items')
        if not subscriptions:
            return jsonify({'error': 'Subscription not found'}), 404

        subscription = subscriptions[0]
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404

        if subscription['userId'] != userDetails['user_id']:
            return jsonify({'error': 'Forbidden'}), 403
    except Exception as e:
        return jsonify({'error': f'Error retrieving subscription: {str(e)}'}), 500

    return jsonify(subscription), 200


@bp.route('/<string:subscriptionId>', methods=['DELETE'])
def delete_subscription(subscriptionId):
    userDetails = decode_jwt(request.headers.get('Authorization'))
    if not userDetails:
        return jsonify({'error': 'Invalid or expired access token'}), 401

    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('subscriptionId').eq(subscriptionId),
        )
        subscriptions = response.get('Items')
        if not subscriptions:
            return jsonify({'error': 'Subscription not found'}), 404

        subscription = subscriptions[0]
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404

        if subscription['userId'] != userDetails['user_id']:
            return jsonify({'error': 'Forbidden'}), 403
    except Exception as e:
        return jsonify({'error': f'Error retrieving subscription: {str(e)}'}), 500

    try:
        subscription_table.delete_item(
            Key={
                'subscriptionId': subscriptionId,
                'userId': userDetails['user_id']  # Include the sort key
            }
        )
        return jsonify({'message': 'Subscription deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error deleting subscription: {str(e)}'}), 500
