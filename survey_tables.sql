SHOW databases;
USE survey;
SHOW tables;


# bot_survey_questions;
DROP TABLE IF EXISTS bot_survey_questions;

CREATE TABLE bot_survey_questions (
  question_id int not null auto_increment
, question_text varchar(1024) not null
, primary key (question_id)
);


-- INSERT INTO bot_survey_questions
-- (question_text)
-- VALUES ('When did you start listening to Data Skeptic?'),
-- ('What is your academic background?'),
-- ('Do you consider yourself to be a data scientist?'),
-- ('What is your field of study?'),
-- ('How long have you been in your current role?'),
-- ('Where do you live?'),
-- ('What is your age?'),
-- ('What is your gender?'),
-- ('When and where do you listen to Data Skeptic?'),
-- ('What other podcasts do you listen to on your commute?'),
-- ('What do you like most about Data Skeptic?'),
-- ('In what ways would you like to see the show improve?'),
-- ('Does any episode in your recent memory stand out as being a favorite?  If so, which one?'),
-- ('Thanks for your feedback!  If we have any further questions, we''d like to be able to follow up via email. If that''s ok, please provide your email.  If not, feel free to write n/a.')
-- ;
-- SELECT * FROM bot_survey_questions;

#bot_survey_responses
# This table should get one record every time a survey is started. It will capture metadata like the time it is started.
DROP TABLE IF EXISTS bot_survey_responses;
CREATE TABLE bot_survey_responses(
survey_id int not null auto_increment
,user_id int 
,survey_start_time TIMESTAMP not null
,primary key (survey_id)
);


INSERT INTO bot_survey_responses(survey_id, user_id, survey_start_time) 
values(3, 1, NOW()),
(4,13, NOW());
SELECT * from bot_survey_responses;


# bot_survey_response_answers
DROP TABLE IF EXISTS bot_survey_response_answers;
CREATE TABLE bot_survey_response_answers(
survey_id int not null
,user_id int
,question_id int not null
,question_order int 
,response_time TIMESTAMP not null
,response_text varchar(1024) not null
,FOREIGN KEY (survey_id) REFERENCES bot_survey_responses(survey_id)
);

INSERT INTO bot_survey_response_answers(survey_id, user_id, question_id, question_order, response_time, response_text) 
values(1, 200, 1, 1, NOW(), "In 2015, I started listening to Data Skeptic"),
(1,200,2,2,Now(), "My academic background is Math");
SELECT * from bot_survey_response_answers;



# survey_branching_logic 
# more work to be done.
CREATE TABLE survey_branching_logic (
question_id int not null
,magic_text varchar(1024) not null
,action_to_take 
);


show tables;

