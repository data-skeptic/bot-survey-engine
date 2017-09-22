import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker
import datetime
import time
import json

# need to have the mysql_password.txt to connect to sqlworkbench/J.
with open ("mysql_password.txt", "r") as myfile:
    password=myfile.readlines()[0].strip()
#connect to sqlworkbench/J
engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % ("xiaofei", password, "iupdated.com:3306","survey"),pool_size=3, pool_recycle=3600)
internal = engine_internal
# Test it is sucessfully connected.

r= internal.execute("show tables;")
print('tables')
print(r.fetchall())


def insert_into_questions_table(question_id, question_text):
	template = "INSERT INTO bot_survey_questions (question_id, question_text) VALUES('{question_id}','{question_text}')"
	query = template.format(question_id = question_id, question_text = question_text)
	try:
	    internal.execute(query)
	except:
		print('questions_table: question_id is ', question_id)
		print( "failed")
	# finally:
	#     internal.close() 
def insert_into_logic_branches(question_id, test_text, next_question_id):
	template = "INSERT INTO logic_branches (question_id, test_text, next_question_id) VALUES('{question_id}','{test_text}','{next_question_id}')"
	query = template.format(question_id = question_id, test_text = test_text, next_question_id = next_question_id)
	try:
	    internal.execute(query)
	except:
		print('logic_branches_table: question_id is ', question_id)
		print( "failed")
	# finally:
	#     internal.close() 
def update_logic_branches(question_id, test_text, next_question_id):
	template = "UPDATE logic_branches SET next_question_id = '{next_question_id}', test_text = '{test_text}' WHERE question_id = '{question_id}';"
	query = template.format(question_id = question_id, test_text = test_text, next_question_id = next_question_id)
	try:
	    internal.execute(query)
	except:
		print('question_id is ', question_id)
		print( "failed")
	# finally:
	#     internal.close() 

with open('survey.json') as f:
	data = json.load(f)
	questions = data['questions'] # questions is a list of dictionaries
	logic_branches = data['logic_branches'] # logic_branches is a list of dictionary


for item in questions:
	question_text = item['question_text']
	question_id = item['question_id']
	#print(question_text, question_id)
	insert_into_questions_table(question_id, question_text)

for item in logic_branches:
	question_id = item['question_id']
	next_question_id = item['next_question_id']
	test_text = item['test_text']
	insert_into_logic_branches(question_id, test_text, next_question_id)



