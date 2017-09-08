from flask import Flask
from flask import Response
from flask_restful import reqparse, Resource, Api, request
from flask import Markup
import numpy as np
import pandas as pd
import json
import os
import sys
import datetime
import time
import logging
import survey
from survey import Survey

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


survey_instance = survey.create_survey()


class GetQuestion(Resource):
    def get(self, question_id):
        question_text = survey_instance.get_question_text(question_id)
        resp = {
            "question_id": question_id,
            "question_text": question_text
        }
        return resp

class SaveAnswer(Resource):
    def post(self, question_id):
        # todo list:
        # get user's answer to question_id
        # save to database: save_answer(self, response_id, question_id, question_order, answer_text) 
        # return magic text: get_magic_reply(self, answer_text, question_id) 
        # return next_question_id: get_next_question_id(self, question_id, answer):
        resp = { "magic_text": "Great job", "next_question_id": 2}
        return resp

# GET /survey/question?question_id=2
# {"question_id": 2, "question_text": "blah}

# POST /survey/response/answer/save

if __name__ == '__main__':
    logger.info("Init")
    app = Flask(__name__)
    api = Api(app)
    parser = reqparse.RequestParser()
    api.add_resource(GetQuestion,          '/survey/question/<int:question_id>')
    api.add_resource(SaveAnswer,           '/survey/response/answer/save')
    app.run(host='0.0.0.0', debug=False, port=3500)
    logger.info("Ready")
