# bot_survey_questions;
DROP TABLE IF EXISTS bot_survey_questions;

CREATE TABLE bot_survey_questions (
  question_id int not null auto_increment
, question_text varchar(1024) not null
, default_next_question_id int 
, is_starting_question BIT 
, can_be_ending_question BIT
, primary key (question_id)
);

# bot_survey_responses
# This table should get one record every time a survey is started. It will capture metadata like the time it is started.
DROP TABLE IF EXISTS bot_survey_responses;
CREATE TABLE bot_survey_responses(
 response_id int not null auto_increment
,response_start_time TIMESTAMP not null
,response_end_time TIMESTAMP null
,primary key (response_id)
);

# bot_survey_response_answers
DROP TABLE IF EXISTS bot_survey_response_answers;
CREATE TABLE bot_survey_response_answers(
  response_answer_id bigint auto_increment
, response_id int not null
, question_id int not null
, question_order int not null
, answer_time TIMESTAMP not null
, answer_text varchar(1024) not null
, PRIMARY KEY (response_answer_id)
, FOREIGN KEY (response_id) REFERENCES bot_survey_responses(response_id)
);

# survey_branching_logic 
CREATE TABLE survey_branching_logic (
  branch_logic_id int not null auto_increment
, question_id int not null
, magic_text varchar(1024) not null
, next_question_id_if_magic int not null
, primary key (branch_logic_id)
);

