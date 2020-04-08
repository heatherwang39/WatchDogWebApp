import requests    # To install: pip install requests
import S3_service as S3
import logging
import boto3
from botocore.exceptions import ClientError
import cv2

s3 = boto3.resource('s3')
object_acl = s3.ObjectAcl('a3user','1586291769.mp4')
response = object_acl.put(ACL='public-read')
if response:
    vim = cv2.VideoCapture('https://a3user.s3.amazonaws.com/1586291769.mp4')
    fps = vim.get(cv2.CAP_PROP_FPS)
    period = vim.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    print(period)
    response = object_acl.put(ACL='private')



