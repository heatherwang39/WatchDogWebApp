from typing import List

import boto3

def table_create():

    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')

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
    dynamodb = boto3.resource('dynamodb')
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
    dynamodb = boto3.resource('dynamodb')
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
    dynamodb = boto3.resource('dynamodb')
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

