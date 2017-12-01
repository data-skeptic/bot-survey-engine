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

class ga_items():
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
        self.luis_url = config['luis']['luis_url']
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
    def extract_ga_items(self,user_request):
        GA_items = {}

        headers = {'Ocp-Apim-Subscription-Key': self.luis_subscription_key}
        print("h", headers)
        params ={
            'q': user_request,
            # Optional request parameters, set to default values
            'timezoneOffset': '-480', # minus 480 mins or 8 hours
            'verbose': 'true',
            'spellCheck': 'false',
            'staging': 'false',
        }
        try:
            r = requests.get(self.luis_url + self.luis_app_id, headers=headers, params=params)
            print(r)
            print(r.content)
            luis_result = r.json()
            print("luis_result is ", luis_result)
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
        score_threshold = 0 # adjust later
        GA_items['query'] = luis_result['query']
        for e in luis_result['entities']:
            print('*************************')
            print(e)
            if 'builtin.datetimeV2' in e.get('type'): # The entity is about time
                GA_items['date_text'] = GA_items.get('date_text',[]) + [e['entity']] # text about date
                if e.get('resolution', None): # resolved by LUIS  
                    if 'range' in e['resolution']['values'][0]['type']: # date range
                        if e['resolution']['values'][0].get('value', None) != 'not resolved': # time range is given by LUIS
                            GA_items['start'] = GA_items.get('end',[]) + [e['resolution']['values'][0]['start']]
                            GA_items['end'] = GA_items.get('end',[]) + [e['resolution']['values'][0]['end']]
                        else: # it is a time range, but the endpoints are not given by LUIS.
                            # it may be a season
                            if "SP" in e['resolution']['values'][0]['timex']: # spring
                                GA_items['start'] = GA_items.get('start',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-01-01"]
                                GA_items['end'] = GA_items.get('end',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-04-01"]
                            if "SU" in e['resolution']['values'][0]['timex']: # spring
                                GA_items['start'] = GA_items.get('start',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-04-01"]
                                GA_items['end'] = GA_items.get('end',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-07-01"]
                            if "FA" in e['resolution']['values'][0]['timex']: # spring
                                GA_items['start'] = GA_items.get('start',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-07-01"]
                                GA_items['end'] = GA_items.get('end',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-10-01"]
                            if "WI" in e['resolution']['values'][0]['timex']: # spring
                                GA_items['start'] = GA_items.get('start',[]) + ["".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])+"-10-01"]
                                GA_items['end'] = GA_items.get('end',[]) + [str(int("".join(e['resolution']['values'][0]['timex'].split('-')[0:-1])) + 1)+"-01-01"]
                            # other cases: it is a range, but not given by LUIS.
                            # ...
                    else: # not time range, a day or a time point, for example 3 days ago.
                        if e['resolution']['values'][0].get('value', None) != 'not resolved':
                            print(e['resolution']['values'][0]['value']) # a day or a time point
                            if ":" not in e['resolution']['values'][0]['value']: # a day, not time point
                                GA_items['start'] = GA_items.get('start',[]) + [e['resolution']['values'][0]['value'] ]
                                GA_items['end'] = GA_items.get('end',[]) + [str(datetime.now())[0:10]] # current day
                                # year = int(e['resolution']['values'][0]['value'].split('-')[0])
                                # month = int(e['resolution']['values'][0]['value'].split('-')[1])
                                # day = int(e['resolution']['values'][0]['value'].split('-')[2])
                                #GA_items['end'] = GA_items.get('end',[]) + [str(datetime(year, month, day) + timedelta(days=1))[0:10]]
                            else: # two hours ago. time is included.
                                GA_items['start'] = GA_items.get('start',[]) + [e['resolution']['values'][0]['value']]
                                GA_items['end'] = GA_items.get('end',[]) + [str(datetime.now())[0:19]]

            else: # ordinary entity, like dimensions, metrics
                if e['score'] > score_threshold:
                    GA_items[e['type']] = GA_items.get(e['type'], []) + [e['entity']]
        
        # get standard dimensions and metrics
        if GA_items.get('ga_dimension'):
            print('**dimension')
            non_standard_dims = GA_items.get('ga_dimension')
            print(non_standard_dims)
            standard_dims = []
            for non_standard_dim in non_standard_dims:
                standard_dim = process.extract(non_standard_dim, self.standard_dims, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
                print(process.extract(non_standard_dim, self.standard_dims, limit = 2,scorer=fuzz.token_sort_ratio))
                standard_dims.append(standard_dim)
            GA_items['standard_dims'] = ['ga:' + standard_dim  for standard_dim in standard_dims]
        if GA_items.get('ga_metric'):
            print('**metric')
            non_standard_metrics = GA_items.get('ga_metric')
            print(non_standard_metrics)
            standard_metrics = []
            for non_standard_metric in non_standard_metrics:
                standard_metric = process.extract(non_standard_metric, self.standard_metrics, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
                print(process.extract(non_standard_metric, self.standard_metrics, limit = 2,scorer=fuzz.token_sort_ratio))
                standard_metrics.append(standard_metric)
            GA_items['standard_metrics'] = ['ga:' + standard_metric  for standard_metric in standard_metrics]
        # LUIS can not inteperate 'all time', so here "start" and "end" are set manually.
        if ("all time" in user_request and (not GA_items.get('start')) and (not GA_items.get('end'))):
            GA_items['start'] = ['2010-01-01']
            GA_items['end'] = [str(datetime.now())[0:10]]

        print("GA_items finally is ", GA_items)
        return GA_items
    # gahelper
    def get_google_analytics(self,GA_items):
        print("here")
        ga = Gahelper(self.config)
        print(GA_items)
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
    def run(self,user_request): # 
        GA_items = self.extract_ga_items(user_request)
        if GA_items.get('standard_metrics') and GA_items.get('start') and GA_items.get('end'):
            print("GA_items", GA_items)
            f = self.get_google_analytics(GA_items)
        else:
            f = {'img': "", 'txt': "Metric, start date and end date are necessary. At least one of them is missing."}
        return f
         
def test_run(user_request):
    ga_instance = ga()
    ga_instance.run(user_request)

if __name__ == '__main__':
    user_request = "What is the ad cost per week in January last year?"
    test_run(user_request)
   














