import json
import boto3
import base64
import sagemaker
from sagemaker.serializers import IdentitySerializer

s3 = boto3.client('s3')
'''
First lambda function : serializeImageData 

    Lambda function will copy an object from S3
'''

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']## TODO: fill in
    bucket = event['s3_bucket']## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket , key , '/tmp/image.png')
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





# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-08-27-07-26-58-371'## TODO: fill in
'''
Second lambda function : image-classification

    classification part - we're going to take the image output from the previous function, decode it, and then pass inferences back to the the Step Function.
'''
def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])

    # Instantiate a Predictor

    predictor = sagemaker.predictor.Predictor(
        endpoint_name="image-classification-endpoint",
        image_uri="<your-image-uri>",
    )
    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    inferences = predictor.predict(image)
    
    # We return the data back to the Step Function    
    event["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
        


THRESHOLD = 0.7
'''
Thisd lambda function : THRESHOLD_CONFIDENCE 

   return it to the step function as image_data in an event.
'''

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(list(inferences))>THRESHOLD 
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }