import boto3
import time
from botocore.exceptions import ClientError


def lambdaForExpire():

    # Get user list and expire time, put into a dictionary
    user_expire = get_all_users_and_expire()

    # Get all the user directory

    expired_video_user = get_user_videos(user_expire)

    # Get and delete S3 object
    expire_keys = get_expire_objects(expired_video_user)

    delete_all_items(expire_keys)

    delete_expire_db(expired_video_user)

def get_all_users_and_expire():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3_user_map')
    response = table.scan()

    user_expire = {}
    for person in response['Items']:
        user_expire[int(person['user_id'])] = int(time.time())-int(person['saving_period'])

    return user_expire

def get_user_videos(user_expire):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3users')
    response = table.scan()

    expired_video_user = []

    for video in response['Items']:
        file_name = int(video['filename'])
        user_id = int(video['user_id'])
        expire = user_expire[user_id]
        if file_name < expire:
            expired_video_user.append([file_name,user_id])

    return expired_video_user

def get_expire_objects(expired_video_user):
    conn = boto3.client('s3')
    expired_keys = []
    for key in conn.list_objects(Bucket='a3video')['Contents']:
        for video_user in expired_video_user:
            if key['Key'].startswith(str(video_user[1])+"/"+str(video_user[0])):
                expired_keys.append({'Key':key['Key']})
    return expired_keys

def delete_all_items(expired_keys):
    if len(expired_keys) != 0:
        client = boto3.client('s3')
        response = client.delete_objects(
            Bucket='a3video',
            Delete={
                'Objects': expired_keys,
            }
        )

def delete_expire_db(expired_video_user):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('A3users')
    for video_user in expired_video_user:
        try:
            response = table.delete_item(
                Key={
                    'user_id': str(video_user[1]),
                    'filename': str(video_user[0])
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            print("DeleteItem succeeded")



lambdaForExpire()