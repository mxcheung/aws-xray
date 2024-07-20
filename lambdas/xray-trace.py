import json
import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core import lambda_launcher

# Patch all supported libraries (boto3, requests, etc.)
patch_all()

# Initialize X-Ray recorder
xray_recorder.configure(service='LambdaFunctionOne')

def lambda_handler(event, context):
    # Start a custom subsegment
    subsegment = xray_recorder.begin_subsegment('LambdaFunctionOneProcessing')
    try:
        # Your function logic here
        result = {"message": "Hello from Lambda One!"}
        # Example: Invoke the second Lambda function
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName='LambdaFunctionTwo',
            InvocationType='RequestResponse',  # or 'Event' for asynchronous
            Payload=json.dumps(event)
        )
        response_payload = json.loads(response['Payload'].read())
        result.update(response_payload)
    finally:
        # End the subsegment
        xray_recorder.end_subsegment()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
