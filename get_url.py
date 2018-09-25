#! /usr/bin/python3

import requests
import time
import os
from google.cloud import storage
import logging
import google.cloud.logging

logclient = google.cloud.logging.Client()
logclient.setup_logging()


url = 'https://data.cityofchicago.org/resource/8v9j-bter.csv'

result=200
run = 0

def is_int(is_number):
    try:
        val = int(is_number)
        if val <= 0:
            return False
        return True
    except ValueError:
        return False


service_account_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
project_id = os.environ['GCLOUD_PROJECT']
bucket_name = os.environ['CLOUD_STORAGE_BUCKET']
## Setting Polling Interval - will default to 300 seconds if not configured or invalid
if os.environ.get('POLLING_INTERVAL') is not None:
    if is_int(os.environ.get('POLLING_INTERVAL')):
        logging.info('Passed Polling Interval is a positive integer, setting polling to: \'%s\'', os.environ.get('POLLING_INTERVAL'))
        polling_interval = os.environ['POLLING_INTERVAL']
    else:
        logging.info('Passed Polling Interval isn\'t a positive integer: \'%s\' setting polling to 300 seconds', os.environ.get('POLLING_INTERVAL'))
        polling_interval = 300
else:
    logging.info('POLLING_INTERVAL is not configured, setting polling to 300 seconds')
    polling_interval = 300

def upload_blob_from_string(bucket_name, source_string, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(source_string)
    #print('String uploaded to {}.'.format(destination_blob_name))
    logging.info('String uploaded to %s', destination_blob_name)
#try:
#    log_file = open('./chicago_stats_log.txt', 'a')
#except:
#    log_file = open('./chicago_stats_log.txt', 'w') 

while result == 200:
    starttime=time.time()
    r = requests.get(url)
    stats_filename = str(time.time()).split('.')[0] + ".txt"
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    blob_path = year + "/" + month + "/" + day + "/" + stats_filename
    #out_file = open(stats_filename, "w")

    if r.status_code == 200:
        log="Stats Pull Successful on " + time.strftime( "%x_%X" ,time.localtime()) + " Status Code: " + str(r.status_code)
        #out_file.write(r.text)
        upload_blob_from_string(bucket_name, r.text, blob_path)
    else:
        log="Stats Pull Unsuccessful on " + time.strftime( "%x_%X" ,time.localtime()) + " Status Code: " + str(r.status_code) + " Reason: " + r.reason

    #log_file.write(log + "\n")
    #log_file.flush()
    result=r.status_code
    if result == 200:
        logging.info(log)
    else:
        logging.warning(log)

    r.close
    #out_file.close
    run += 1
    #print ('Run {0} completed at {1}'.format(run,time.ctime()))
    logging.info('Run %s completed at %s', run, time.ctime())
    time.sleep(polling_interval - (time.time() - starttime))
#   log_file.close
