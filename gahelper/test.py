import json
from gahelper import Gahelper

config = json.load(open("../config/config.json"))

ga = Gahelper(config)
metrics = ['ga:newUsers']
dimensions = ['ga:medium']
start_date = '2017-11-01'
end_date = '2017-11-10'
report = ga.get_report(metrics, dimensions, start_date, end_date)

print(report)