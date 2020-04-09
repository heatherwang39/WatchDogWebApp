event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2020-04-09T18:31:50.206Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROAQ5QTXE6E5PMRHY2XX:user603413=seanxiaoyi.wang@mail.utoronto.ca'}, 'requestParameters': {'sourceIPAddress': '184.145.92.35'}, 'responseElements': {'x-amz-request-id': '31E4EFC30CFA62E6', 'x-amz-id-2': '0P3Ux4miOe2EFADitwHfIcci+pKbamcELwunn99VmdPNJxviQgyWXTEznNBZDFIxdU2iOlnK6elxV1Wwd4PowuAYB41vjly7'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '9b9ace04-f990-4b5b-bb6d-afc6b0be51e5', 'bucket': {'name': 'a3video', 'ownerIdentity': {'principalId': 'AJG63JZJU7J8Y'}, 'arn': 'arn:aws:s3:::a3video'}, 'object': {'key': '1789/test_unprocessed.jpg', 'size': 83480, 'eTag': 'fc0cb210d62f7da39984491b942c78d7', 'sequencer': '005E8F6A162C62DA1F'}}}]}

events = event['Records'][0]['s3']['object']['key']
keys = events.split('/')
file_name = keys[-1]
print(folder, file_name)