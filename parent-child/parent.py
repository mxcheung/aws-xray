import json
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core import lambda_launcher
import logging

# Patch all supported libraries (boto3, requests, etc.)
patch_all()

# Initialize X-Ray recorder
xray_recorder.configure(service='LambdaFunctionOne')

def lambda_handler(event, context):
    # Start a segment for the entire Lambda execution
    xray_recorder.begin_segment('LambdaFunctionOne')

    # Start a custom subsegment
    subsegment = xray_recorder.begin_subsegment('FileUploadProcessing')
    try:
        # Your function logic here
        result = {"message": "File uploaded successfully!"}
        
        # Simulate processing file and generating client references
        client_references = process_file(event)
        
        # Process each client reference
        for client_ref in client_references:
            # Start a new subsegment for each row processing
            row_subsegment = xray_recorder.begin_subsegment('RowProcessing')
            try:
                # Log the row processing
                transaction = client_ref
                
                # Log the trace context to be picked up by Lambda Two
                logging.info({
                    'transaction': transaction,
                    '_xray_trace_header': {
                        'Root': xray_recorder.current_segment().trace_id,
                        'Parent': row_subsegment.id,
                        'Sampled': '1'
                    }
                })
            finally:
                # End the row subsegment
                xray_recorder.end_subsegment()

    finally:
        # End the subsegment
        xray_recorder.end_subsegment()

    xray_recorder.end_segment()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def process_file(event):
    # Dummy function to process file and return client references
    return [{'id': 'client1', 'amount': 100}, {'id': 'client2', 'amount': 200}]
