import json
import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core import lambda_launcher

# Patch all supported libraries (boto3, requests, etc.)
patch_all()

# Initialize X-Ray recorder
xray_recorder.configure(service='LambdaFunctionOne')

def lambda_handler(event, context):
    # Extract the trace header from the event (if available)
    trace_header = event.get('_xray_trace_header')
    if trace_header:
        xray_recorder.begin_segment('LambdaFunctionOne', traceid=trace_header['Root'], parent_id=trace_header['Parent'], sampled=trace_header['Sampled'])
    else:
        xray_recorder.begin_segment('LambdaFunctionOne')

    # Start a custom subsegment
    subsegment = xray_recorder.begin_subsegment('LambdaFunctionOneProcessing')
    try:
        # Your function logic here
        result = {"message": "File uploaded successfully!"}
        
        # Process file and generate individual transactions
        transactions = process_file(event)
        
        # Example: Invoke the second Lambda function for each transaction
        client = boto3.client('lambda')
        for transaction in transactions:
            client.invoke(
                FunctionName='LambdaFunctionTwo',
                InvocationType='Event',  # Using Event for asynchronous invocation
                Payload=json.dumps({
                    'transaction': transaction,
                    '_xray_trace_header': {
                        'Root': xray_recorder.current_segment().trace_id,
                        'Parent': xray_recorder.current_subsegment().id,
                        'Sampled': '1'
                    }
                })
            )
    finally:
        # End the subsegment
        xray_recorder.end_subsegment()

    xray_recorder.end_segment()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def process_file(event):
    # Dummy function to process file and return transactions
    return [{'id': 'tx1', 'amount': 100}, {'id': 'tx2', 'amount': 200}]
