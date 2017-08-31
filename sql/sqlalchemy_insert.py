
# coding: utf-8

# In[2]:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from sqlalchemy_declarative import bot_survey_responses, Base, bot_survey_response_answers
 
engine = create_engine("sqlite:///user_responses.db") 
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
 



# Insert a Person in the person table

def get_response(response_info):
    '''
    write a function to get all the information we need of a response 
    
    '''
    return user_id, response_start_time, response_end_time

#user_id, response_start_time, response_end_time = get_response(response_info)
    
user_id = user_id
response_start_time = response_start_time
response_end_time = response_end_time

new_response = bot_survey_responses(user_id=user_id, response_start_time = response_start_time, response_end_time=response_end_time)

session.add(new_response)
session.commit()
 







# Insert an answer in the answer table



def get_answer(answer_info):
    '''
    write a function to get all the information we need of an answer 
    
    '''
    return response_id, answer_id, user_id, question_id, question_order, answer_submit_time, answer_text


# response_id, answer_id, user_id, question_id, question_order, answer_submit_time, answer_text = get_answer(answer_info)


# response_id = 1
# answer_id  = 20
# user_id =2
# question_id = 1
# question_order = 1
# answer_submit_time = "2017-08-31 11:20:30"
# answer_text = "Two years ago."


new_answer = bot_survey_response_answers(response_id = response_id, answer_id = answer_id, user_id= user_id, question_id =question_id, question_order=question_order, answer_submit_time=answer_submit_time,answer_text=answer_text)

session.add(new_answer)
session.commit()



