import os
import sys
import boto3
import hashlib


def main():

    URL = os.environ['TADPOLES_SQS_QUEUE_URL']

    client = boto3.client('sqs')

    with open(sys.argv[1]) as f:
        done = False
        while True:
            entries = []
            for i in range(10):
                try:
                    body = next(f)
                except StopIteration:
                    done = True
                    break
                entries.append(dict(
                    Id=hashlib.md5(bytes(body, 'utf8')).hexdigest(),
                    MessageBody=body
                ))
            response = client.send_message_batch(
                QueueUrl=URL,
                Entries=entries
            )
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception('Bad response: %r' % response)
               
            if done:
                break
                
if __name__ == "__main__":
    main()    
