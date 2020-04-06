# encoding:utf-8
import json

import requests

# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=R7FBLMwCGf7HCI8KTdCkmZyZ&client_secret=rYLsAPFEadylhZvB0pzA3lBUlteN9Ut6'
response = requests.get(host)
if response:
    ret = response.json()
    access_token = ret['access_token']
    print(access_token)