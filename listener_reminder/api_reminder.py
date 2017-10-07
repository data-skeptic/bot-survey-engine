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
import random
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

reminder_ins = Listener_Reminder()

class reminder(Resource):
    def post(self):
        r = request.get_data()
        user_info = json.loads(r.decode('utf-8'))
        contact_type = user_info.get('contact_type')
        contact_account = user_info.get('contact_account')
        time_zone = user_info.get('time_zone')
        reminder_time = user_info.get('reminder_time') 
        reminder_time_server = user_info.get('reminder_time_server')
        episode_title = user_info.get('episode_title', None)
        episode_link = user_info.get('episode_link')
        # save reminder task into the table.
        reminder_ins.save_reminder_task(contact_type, contact_account, time_zone, 
                                            reminder_time, reminder_time_server, 
                                                episode_title, episode_link)
        # send email or short message
        if contact_type.lower() == 'email':
            reminder_ins.send_email(contact_account, episode_title, episode_link)
        if contact_type.lower() == "sns":
            reminder_ins.send_sms(contact_account, episode_title, episode_link)
        return "message has been sent. Please check."

if __name__ == '__main__':
    logger.info("Init")
    app = Flask(__name__)
    api = Api(app)
    parser = reqparse.RequestParser()

    api.add_resource(reminder,  '/listener_reminder')
    app.run(host='0.0.0.0', debug=False, port=3500)
    logger.info("Ready")
    
