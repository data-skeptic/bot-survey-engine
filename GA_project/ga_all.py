import json
import os 
import time
import boto3
import numpy as np
import sys
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
#import parsedatetime as pdt # $ pip install parsedatetime
import dateparser #https://dateparser.readthedocs.io/en/latest/
from tabulate import tabulate

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter

sys.path.insert(0, './gahelper')
from gahelper import Gahelper
from gaformatter import format_dataframe

class ga():
    def __init__(self,update_model = False):
        config = json.load(open("../config/config.json"))
        self.key = config['aws']['accessKeyId']
        self.secret = config['aws']['secretAccessKey']
        self.bucketname = config['aws']['bucket_name']
        self.s3 = boto3.resource('s3', aws_access_key_id=self.key, aws_secret_access_key=self.secret)
        self.config = config
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        if update_model:
            #-----train a new model and save it in mdoel_directory-----------
            #load training data
            training_data =  load_data(self.dir_path +'/data/training_data.json')
            # set config and train
            trainer = Trainer(RasaNLUConfig("sample_configs/config_spacy.json"))
            trainer.train(training_data)
            # Returns the directory the model is stored in 
            self.model_directory = trainer.persist('./projects/') 
            return self.model_directory
        else:
            self.model_directory = self.dir_path + "/projects/default/model_20171110-144019"
        # load the model
        self.interpreter = Interpreter.load(self.model_directory, RasaNLUConfig("sample_configs/config_spacy.json"))

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
    def parse_data(self,user_request):
        parsed_result = self.interpreter.parse(user_request)
        return parsed_result # which is in json form
    def parse_test_data(self):
        file_name = self.dir_path + "/data/testing_data.txt" 
        result_file_path = self.dir_path + "/data/testing_results.json"
        result_file = open(result_file_path, 'w')
        result_file.close()
        i = 0
        with open(file_name, 'r') as f:
            result_file = open(result_file_path, 'a')
            for line in f:
                if i != 0:
                    result_file.write(',')
                else:
                    result_file.write('{\"test_results\":[ \n')
                request = line[0:-1]
                result = self.interpreter.parse(request)
                json.dump(result,result_file,indent=4, separators=(',', ': '))
                result_file.write("\n")
                i += 1
            result_file.write("]\n}")
        result_file.close()
        self.result_file_path = result_file_path
        
    # further process of the parsed data to get legal dimensions and metrics in GA.
    def get_date_range(self,time_string):
        result = dateparser.parse(time_string)
        if result: 
            return dateparser.parse(time_string).date(), datetime.today().date()
        else:
            return None, None 
    def get_standard_dim_metric(self, parsed_result):
        GA_items = {}
        entities = parsed_result['entities']
        GA_items['text'] = parsed_result['text']
        for e in entities: # e is a dict: {'start': 12, 'end': 31, 'value': 'average bounce rate', 'entity': 'metric', 'extractor': 'ner_crf'}
            value = e.get('value')
            entity = e.get('entity')
            GA_items[entity] = GA_items.get(entity, "") + " " + value
        if 'date' in GA_items.keys():
            if GA_items.get('date').split()[0] == 'past':
                GA_items['date'] = " ".join(GA_items.get('date').split()[1:]) + " " + "ago"
            GA_items['start'], GA_items['end'] = self.get_date_range(GA_items['date'])
        
        if GA_items.get('dimension'):
            print('**dimension')
            non_standard_dim = GA_items.get('dimension')
            print(non_standard_dim)
            standard_dim = process.extract(non_standard_dim, self.standard_dims, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
            print(process.extract(non_standard_dim, self.standard_dims, limit = 2,scorer=fuzz.token_sort_ratio))
            GA_items['standard_dim'] = 'ga:' + standard_dim     
        print('**metric')
        non_standard_metric = GA_items.get('metric')
        print(non_standard_metric)
        standard_metric = process.extract(non_standard_metric, self.standard_metrics, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
        print(process.extract(non_standard_metric, self.standard_metrics, limit = 2,scorer=fuzz.token_sort_ratio))
        GA_items['standard_metric'] = 'ga:' + standard_metric
        # show results in dataframe form
        return GA_items

    def get_standard_dim_metric_test_date(self):
        with open(self.result_file_path, 'r') as f:
            data = json.load(f)['test_results'] # data is a list
            results = []
            for i in range(len(data)):
                GA_items = {}
                entities = data[i]['entities'] # a list
                GA_items['text'] = data[i]['text']
                for e in entities: # e is a dict: {'start': 12, 'end': 31, 'value': 'average bounce rate', 'entity': 'metric', 'extractor': 'ner_crf'}
                    value = e.get('value')
                    entity = e.get('entity')
                    GA_items[entity] = GA_items.get(entity, "") + " " + value
            
                if 'date' in GA_items.keys():
                    if GA_items.get('date').split()[0] == 'past':
                        GA_items['date'] = " ".join(GA_items.get('date').split()[1:]) + " " + "ago"
                    GA_items['start'], GA_items['end'] = self.get_date_range(GA_items['date'])
                results.append(GA_items)
        
        for result in results:
            print('--------------', result.get('text'), '---------------')
            if result.get('dimension'):
                print('**dimension')
                non_standard_dim = result.get('dimension')
                print(non_standard_dim)
                standard_dim = process.extract(non_standard_dim, self.standard_dims, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
                print(process.extract(non_standard_dim, self.standard_dims, limit = 2,scorer=fuzz.token_sort_ratio))
                result['standard_dim'] = 'ga:' + standard_dim     
            print('**metric')
            non_standard_metric = result.get('metric')
            print(non_standard_metric)
            standard_metric = process.extract(non_standard_metric, self.standard_metrics, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
            print(process.extract(non_standard_metric, self.standard_metrics, limit = 2,scorer=fuzz.token_sort_ratio))
            result['standard_metric'] = 'ga:' + standard_metric
        print(results)
        # show results in dataframe form
        testing_results_df = pd.DataFrame.from_dict(results)
        testing_results_df = testing_results_df[['dimension','standard_dim','metric', 'standard_metric','start','end']]
        print('\n')
        print(tabulate(testing_results_df, headers='keys', tablefmt='psql'))
        return results,testing_results_df

# gahelper
    def get_google_analytics(self,GA_items):
        ga = Gahelper(self.config)
        # a test
        # test = results[3]
        # print(test['text'])
        # metrics = [test.get('standard_metric', "")]
        # dimensions = [test.get('standard_dim',"")]
        # start_date = str(test.get('start'))
        # end_date = str(test.get('end'))
        # print(metrics, dimensions,start_date,end_date)

        # report = ga.get_report(metrics, dimensions, start_date, end_date)
        # print(tabulate(report, headers='keys', tablefmt='psql'))
        # f = format_dataframe(self.s3, self.bucketname, self.report, metrics, dimensions, start_date, end_date)
        # print(f)
        print(GA_items)
        metrics = [GA_items.get('standard_metric', "")]
        dimensions = [GA_items.get('standard_dim',"")]
        start_date = str(GA_items.get('start'))
        end_date = str(GA_items.get('end'))
        print(metrics, dimensions,start_date,end_date)

        report = ga.get_report(metrics, dimensions, start_date, end_date)
        print(tabulate(report, headers='keys', tablefmt='psql'))
        f = format_dataframe(self.s3, self.bucketname, report, metrics, dimensions, start_date, end_date)
        print(f)
        return f
def run(): # later pass user_request to run() instead of using a default user_request.
    ga_instance = ga(update_model = False)
    user_request = "How many transactions across user type in the last year?"
    parsed_result = ga_instance.parse_data(user_request)
    GA_items = ga_instance.get_standard_dim_metric(parsed_result)
    f = ga_instance.get_google_analytics(GA_items)
run()

def run_test_data():
    ga_instance = ga(update_model = False)
    ga_instance.parse_test_data()
    ga_instance.get_standard_dim_metric_test_date()

run_test_data()

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    




