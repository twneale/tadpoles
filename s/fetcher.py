import io
import os
import json
import boto3
import base64
import http.client
from datetime import datetime
from botocore.exceptions import ClientError



def get_cookie():

    # Whatever you want the secret name of your AWS secret containing the tadpoles cookie to be.
    secret_name = os.environ['TADPOLES_COOKIE_AWS_SECRET_NAME']
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
    # Your code goes here. 
    return json.loads(secret)['Cookie']


s3 = boto3.client('s3')
sqs = boto3.client('sqs')


def lambda_handler(event, context):
    conn = http.client.HTTPSConnection("www.tadpoles.com")
    HEADERS = {
      'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
      'Accept': 'application/json, text/javascript, */*; q=0.01',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'X-TADPOLES-UID': 'twneale@gmail.com',
      'X-Requested-With': 'XMLHttpRequest',
      'Connection': 'keep-alive',
      'Referer': 'https://www.tadpoles.com/parents',
      'Cookie': get_cookie()
    }
    URL = "/remote/v1/obj_attachment?obj={key}&key={attachment}"

    succeeded = []
    for record in event['Records']:
        data = json.loads(record['body'])
        if data['mime_type'] != 'image/jpeg':
            continue

        key = datetime.fromtimestamp(data['create_time']).strftime('tadpoles/{child}/%Y/%m/%d/H=%H,M=%M,S=%S.jpg'.format(**data))

        file_name = '/tmp/' + key.replace('/', '_')
        
        do_fetch = False
        try:
            response = s3.head_object(Bucket=os.environ['TADPOLES_S3_BUCKET'], Key=key)
        except Exception as exc:
            if exc.response['Error']['Code'] == '404':
                do_fetch = True
        
        # Skip the fetch if already in S3.    
        if not do_fetch:
            data.update(skipped=True)
            succeeded.append(dict(Id=record['MessageId'], ReceiptHandle=record['ReceiptHandle']))
            continue
        
        url = URL.format(**data)
        conn.request('GET', url, headers=HEADERS)
        response = conn.getresponse()
        if int(response.status) != 200:
            raise Exception('Bad response: %r' % response.status)

        img = response.read()
        with open(file_name, 'wb') as f:
             f.write(img)
        try:
            response = s3.put_object(Bucket=os.environ['TADPOLES_S3_BUCKET'] Key=key, Body=img)
            print(response)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
        else:
            succeeded.append(dict(Id=record['MessageId'], ReceiptHandle=record['ReceiptHandle']))

    if succeeded:
        response = sqs.delete_message_batch(
          QueueUrl=os.environ['TADPOLES_SQS_QUEUE_URL'],
          Entries=succeeded
        )
        import pprint
        pprint.pprint(response)
        
    return {
        'statusCode': 200,
        'body': json.dumps({})
    }
        
if __name__ == "__main__":
    while True:
        resp = sqs.receive_message(
          QueueUrl=os.environ['TADPOLES_SQS_QUEUE_URL'],
          MaxNumberOfMessages=10
        )
        if not resp['Messages']: break
        resp['Records'] = resp['Messages']
        for rec in resp['Records']:
            rec['body'] = rec.pop('Body')
        lambda_handler(resp, None)
