import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker
import datetime
import time
from pandas import DataFrame
import random
import pandas as pd
import json
import boto3

class Listener_Reminder():
    def __init__(self, user, pw, username, password, address, databasename):
        self.message = "It is time to listen to Data Skeptic's podcasts! "
        engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (username, password, address, databasename),pool_size=3, pool_recycle=3600)
        self.internal = engine_internal
        #test
        try:
            self.internal.execute("SHOW DATABASES;")
            print('The connection is successful.')
        except:
            print('The connection fails.')
            raise
        self.user= user
        self.pw = pw
        
           
    def save_reminder_task (self, contact_type, contact_account, time_zone, reminder_time, reminder_time_server, episode_title, episode_link = None):
        # What special characters may have in episode titles and links?
        if episode_link and episode_title:
            episode_link = episode_link.replace("'", "\\'")
            episode_link = episode_link.replace(";", "\\;")
            episode_link = episode_link.replace("&", "\\&")
            episode_link = episode_link.replace("%", "%%")
            episode_link = '<a href="' + episode_link + '">' + episode_title + '</a> '
            print("episode_link is ", episode_link )
        try:
            template = """
                        INSERT INTO reminder_schedule (contact_type, contact_account, time_zone, reminder_time, 
                        reminder_time_server, episode_title, episode_link) 
                        Values ('{contact_type}', '{contact_account}', '{time_zone}', '{reminder_time}', 
                        '{reminder_time_server}', '{episode_title}', '{episode_link}')
                       """
            query = template.format(contact_type = contact_type, contact_account = contact_account, time_zone = time_zone, reminder_time= reminder_time, 
                        reminder_time_server = reminder_time_server, episode_title=episode_title, episode_link=episode_link)
            conn = self.internal.connect()
            conn.execute(query)
            conn.close()
        except: 
            print("Error in saving task into reminder_schedule table.")
            raise

    def send_email(self, user_email, send_time,episode_title = None, episode_link = None):
            client = boto3.client('ses',
                        region_name = 'us-east-1', 
                        aws_access_key_id = self.user, 
                        aws_secret_access_key = self.pw
                        )
            source_email = "xfzhengnankai@gmail.com"
            destination_email = ["fayezheng1010@gmail.com", user_email] #add "kyle@dataskeptic.com" later when everything is fixed.
            reply_to_email = source_email
            if episode_title is None:
                episode_title = ""
            if episode_link is None:
                episode_link = ""

            response = client.send_email(
                        Source= source_email,
                        Destination={'ToAddresses': destination_email},
                        Message={
                            'Subject': {
                                'Data': 'A reminder from Data Skeptic!'
                            },
                            'Body': {
                                'Text': {'Data': self.message + episode_title + " " + episode_link}
                            }
                        },
                        ReplyToAddresses=[reply_to_email]
                    )
            return response if 'ErrorResponse' in response else 'successful. Check email box.'  
            
    def send_sms(self, user_phone,send_time, episode_title = None, episode_link = None):
        client = boto3.client(
            "sns",
            aws_access_key_id=self.user,
            aws_secret_access_key=self.pw,
            region_name="us-east-1"
        )
        client.publish(
            # phone number has to be in this form: "+12223334444"
            PhoneNumber = user_phone,  # Note the formate of the phone number. It's got to be in something called E.164 format.
            Message = self.message  + episode_title + " " + episode_link
        )

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
   
