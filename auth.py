import boto3
import json
import twitter
from settings import *


def get_sign_in_token(event, context):
    client = twitter.UserClient(
        CONSUMER_KEY,
        CONSUMER_SECRET,
    )
    token = client.get_signin_token(
        callback_url=CALLBACK_URL
    )
    return {
        'location': token.auth_url,
        'cookie': 'token=%s;PATH=/;' % (
            token.oauth_token_secret,
        ),
    }


def get_access_token(event, context):
    token = event['queryParams']['oauth_token']
    secret = event['headers']['Cookie'].split('=')[1]
    client = twitter.UserClient(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        token,
        secret,
    )
    token = client.get_access_token(event['queryParams']['oauth_verifier'])

    # save the token to dynamodb
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        endpoint_url=DYNAMODB_ENDPOINT,
    )
    table = dynamodb.Table(DYNAMODB_TABLE)
    table.put_item(
        Item={
            'user_id': int(token['user_id']),
            'app_name': TWITTER_APP_NAME,
            'data': json.dumps(token),
        },
        #ConditionExpression='attribute_not_exists',
    )

    return {
        'token': token,
    }
