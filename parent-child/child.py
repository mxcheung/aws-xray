import json
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core import lambda_launcher
import logging

# Patch all supported libraries (boto3, requests, etc.)
patch_all()

# Initialize X-Ray recorder
xray_recorder.configure(service='LambdaFunctionTwo')

def lambda_handler(event, context):
    # Extract the trace header from the event or logs (for simulation purposes, here we use a static example)
    trace_header = event.get('_xray_trace_header')
    if trace_header:
        xray_recorder.begin_segment('LambdaFunctionTwo', traceid=trace_header['Root'], parent_id=trace_header['Parent'], sampled=trace_header['Sampled'])
    else:
        xray_recorder.begin_segment('LambdaFunctionTwo')

    # Start a custom subsegment
    subsegment = xray_recorder.begin_subsegment('TransactionProcessing')
    try:
        # Your function logic here
        transaction = event['transaction']
        result = {
            "message": "Transaction processed successfully!",
            "transaction": transaction
        }
    finally:
        # End the subsegment
        xray_recorder.end_subsegment()

    xray_recorder.end_segment()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
