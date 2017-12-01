import json
import os 
import time
import boto3
import numpy as np
import sys
import pandas as pd

import matplotlib.pyplot as plt
#import parsedatetime as pdt # $ pip install parsedatetime
import requests
from tabulate import tabulate

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from gahelper.gahelper import Gahelper
from gahelper.gaformatter import format_dataframe

from datetime import datetime  
from datetime import timedelta

class ga_report():
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        # print("/".join(self.dir_path.split("/")[0:-1]) + "/config/config.json")
        config = json.load(open("/".join(self.dir_path.split("/")[0:-1]) + "/config/config.json"))
        self.key = config['aws']['accessKeyId']
        self.secret = config['aws']['secretAccessKey']
        self.bucketname = config['aws']['bucket_name']
        self.s3 = boto3.resource('s3', aws_access_key_id=self.key, aws_secret_access_key=self.secret)
        self.config = config

        self.luis_app_id = config['luis']['app_id']
        self.luis_subscription_key = config['luis']['subscription_key']

        self.standard_dims = []
        with open(self.dir_path + "/data/dimensions.json") as f:
            data = json.load(f)
            for key, value in data.items():
                self.standard_dims = self.standard_dims + value
        self.standard_metrics = []
        with open(self.dir_path + "/data/metrics.json") as f:
            data = json.load(f)
            for key, value in data.items():
                self.standard_metrics = self.standard_metrics + value
        return
    # gahelper
    def get_google_analytics(self,GA_items):
        ga = Gahelper(self.config)
        print("GA_items in get_google_analytics is ", GA_items)
        if not GA_items.get('standard_metrics'):
            f  = {'img':"",'txt':""}
        if not GA_items.get('start'): # start is missing
            if GA_items.get('end'): # end is not missing
                f = {'img': "", 'txt': "start missing"}
            else:
                f = {'img':"", 'txt':"date range is missing."}
        else: # start is not missing
            if not GA_items.get('end'): # end is missing
                f = {'img': "", 'txt': "end missing"}
            else:
                metrics = GA_items.get('standard_metrics', [])
                dimensions = GA_items.get('standard_dims',[])
                if len(GA_items.get('start')) == 1:
                    start_date = str(GA_items.get('start')[-1])
                    end_date = str(GA_items.get('end')[-1])
                else:
                    # if there are more than one pair of start and end, which one is right? Or need to combine all/both pairs?
                    # for the moment, use the last one. It is more likely to be the right one. For example, how many sessions per month in 2017? Then ['month', '2017'] will be returned. use the last one '2017'.
                    start_date = str(GA_items.get('start')[-1])
                    end_date = str(GA_items.get('end')[-1])
                print(metrics, dimensions,start_date,end_date)

                report = ga.get_report(metrics, dimensions, start_date, end_date)
                print(tabulate(report, headers='keys', tablefmt='psql'))
                f = format_dataframe(self.s3, self.bucketname, report, metrics, dimensions, start_date, end_date)
                print(f)
        return f
    def run(self,GA_items): # 
        # GA_items = self.extract_ga_items(user_request)
        # if GA_items.get('standard_metrics') and GA_items.get('start') and GA_items.get('end'):
        #     f = self.get_google_analytics(GA_items)
        # else:
        #     f = {'img': "", 'txt': "Metric, start date and end date are necessary. At least one of them is missing."}
        # return f
        if GA_items.get('standard_metrics'):
            if GA_items.get('start'):
                if GA_items.get('end'):
                    f = self.get_google_analytics(GA_items)
                else:
                    f = {'img': "", 'txt': "end missing'"}
            elif GA_items.get('end'):
                f = {'img': "", 'txt': "start missing"}
            else:
                f = {'img': "", 'txt': "date range missing"}
        else:
            f = {'img':"",'txt':""}

        return f
# def test_run(user_request):
#     ga_instance = ga()
#     ga_instance.run(user_request)
    
# user_request = "What is the ad cost per week in January last year?"
# test_run(user_request)

if __name__ == '__main__':
    pass
   














