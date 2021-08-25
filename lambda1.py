import json
import boto3
import datetime 
import requests
from requests_aws4auth import AWS4Auth


endpoint = 'https://search-photos-543puc4hnzrvr4oyaxiqfi7y24.us-east-1.es.amazonaws.com'
username = 'master'
password = 'password'

def lambda_handler(event, context):
    # TODO implement
    s3 = boto3.client('s3')
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    name = event["Records"][0]["s3"]["object"]["key"]
    meta_response = s3.head_object(Bucket=bucket, Key=name)
    meta_labels = list(meta_response['Metadata'].keys())
    rek_labels = get_rekognition_labels(bucket, name)
    labels = list(set(meta_labels + rek_labels))
    response = index_photo(bucket, name, labels)
    print(response)
    return {
        'statusCode': 200,
        'body': json.dumps('Photo Indexed!')
    }


# return a list of labels detected by AWS Rekognition
def get_rekognition_labels(bucket, name):
    rekog = boto3.client('rekognition')
    image_json = {
        "S3Object": {
            "Bucket": bucket,
            "Name": name
        }
    }
    
    response = rekog.detect_labels(Image=image_json, MaxLabels= 5, MinConfidence=85)
    labels = []
    for record in response['Labels']:
        labels.append(record['Name'].lower())
    
    return labels

# index the photo with its (Rekognition) label(s) and custom label(s)
# https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-aws-integrations.html
def index_photo(bucket, name, labels):
    url = endpoint + '/photos/lambda-type'
    headers = { "Content-Type": "application/json" }
    document = {
        "objectKey" : name,
        "bucket" : bucket,
        "createdTimeStamp" : datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "labels" : labels
    }
    print(document)
    response = requests.post(url, auth=(username, password), json=document, headers=headers)
    return response
