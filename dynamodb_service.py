from typing import List

import boto3
from boto3.dynamodb.conditions import Key, Attr
import time
import random


def table_create():

    # Get the service resource.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName='A3users',
        KeySchema=[
            {
                'AttributeName': 'user_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'filename',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'filename',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

def put_user_video(user_id, filename,count,finish_count,finish_details,start_time):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3users')

    table.put_item(
        Item={
            'user_id': user_id,
            'filename': filename,
            'start_time': start_time,
            'count':count,
            'finish_count': finish_count,
            'finish_details':finish_details,
            'complete': False,
        }
    )


def add_finish_counter(user_id:str, filename:str, finish_counter:int, finish_detail: dict, people_num:int):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3users')
    response = table.get_item(
        Key={
            'user_id': user_id,
            'filename':filename
        }
    )
    counters = response['Item']['count']
    counters_int = [int(item) for item in counters]
    start_time = response['Item']['start_time']
    finish_counters = response['Item']['finish_count']
    finish_details = response['item']['finish_details']
    finish_counters[str(finish_counter)] = people_num
    finish_details[str(finish_counter)] = finish_detail
    put_user_video(user_id,filename,counters_int,finish_counters, finish_details, start_time)

#put_user_video('temp','1586408994.mp4',[200,400],{str(200):20},1586129400)
#add_finish_counter('temp','1586408994.mp4',400,30)

def get_start_count_finish(user_id:str, filename:str):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3users')
    response = table.get_item(
        Key={
            'user_id': user_id,
            'filename': filename
        }
    )
    counters = response['Item']['count']
    counters_int = [int(item) for item in counters]
    start_time = response['Item']['start_time']
    finish_counters = response['Item']['finish_count']
    finish_details = response['Item']['finish_details']
    return start_time,counters_int,finish_counters, finish_details

def query_user_videos(user_id: str):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3users')
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    ret_videos = []
    videos = response['Items']
    for video in videos:
        ret_videos.append(video['filename'])
    return ret_videos

def get_userID(email):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('A3_user_map')
    response = table.get_item(
        Key={
            'email': email
        }
    )

    if 'Item' in response.keys():
        return str(response['Item']['user_id'])
    else:
        user_id = str(int(time.time()))+str(random.randint(0,100))
        put_user_id(email, user_id)
        return user_id

def get_saving_time(email):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('A3_user_map')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    return int(response['Item']['saving_period'])


def put_user_id(email, user_id, saving_period = 2592000):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('A3_user_map')

    table.put_item(
        Item={
            'email': email,
            'user_id': user_id,
            'saving_period': saving_period
        }
    )

def put_saving_time(email, saving_Days):
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('A3_user_map')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    user_id = int(response['Item']['user_id'])
    saving_period = int(saving_Days)*86400
    put_user_id(email,user_id,saving_period)

#put_user_id('temp@email.com', 1010)
#get_userID('temp@mail.com')
# print(query_user_videos('temp'))
