from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
import json
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
#-----train a new model and save it in mdoel_directory-----------
# load training data
# training_data =  load_data(dir_path +'/data/training_data.json')
# # set config and train
# trainer = Trainer(RasaNLUConfig("sample_configs/config_spacy.json"))
# trainer.train(training_data)
# # Returns the directory the model is stored in 
# model_directory = trainer.persist('./projects/') 
#----------------end of training and saving-----------------------

#----------------load the model already trained-------------------
#model_directory stores all information of the model.
model_directory = dir_path + "/projects/default/model_20171110-144019"
#where `model_directory points to the folder the model is persisted in
interpreter = Interpreter.load(model_directory, RasaNLUConfig("sample_configs/config_spacy.json"))

# use the model to parse testing data and save the result in a json file /data/testing_results.json
file_name = dir_path + "/data/testing_data.txt" 
result_file_path = dir_path + "/data/testing_results.json"
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
        result = interpreter.parse(request)
        json.dump(result,result_file,indent=4, separators=(',', ': '))
        result_file.write("\n")
        i += 1
    result_file.write("]\n}")
result_file.close()

# further process of the parsed data to get legal dimensions and metrics in GA.




