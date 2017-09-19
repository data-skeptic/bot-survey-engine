#(9_14_17)
import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker
import datetime
import time
from pandas import DataFrame
import random
import pandas as pd
import json
import boto3


class Survey():   
    def __init__(self, username, address, databasename):
         
        with open ("mysql_password.txt", "r") as myfile:
            self.password = myfile.readlines()[0].strip()    

        #connect to sqlworkbench/J
        #engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % ("xiaofei", password, "iupdated.com:3306","survey"),pool_size=3, pool_recycle=3600)
        engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (username, self.password, address,databasename),pool_size=3, pool_recycle=3600)
        #Internal = sessionmaker(bind=engine_internal)
        #self.internal = Internal()
        self.internal = engine_internal
        #test
        try:
            self.internal.execute("SHOW DATABASES;")
            print('The connection is successful.')
        except:
            print('The connection fails.')
            raise
        # call method refresh_from_database
        self._dfs = self.refresh_from_database()
        # refresh_from_database() returns the database form of the three tables:'magic', 'bot_survey_questions', 'logic_branches'
        # They are saved in the dictionary self._dfs and we only need to query the database once. 
    def refresh_from_database(self):
        table_names = ['magic', 'bot_survey_questions', 'logic_branches']
        result_dfs = {}
        for table_name in table_names:
            try:
                r = self.internal.execute("SELECT * FROM "+ table_name)
                print('Refresh '+ table_name +' is successful.')
                data = r.fetchall()
                df = DataFrame(data)
                df.columns = r.keys()
                result_dfs[table_name+"_df"] = df
                print('refresh successfully.')
            except:
                print("Error in refresh " + table_name)
                raise        
        return result_dfs
    def get_question_text(self, question_id):
        print("debugging for get_question_text.")
        df = self._dfs['bot_survey_questions_df']
        
        return df[df['question_id'] == question_id]['question_text'].values[0]
        #return 'default question.'
    def get_next_question_id(self, question_id, answer):
        question_df = self._dfs['logic_branches_df']
        #filter according to question_id and the answer
        sub_df = question_df.loc[(question_df['question_id'] == question_id) & (question_df['test_text'].apply(lambda x: str(x).lower() in answer.lower()) )]
        if sub_df['next_question_id'].shape[0] == 1:
            return sub_df['next_question_id'].values[0]
        else:
            sub_df = question_df.loc[(question_df['question_id'] == question_id) & ((question_df['test_text'].apply(lambda x: str(x) == "None")) )]
            return sub_df['next_question_id'].values[0]
    
    # update table bot_survey_response_answers and bot_survey_responses with users' answers.
    def save_answer(self, response_id, question_id, question_order, answer_text):
        '''
        write a function to update responses and answers tables.
        '''
        answer_text = answer_text.replace("'", "\\'")
        answer_text = answer_text.replace(";", "\\;")
        answer_text = answer_text.replace("&", "\\&")
        answer_text = answer_text.replace("%", "\\%")

        print("answer_text is", answer_text)
        # update table bot_survey_responses if response_id is None
        if response_id is None:  # a new survey starts when response_id is None.
            # we insert a new row in table bot_survey_responses to update the response_start_time
            # response_id will be generated automatically when insert a new row.
            try: 
                template = "INSERT INTO bot_survey_responses(response_start_time) VALUES(NOW())"
                query = template.format()
                conn = self.internal.connect()
                conn.execute(query)
                r = conn.execute("SELECT last_insert_id()")

                conn.close()
                #self.internal.execute(query)
                print('Successful in inserting into bot_survey_responses table.')
                # retrivel the response_id if the insertation is sucessful.
                response_id = r.fetchone()[0]
                print('get a new response_id', response_id)
                print('Successful in getting the response_id.')                                                              
            except: 
                print("Error in inserting into bot_survey_responses.")
                raise
        # response_id is known for the moment.
        # check whether the survey is over. If yes, then update the end_time and reset response_id = None
        
          # just for test todo: query from question_table to get a list of ending question_ids.
        last_question_list = [20]
        if question_id in last_question_list:
            # Then the survey is over
            template = "UPDATE bot_survey_responses SET response_end_time = Now() WHERE response_id = '{response_id}';"
            query = template.format(response_id=response_id)
            self.internal.execute(query)
            print('Update the response end time successfully.') 

        # update table bot_survey_response_answers   
        try: 
            #check whether response_id is in the response_table
            respns = self.internal.execute('select response_id from bot_survey_responses;')
            response_ids = respns.fetchall() 
            response_ids = [id[0] for id in response_ids]

            if response_id not in response_ids:
                print('Foreign key error will happen. Because response_id is not in the response table.')
                return 
            # response_answer_id will be automatically added by sql when we insert new rows.
            template = "INSERT INTO bot_survey_response_answers (response_id, question_id, question_order, answer_time, answer_text) VALUES('{response_id}','{question_id}', '{question_order}', NOW(), '{answer_text}')"
            print('in the survey.py, print the response_id which is to be inserted into the table ', response_id)
            query = template.format(response_id = response_id, question_id=question_id,  question_order=question_order, answer_text=answer_text)
            self.internal.execute(query) 
            # retrivel the response_id if the insertation is sucessful.
            r = self.internal.execute("SELECT LAST_INSERT_ID()") 
            response_answer_id = r.fetchone()[0]

            print('Insert into the answers table successfully.')
            print("Get the response_answer_id successfully.")
        except: 
            print('Error in inserting into the answers table.')
            print('Error in getting response_anwser_id.')
            raise
        return response_id, response_answer_id
    def get_magic_reply(self, answer_text, question_id):
        template = "SELECT * FROM magic WHERE question_id = '{question_id}' "
        r = self.internal.execute(template.format(question_id = question_id))
        n= r.rowcount

        rows = []
        for i in range(n):
            text_reply = r.fetchone()
            if text_reply['magic_text'] in answer_text:
                return text_reply['magic_reply']
        return ""

    def survey_retrieval(self, next_question_id, response_id):
        
        if next_question_id == -1:
            print('The survey is complete. Information retrieval time!') # for testing
            # how to get all information needed for an email from database?
            table_name = 'bot_survey_response_answers'
            try:
                r = self.internal.execute("SELECT * FROM "+ table_name + " where response_id = " + str(response_id))
                print('Refresh '+ table_name +' is successful.')
                data = r.fetchall()
                df = DataFrame(data)
                df.columns = r.keys()
    
            except:
                print("Error in refreshing " + table_name)
                raise 
            #print("question_table is : ")
            question_table = self._dfs['bot_survey_questions_df'][['question_id', 'question_text']]
            #print(question_table) 
            question_dict = dict(zip(question_table.question_id, question_table.question_text))
            #print(question_dict)
            df = df.replace({"question_id": question_dict})
            df = df[['question_id', 'answer_time', 'answer_text']]  
            df.rename(columns={'question_id': 'question_text'}, inplace=True)
            df = df[df['question_text'] != -1 ]
        # if the survey is completed, return {'bot_survey_responses_df': a df, 'bot_survey_response_answers_df': a df }
        # else return {}
            return df
        else:
            return pd.DataFrame()

    #def send_email(self, result_dfs, source_email, destination_email, reply_to_email):
    def send_email(self,result_dfs):
        with open ("awskeys.txt", "r") as myfile:
            user, pw = [s.strip() for s in myfile.readlines()]

        client = boto3.client('ses',
                    region_name = 'us-east-1', 
                    aws_access_key_id = user, 
                    aws_secret_access_key = pw)
        source_email = "xfzhengnankai@gmail.com"
        destination_email = "fayezheng1010@gmail.com"
        reply_to_email = source_email
        if not result_dfs.empty:
            bodyhtml = result_dfs.to_html() 
            response = client.send_email(
                Source= source_email,
                Destination={'ToAddresses': [destination_email]},
                Message={
                    'Subject': {
                        'Data': 'A survey is complete.'
                    },
                    'Body': {
                        'Html': {
                            'Data': bodyhtml
                        }
                    }
                },
                ReplyToAddresses=[reply_to_email]
            )
            return response if 'ErrorResponse' in response else 'successful. Check email box.'  # if successful, return ""
        else:
            print("The survey is not complete yet. Email will be sent once it is complete.") 
            return "not complete yet."
