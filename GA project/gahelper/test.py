import os
import json
import boto3
import numpy as np
from gahelper import Gahelper
import matplotlib.pyplot as plt
from datetime import datetime
from gaformatter import format_dataframe

config = json.load(open("../config/config.json"))

key = config['aws']['accessKeyId']
secret = config['aws']['secretAccessKey']
bucketname = config['aws']['bucket_name']

s3 = boto3.resource('s3', aws_access_key_id=key, aws_secret_access_key=secret)

ga = Gahelper(config)
metrics = ['ga:newUsers']
dimensions = ['ga:medium']
start_date = '2017-11-01'
end_date = '2017-11-10'
report = ga.get_report(metrics, dimensions, start_date, end_date)

f = format_dataframe(s3, bucketname, report, metrics, dimensions, start_date, end_date)
print(f)