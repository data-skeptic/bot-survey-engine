#10_19_17
from flask import Flask
from flask import Response
from flask_restful import reqparse, Resource, Api, request
from flask import Markup
import numpy as np
import pandas as pd
import json
import os
import random
import sys
import datetime
import time
import logging

import time
import boto3
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.date import DateTrigger
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger

from datetime import datetime, timedelta

import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()



sys.path.insert(0, './survey')
import survey
from survey import Survey

sys.path.insert(0, './episodes')
import rcm
from rcm import episode

sys.path.insert(0, './listener_reminder')
import listener_reminder
from listener_reminder import Listener_Reminder


logname = sys.argv[0]
logger = logging.getLogger(logname)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.INFO)

logfile = '/var/tmp/' + logname + '.log'
ldir = os.path.dirname(logfile)
if not(os.path.isdir(ldir)):
    os.makedirs(ldir)
hdlr = logging.FileHandler(logfile)

hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
stdout = logging.StreamHandler()
stdout.setFormatter(formatter)
logger.addHandler(stdout)

version = "0.0.1"

#survey
with open ("./config/config.json", "r") as myfile:
        data = json.load(myfile)
        #mysql
        username = data['mysql']['username']
        address = data['mysql']['address']
        password = data['mysql']['password']
        databasename = data['mysql']['databasename']
        #gensim model
        size = data['model_paras']['size']
        min_count = data['model_paras']['min_count']
        window = data['model_paras']['window']
        name = str(size) + "_" + str(window) + "_"+ str(min_count) 
        # aws
        user = data['aws']['accessKeyId']
        pw = data['aws']['secretAccessKey']
        url = "mysql://%s:%s@%s/%s" % (username, password, address,databasename)
survey_instance = Survey(username, password, address, databasename)

class GetQuestion(Resource):
    def get(self, question_id):
        question_text = survey_instance.get_question_text(question_id)
        resp = {
            "question_id": question_id,
            "question_text": question_text
        }
        return resp

class SaveAnswer(Resource):
    #def post(self, response_id = None, question_id, question_order):
    def post(self):
        r = request.get_data()
        req = json.loads(r.decode('utf-8'))

        answer_text = req['answer_text']
        question_id = req['question_id']
        question_order = req['question_order']
        if 'response_id' in req:
            response_id = req['response_id']
            print('response_id is ', response_id)
        else:
            response_id = None
            print('response_id is none.')
        
        magic_text = survey_instance.get_magic_reply(answer_text, question_id)
        next_question_id = survey_instance.get_next_question_id(question_id, answer_text)
        response_id, response_answer_id = survey_instance.save_answer(response_id, question_id, question_order, answer_text)
        
        resp = { "magic_text": magic_text, "response_id": response_id, "next_question_id": int(next_question_id)}
        if next_question_id == -1:
            content = survey_instance.survey_retrieval(next_question_id, response_id)
            print(content)
            if content.empty:
                print("No data for the current survey.")
            else:
                survey_instance.send_email(content, user, pw)
        return resp

# episode
update_episode = True
print('name in episode part is ', name)
episode_instance = episode(update_episode, size, min_count, window, name)

class random_recommendation(Resource):
    def get(self):
        descriptions = episode_instance.descriptions
        descToNum = episode_instance.descToNum
        descToTitle = episode_instance.descToTitle
        descToLink = episode_instance.descToLink
        total = len(descToLink)
        rand_ind = random.sample(list(descToNum.values()), 1)[0] - 1
        desc = descriptions[rand_ind]
        return {'desc':desc, 'num':descToNum[desc], 'link':descToLink[desc],'title':descToTitle[desc]}

class give_recommendation(Resource):
    def post(self):
        r = request.get_data()
        req = json.loads(r.decode('utf-8'))
        user_request = req['request']
        result = episode_instance.recommend_episode(user_request)
        if len(result) > 0:
            return result
        else:
            return None

#listener_reminder

reminder_ins = Listener_Reminder(user, pw, username, password, address, databasename)
## a test.
# contact_type = 'sms'
# contact_account = '+18144414200'
# episode_title = "MCMC"
# episode_link = "https://dataskeptic.com/blog/episodes/2017/data-science-tools-and-other-announcements-from-ignite"
# episode_link = '<a href="' + episode_link + '">' + episode_title + '</a> '
# reminder_ins.send_message(contact_type, contact_account,episode_title , episode_link)

class reminder(Resource):
    def post(self):
        r = request.get_data() # request is RAW body in REST Console.
        user_info = json.loads(r.decode('utf-8'))
        print('user_info is ', user_info)
        contact_type = user_info.get('contact_type')
        contact_account = user_info.get('contact_account')
        #reminder_time = user_info.get('reminder_time') 
        reminder_time = user_info.get('reminder_time')
        episode_title = user_info.get('episode_title')
        episode_link = user_info.get('episode_link')
        # save reminder task into the table.
        reminder_ins.save_reminder_task(contact_type, contact_account,reminder_time, 
                                                episode_title, episode_link)
        return " Reminder will be sent."# + str(alarm_time)


if __name__ == '__main__':
    logger.info("Init")
    app = Flask(__name__)
    api = Api(app)
    parser = reqparse.RequestParser()
    # survey
    api.add_resource(GetQuestion,  '/survey/question/<int:question_id>')
    api.add_resource(SaveAnswer,   '/survey/response/answer/save')
    # episode
    api.add_resource(random_recommendation,  '/episode/random_recommendation')
    api.add_resource(give_recommendation,   '/episode/recommendation')
    # listener_reminder
    api.add_resource(reminder,  '/listener_reminder')
    
    @app.before_first_request 
    def add_tasks():
        #scheduler = BlockingScheduler()
        scheduler = BackgroundScheduler()
        scheduler.add_job(reminder_ins.checkForReminders, 'interval', seconds=30)
        print('Press Ctrl+{0} to exit scheduler'.format('Break' if os.name == 'nt' else 'C'))
        try:
            scheduler.start()

        except (KeyboardInterrupt, SystemExit):
            pass
        scheduler.print_jobs()
        atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0', debug=False, port=3500)

    logger.info("Ready")
    