# the end of the definition of the class

def create_survey():
    username = 'xiaofei'
    address = "iupdated.com:3306"
    databasename = 'survey'
    # check initialization
    survey_instance = Survey(username, address, databasename)
    return survey_instance

def test():
    username = 'xiaofei'
    address = "iupdated.com:3306"
    databasename = 'survey'

    # check initialization
    s= Survey(username,  address, databasename)
    s._dfs['logic_branches_df']
    #check get_next_question_id
    s.get_next_question_id(1, "Since last year.")

    response_id = None
    question_id =1
    question_order =1
    answer_text = "Some Text"
    (r_id, a_id) = s.save_answer(response_id, question_id, question_order, answer_text)
    print("Response_id and answer_id are ", (r_id, a_id))
                                                                                  
    #When insert an answer which has response_id into the answer table, 
    # the response_id must be in the response_id column of the response table due to the foreign key restriction.                                                                               
    respns = s.internal.execute('select response_id from bot_survey_responses;')
    response_ids = respns.fetchall() 
    response_ids = [id[0] for id in response_ids]
                                                                                  
    response_id = random.choice(response_ids)
    question_id =2
    question_order =2
    answer_text = "Some Text"
    s.save_answer(response_id, question_id, question_order, answer_text)

    respns = s.internal.execute('select * from bot_survey_responses;')
    respns.fetchall()


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
   
   
