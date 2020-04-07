import logging
import boto3
from botocore.exceptions import ClientError


def upload_file(file, bucket='a3user', filename = None, file_directory="videos/"):
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
    bucket.Object(file_directory+filename).put(Body=file.read())
    print("File uploaded to s3: "+filename)
    return True

