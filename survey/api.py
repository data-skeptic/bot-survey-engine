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
    #def post(self, response_id = None, question_id, question_order):
    def post(self):
        r = request.get_data()
        req = json.loads(r.decode('utf-8'))

        answer_text = req['answer_text']
        question_id = req['question_id']
        question_order = req['question_order']
        if 'response_id' in req:
            response_id = req['response_id']
        else:
            response_id = None
        
        magic_text = survey_instance.get_magic_reply(answer_text, question_id)
        next_question_id = survey_instance.get_next_question_id(question_id, answer_text)
        response_id, response_answer_id = survey_instance.save_answer(response_id, question_id, question_order, answer_text)
    
        resp = { "magic_text": magic_text, "next_question_id": int(next_question_id)}
        return resp

if __name__ == '__main__':
    logger.info("Init")
    app = Flask(__name__)
    api = Api(app)
    parser = reqparse.RequestParser()
    api.add_resource(GetQuestion,  '/survey/question/<int:question_id>')
    api.add_resource(SaveAnswer,   '/survey/response/answer/save')
    app.run(host='0.0.0.0', debug=False, port=3500)
    logger.info("Ready")
    
