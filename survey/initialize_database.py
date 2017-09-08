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

# create question table
def create_questions_table():
    query_create = """
      CREATE TABLE bot_survey_questions (
      question_id int not null auto_increment
    , question_text varchar(1024) not null
    , default_next_question_id int 
    , is_starting_question BIT 
    , can_be_ending_question BIT
    , primary key (question_id)
    );
    """
    try:
        #internal.execute("""DROP TABLE IF EXISTS bot_survey_responses;""")
        internal.execute(query_create)
        print( "done")
    except:
        print( "failed")
    finally:
        internal.close()     

def create_responses_table():
    query_create = """
    CREATE TABLE bot_survey_responses(
     response_id INT NOT NULL AUTO_INCREMENT,
     response_start_time DATETIME NOT NULL,
     response_end_time TIMESTAMP,
     primary key(response_id)
    );
    """
    try:
        #internal.execute("""DROP TABLE IF EXISTS bot_survey_responses;""")
        internal.execute(query_create)
        print( "done")
    except:
        print( "failed")
    finally:
        internal.close()

# create response_answer table
def create_response_answers_table():
    query_create ="""
    CREATE TABLE bot_survey_response_answers(
    response_answer_id int not null auto_increment,
    response_id int not null,
    question_id int,
    question_order int,
    answer_time TIMESTAMP,
    answer_text varchar(1024) not null,
    PRIMARY KEY (response_answer_id),
    FOREIGN KEY (response_id) REFERENCES bot_survey_responses(response_id)
    );
    """
    try:
        #internal.execute("""DROP TABLE IF EXISTS bot_survey_response_answers;""")
        internal.execute(query_create)
        internal.commit()
        print( "done")
    except:
        print( "failed")
    finally:
        internal.close()

def create_magic_table():
   query_create =""" 
   CREATE TABLE magic (
     magic_id int not null auto_increment
   , question_id int not null
   , magic_text varchar(1024) DEFAULT NULL
   , magic_reply varchar(1024) DEFAULT NULL
   , primary key (magic_id)
   );
   """
   try:
   #internal.execute("""DROP TABLE IF EXISTS bot_survey_response_answers;""")
       internal.execute(query_create)
       internal.commit()
       print( "done")
   except:
       print( "failed")
   finally:
       internal.close()
    
def create_logic_branches_table():
    query_create =""" 
    CREATE TABLE logic_branches (
     logic_branches_id int not null auto_increment
    , question_id int not null
    , test_text varchar(1024) DEFAULT NULL
    , next_question_id int not null
    , primary key (logic_branches_id)
    );
    """
    try:
    #internal.execute("""DROP TABLE IF EXISTS bot_survey_response_answers;""")
       internal.execute(query_create)
       internal.commit()
       print( "done")
    except:
       print( "failed")
    finally:
       internal.close()

create_questions_table()
create_responses_table()
create_response_answers_table()
create_magic_table()
create_logic_branches_table()

