import json
import boto3
import datetime 
import requests
from requests_aws4auth import AWS4Auth


endpoint = 'https://search-photos-543puc4hnzrvr4oyaxiqfi7y24.us-east-1.es.amazonaws.com'
username = 'master'
password = 'password'
search_url = endpoint + '/photos/_search?q='

def lambda_handler(event, context):
    # this function should return list of URL that is pointed to the pictures in S3
    search = event['queryStringParameters']['q']
    if search == "allPictures" :
       # return all pictures in the database
       # query all pictture in elastic
       # query response -> all url -> url list
       # query end
       photo_urls = retrive_all_photos()
       return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'body': json.dumps(photo_urls)
        }
    
    else:
        print(search)
        labels = get_labels_from_lex(search)
        photo_urls = []
        photo_urls = search_photos(labels)
        
        return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'body': json.dumps(photo_urls)
        }
    
def get_labels_from_lex(search):
    botClient = boto3.client('lex-runtime')
    lexResponse = botClient.post_text(
        botName="searchKeyWords",
        botAlias="Searchfor",
        userId="eleven11Li",
        sessionAttributes={},
        requestAttributes={},
        inputText=search,
        activeContexts=[]
    )
    labels = []
    if lexResponse['slots']['a']:
        labels.append(lexResponse['slots']['a'])
    
    if lexResponse['slots']['b']:
        labels.append(lexResponse['slots']['b'])
        
    if len(labels) == 1:
        lexResponse = botClient.post_text(
            botName="searchKeyWords",
            botAlias="Searchfor",
            userId="eleven11Li",
            sessionAttributes={},
            requestAttributes={},
            inputText="dog",
            activeContexts=[]
        )
   
    return labels
    
def retrive_all_photos():
    photo_urls = []
    url = search_url + '*'
    response = requests.get(url, auth=(username, password)).json()
    results = response['hits']['hits']
    for result in results:
        bucket = result['_source']['bucket']
        name = result['_source']['objectKey']
        photo_url = 'https://{}.s3.amazonaws.com/{}'.format(bucket,name)
        photo_urls.append(photo_url)
    return photo_urls
    

def search_photos(labels):
    photo_urls = []
    for label in labels:
        url = search_url + label
        response = requests.get(url, auth=(username, password)).json()
        results = response['hits']['hits']
        for result in results:
            bucket = result['_source']['bucket']
            name = result['_source']['objectKey']
            photo_url = 'https://{}.s3.amazonaws.com/{}'.format(bucket,name)
            photo_urls.append(photo_url)
    
    return list(set(photo_urls))
        
        
    
    
