import json
import time
import os
import pandas as pd
from datetime import datetime
#import parsedatetime as pdt # $ pip install parsedatetime
import dateparser #https://dateparser.readthedocs.io/en/latest/
from tabulate import tabulate

# def get_date_range(time_string):
# 	now = datetime.now()
# 	cal = pdt.Calendar()
# 	return cal.parseDT(time_string, now)[0], now
	
def get_date_range(time_string):
	return dateparser.parse(time_string), datetime.now()

dir_path = os.path.dirname(os.path.realpath(__file__))
result_file_path = dir_path + "/data/testing_results.json"

with open(result_file_path, 'r') as f:
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
			GA_items['start'], GA_items['end'] = get_date_range(GA_items['date'])
		results.append(GA_items)

testing_results_df = pd.DataFrame.from_dict(results)
testing_results_df = testing_results_df[['dimension','metric','date','start','end']]
print('\n')
print(tabulate(testing_results_df, headers='keys', tablefmt='psql'))






	


