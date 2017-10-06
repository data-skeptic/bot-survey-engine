#10_02_17
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
import rcm
import random
from rcm import episode

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

update_episode = True
episode_instance = episode(update_episode)

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

if __name__ == '__main__':
    logger.info("Init")
    app = Flask(__name__)
    api = Api(app)
    parser = reqparse.RequestParser()

    api.add_resource(random_recommendation,  '/episode/random_recommendation')
    api.add_resource(give_recommendation,   '/episode/recommendation')
    app.run(host='0.0.0.0', debug=False, port=3500)
    logger.info("Ready")
    
