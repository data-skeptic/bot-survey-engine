
# coding: utf-8

import pandas as pd
import numpy as np
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine




Base = declarative_base()
 
class bot_survey_responses(Base):
    __tablename__ = 'bot_survey_responses'
    # Here we define columns for the table bot_survey_responses
    # Notice that each column is also a normal Python instance attribute.
    response_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    response_start_time = Column(String)
    response_end_time = Column(String)

class bot_survey_response_answers(Base):
    __tablename__ = 'bot_survey_response_answers'
    # Here we define columns for the table bot_survey_response_answers
    # Notice that each column is also a normal Python instance attribute.
    response_id = Column(Integer, ForeignKey('bot_survey_responses.response_id'))
    answer_id = Column(Integer, primary_key = True)
    user_id = Column(Integer)
    question_id = Column(Integer)
    question_order = Column(Integer)
    answer_submit_time = Column(String)
    answer_text = Column(String)
    

    
# Create an engine that stores data in the local directory's user_responses.db file.
engine = create_engine("sqlite:///user_responses.db")
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)






