""" 
data_generation

"""

import json
import boto3
import base64


s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input (You may also check lambda test)
    key = event['s3_key']                               
    bucket = event['s3_bucket']                         
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:          
        image_data = base64.b64encode(f.read())      

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    
   
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

"""

image_classification

"""

import json
import base64
import boto3


runtime_client = boto3.client('sagemaker-runtime')                   


# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-10-21-15-50-08-352"



def lambda_handler(event, context):
    
    # Decode the image data
    
    image = base64.b64decode(event["body"]["image_data"])

    # Instantiate a Predictor
    response = runtime_client.invoke_endpoint(
                                        EndpointName=ENDPOINT,    
                                        Body=image,               
                                        ContentType='image/png'
                                    )
                                    
    
    # Make a prediction
    inferences = json.loads(response['Body'].read().decode('utf-8'))
  
    
    # We return the data back to the Step Function    
    event['inferences'] = inferences                        
    return {
        'statusCode': 200,
        'body': event
    }


"""
filtering

"""

import json

THRESHOLD = 0.7


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event["body"]['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences)>THRESHOLD
    
   

    return {
        'statusCode': 200,
        'body': event
    }