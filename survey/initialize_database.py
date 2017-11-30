import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker
import json

with open ("../config/config.json", "r") as myfile:
            data = json.load(myfile)
            password = data['mysql']['password']
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
    , question_text varchar(244) not null
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
     response_end_time DATETIME default null,
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

def create_reminder_table():
    query_create = """
      CREATE TABLE reminder_schedule (
      task_id int not null auto_increment
    , contact_type varchar(122) not null
    , contact_account varchar(244) not null
    , reminder_time DATETIME not null
    , episode_title varchar(1024) 
    , episode_link varchar(1024)
    , scheduled int default 0
    , primary key (task_id)
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

def create_record_recommendation_table():
  query_create = """
      CREATE TABLE record_recommendation( 
      ID int not null auto_increment
    , user_request varchar(1024) not null
    , recommended_episode_title varchar(1024) not null
    , top int 
    , body_cos_similarity DOUBLE(4, 3)
    , title_cos_similarity DOUBLE(4, 3)
    , primary key (ID)
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

# create_questions_table()
# create_responses_table()
# create_response_answers_table()
# create_magic_table()
# create_logic_branches_table()
create_reminder_table()