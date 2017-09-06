import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker
import datetime
import time

# need to have the mysql_password.txt to connect to sqlworkbench/J.
with open ("mysql_password.txt", "r") as myfile:
    password=myfile.readlines()[0].strip()

#connect to sqlworkbench/J
engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % ("xiaofei", password, "iupdated.com:3306","survey"),pool_size=3, pool_recycle=3600)
Internal = sessionmaker(bind=engine_internal)
internal = Internal()

# Test it is sucessfully connected.
internal.execute('SHOW databases;')

# insert survey question to table
def insert_question_into_table(question_id,question_text,default_next_question_id,is_starting_question,can_be_ending_question):
    try:
        template = "INSERT INTO bot_survey_questions(question_id,question_text,default_next_question_id,is_starting_question,can_be_ending_question) VALUES('{question_id}','{question_text}','{default_next_question_id}','{is_starting_question}','{can_be_ending_question}')"
        query = template.format(question_id = question_id,question_text=question_text,default_next_question_id=default_next_question_id,is_starting_question=is_starting_question,can_be_ending_question=can_be_ending_question)
        internal.execute(query)
        print('Insert into quesiton table is successful.')
    except:
        print("Error in insert operation")
        pass

#test 
question_id = 1
question_text = 'When did you start listening to Data Skeptic?'
default_next_question_id = 2
is_starting_question = True
can_be_ending_question = False

insert_question_into_table(question_id,question_text,default_next_question_id,is_starting_question,can_be_ending_question)

# retrieve question text given quesiton_id
def retrieve_question(question_id):
    try:
        template = "SELECT question_text FROM bot_survey_questions WHERE question_id = '{question_id}' "
        r = internal.execute(template.format(question_id = question_id))
        return  r.fetchone()[0]

        
    except:
        print('error in retrieve question text.')
        raise

# test 
retrieve_question(question_id)

# update table bot_survey_response_answers and bot_survey_responses with users' answers.
def record_answer_to_database(response_id, question_id, question_order, answer_text):
    '''
    write a function to update responses and answers tables.
    '''
    # update table bot_survey_responses if response_id is None
    if response_id is None:  # a new survey starts when response_id is None.
        # we insert a new row in table bot_survey_responses to update the response_start_time
        # response_id will be generated automatically when insert a new row.
        try: 
            template = "INSERT INTO bot_survey_responses(response_start_time) VALUES(NOW())"
            query = template.format()
            
            internal.execute(query)
            
            # retrivel the response_id if the insertation is sucessful.
            r = internal.execute("SELECT last_insert_id()")
            response_id = r.fetchone()[0]
            #print(response_id)
        except: 
            print("Error")
            raise
    # response_id is known for the moment.
    # check whether the survey is over. If yes, then update the end_time and reset response_id = None
    last_question_list = [4,5]  # just for test todo: query from question_table to get a list of ending question_ids.
    if question_id in last_question_list:
        # Then the survey is over
        template = "UPDATE bot_survey_responses SET response_end_time = Now() WHERE response_id = '{response_id}';"
        query = template.format(response_id=response_id)
        internal.execute(query)
        print('Update the response end time successfully.') 

    # update table bot_survey_response_answers   
    try: 
        # response_answer_id will be automatically added by sql when we insert new rows.
        template = "INSERT INTO bot_survey_response_answers (response_id, question_id, question_order, answer_time, answer_text) VALUES('{response_id}','{question_id}', '{question_order}', NOW(), '{answer_text}')"
        query = template.format(response_id = response_id, question_id=question_id,  question_order=question_order, answer_text=answer_text)
        internal.execute(query) 
        # retrivel the response_id if the insertation is sucessful.
        r = internal.execute("SELECT LAST_INSERT_ID()") 
        response_answer_id = r.fetchone()[0]
        
        print('Insert into the answers table successfully.')
        print("Get the response_answer_id successfully.")
    except: 
        print('Error in inserting into the answers table.')
        print('Error in getting response_anwser_id.')
        raise
        
    return response_id, response_answer_id

# test the function record_answer_to_database
# The first question
response_id = None
question_id = 1
question_order = 1
answer_text = "Since last year."
results = record_answer_to_database(response_id, question_id, question_order, answer_text)

#The second question
response_id = 1
question_id = 2
question_order = 2
answer_text = "Two years ago."
results = record_answer_to_database(response_id, question_id, question_order, answer_text)


#The last question:(you will see that the response_end_time will be updated.)
response_id = 1
question_id = 4
question_order = 3
answer_text = "Two months ago."
results = record_answer_to_database(response_id, question_id, question_order, answer_text)

# insert magic text to magic table
def insert_magic():
    try:
        template = "INSERT INTO magic (question_id , magic_text, magic_reply) VALUES('{question_id}', '{magic_text}', '{magic_reply}')"
        query = template.format(question_id=question_id, magic_text = magic_text,magic_reply = magic_reply)   
        internal.execute(query)
        print('insert operation is successful.')
    except:
        print("Error in insert operation")
        pass

# for example, when answering question 6: where do you live? We have designed the following magic replies.
question_id = 6
magic_text = "Los Angeles"
magic_reply = "Data Skeptic records in Los Angeles."
insert_magic()

question_id = 6
magic_text = "Chicago"
magic_reply = "Kyle used to live there."
insert_magic()

question_id = 6
magic_text = "North Carolina"
magic_reply = "Linhda used to live there."
insert_magic()

# get_magic_reply.
def get_magic_reply(answer_text, question_id):
    template = "SELECT * FROM magic WHERE question_id = '{question_id}' "
    r = internal.execute(template.format(question_id = question_id))
    n= r.rowcount
   
    rows = []
    for i in range(n):
    	text_reply = r.fetchone()
    	if text_reply['magic_text'] in answer_text:
    		return text_reply['magic_reply']
       
get_magic_reply("I live at Los Angeles.", 6)
