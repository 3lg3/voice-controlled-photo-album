import json
import boto3
import base64

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket = "photobuckethw2"
    
    filename = event['filename']
    image_64 = event['content']
    tags = event['tags']
    print(tags)
    tags_dic = dict.fromkeys(tags, "tag")
    s3_client.put_object(Body=base64.b64decode(image_64), Metadata=tags_dic, ACL="public-read", Key=filename, Bucket=bucket)
    
   
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
