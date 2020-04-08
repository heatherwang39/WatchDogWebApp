import logging
import boto3
from botocore.exceptions import ClientError
import image_process as ip
import requests
import cv2
import base64


def upload_file(file, bucket='a3user', filename=None, file_directory="videos/"):
    """Upload a file to an S3 bucket

    :param file_directory:
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if filename == None:
        filename = file.filename

    # Upload the file
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket)
    bucket.Object(file_directory + filename).put(Body=file.read())
    print("File uploaded to s3: " + filename)
    return True

def upload_cvimage(img, filename, bucket='a3user', file_directory="videos/"):
    """Upload a file to an S3 bucket

    :param img: openCV image file in MAT
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    img64 = ip.cv_to_64(img)
    f_read = base64.b64decode(img64)

    # If S3 object_name was not specified, use file_name

    # Upload the file
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket)
    bucket.Object(file_directory + filename).put(Body=f_read)
    print("File uploaded to s3: " + filename)
    return True



def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response

def file_setpublic(bucket_name, file_name):
    s3 = boto3.resource('s3')
    object_acl = s3.ObjectAcl(bucket_name, file_name)
    response = object_acl.put(ACL='public-read')
    if response:
        return True

def file_setprivate(bucket_name, file_name):
    s3 = boto3.resource('s3')
    object_acl = s3.ObjectAcl(bucket_name, file_name)
    response = object_acl.put(ACL='private')
    if response:
        return True

def get_image(bucket_name, file_name):
    import boto3
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, file_name)
    return obj.get()['Body']