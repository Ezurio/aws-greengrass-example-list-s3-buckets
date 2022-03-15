import sys
import os
import logging
# the IG60 firmware does not include boto3, so we had to package it up ourselves
# since we were unable to install at runtime using PIP3
# The following is used to find our current location, so we can reference the included boto3 module
dirpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f'{dirpath}/boto3local')
import boto3
log_filename = "/tmp/S3buckets.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ])


try:
    logging.info("Creating boto3 S3 client...")
    s3 = boto3.client('s3')
    logging.info("Successfully created boto3 S3 client")
except Exception as e:
    logging.warning("Failed to create boto3 s3 client. Error: " + str(e))
    exit(1)

try:
    logging.info("Listing S3 buckets...")
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        bucket_name = bucket["Name"]
        bucket_datetime = bucket["CreationDate"]
        bucket_date = bucket_datetime.strftime("%Y-%b-%d")
        logging.info(f'Creation Date: {bucket_date}, Bucket Name: {bucket_name}')

    logging.info("Successfully listed S3 buckets")

except Exception as e:
    logging.warning("Failed to list S3 buckets. Error: " + str(e))
    exit(1)
