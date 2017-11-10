import json
import time
import os
import sys
import pandas as pd
from datetime import datetime
#import parsedatetime as pdt # $ pip install parsedatetime
import dateparser #https://dateparser.readthedocs.io/en/latest/
from tabulate import tabulate
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


sys.path.insert(0, './gahelper')
from gahelper import Gahelper

# def get_date_range(time_string):
# 	now = datetime.now()
# 	cal = pdt.Calendar()
# 	return cal.parseDT(time_string, now)[0], now
	
def get_date_range(time_string):
	result = dateparser.parse(time_string)
	if result: 
		return dateparser.parse(time_string).date(), datetime.today().date()
	else:
		return None, None 

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

#find the standard dimension in GA by fuzzywuzzy
standard_dims = []
with open(dir_path + "/data/dimensions.json") as f:
	data = json.load(f)
	for key, value in data.items():
		standard_dims = standard_dims + value

standard_metrics = []
with open(dir_path + "/data/metrics.json") as f:
	data = json.load(f)
	for key, value in data.items():
		standard_metrics = standard_metrics + value

for result in results:
	print('--------------', result.get('text'), '---------------')

	if result.get('dimension'):
		print('**dimension')
		non_standard_dim = result.get('dimension')
		print(non_standard_dim)
		standard_dim = process.extract(non_standard_dim, standard_dims, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
		print(process.extract(non_standard_dim, standard_dims, limit = 2,scorer=fuzz.token_sort_ratio))
		result['standard_dim'] = 'ga:' + standard_dim

	
	print('**metric')
	non_standard_metric = result.get('metric')
	print(non_standard_metric)
	standard_metric = process.extract(non_standard_metric, standard_metrics, limit = 1,scorer=fuzz.token_sort_ratio)[0][0]
	print(process.extract(non_standard_metric, standard_metrics, limit = 2,scorer=fuzz.token_sort_ratio))
	result['standard_metric'] = 'ga:' + standard_metric

print(results)

# results dataframe form;
testing_results_df = pd.DataFrame.from_dict(results)
testing_results_df = testing_results_df[['dimension','standard_dim','metric', 'standard_metric','start','end']]
print('\n')
print(tabulate(testing_results_df, headers='keys', tablefmt='psql'))

# gahelper
config = json.load(open("../config/config.json"))
ga = Gahelper(config)

# a test
test = results[3]
print(test['text'])
metrics = [test.get('standard_metric', "")]
dimensions = [test.get('standard_dim',"")]
start_date = str(test.get('start'))
end_date = str(test.get('end'))
print(metrics, dimensions,start_date,end_date)

# metrics = ['ga:newUsers']
# dimensions = ['ga:medium']
# start_date = '2017-11-01'
# end_date = '2017-11-10'
# print(metrics, dimensions,start_date,end_date)

# metrics = ['ga:newUsers']
# dimensions = []
# start_date = '2017-11-01'
# end_date = '2017-11-10'
# print(metrics, dimensions,start_date,end_date)


# report = ga.get_report(metrics, dimensions, start_date, end_date)
# print(tabulate(report, headers='keys', tablefmt='psql'))

def report_reply(metrics, dimensions, start_date, end_date):
	report = ga.get_report(metrics, dimensions, start_date, end_date)
	print(tabulate(report, headers='keys', tablefmt='psql'))

	noga_dimensions = [dimension[3:] for dimension in dimensions]
	noga_metrics = [metric[3:] for metric in metrics]

	print('noga ', noga_metrics, noga_dimensions)
	print("From ", start_date, " to ", end_date, "\n")
	for i in range(report.shape[0]):
		print("-----------")
		dims = ",".join([report.loc[i, d] for d in noga_dimensions])
		mts = ",".join([report.loc[i, m] for m in noga_metrics])
		print("when ", ",".join(noga_dimensions), ' is/are ', dims, ',')
		print(",".join(noga_metrics), " is/are ", mts, ".")
report_reply(metrics, dimensions,start_date, end_date)




	


