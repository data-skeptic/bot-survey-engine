import sqlalchemy
import pymysql
import re
import boto3
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import sessionmaker
# import datetime
# import time
# from pandas import DataFrame
import json
# import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger
# from datetime import date

class Listener_Reminder():
    def __init__(self, user, pw, username, password, address, databasename):
        self.message = "It is time to listen to Data Skeptic! "
        engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (username, password, address, databasename),pool_size=3, pool_recycle=3600)
        self.internal = engine_internal
        #test
        try:
            self.internal.execute("SHOW DATABASES;")
            # print('The connection is successful.')
        except:
            #print('The connection fails.')
            raise
        self.user= user
        self.pw = pw

    def save_reminder_task (self, contact_type, contact_account, reminder_time, episode_titles = None, episode_links = None):
        # What special characters may have in episode titles and links?
        if episode_links and episode_titles:
            print("listener_reminder: episode_links and titles are not empty and they are ",episode_links,episode_titles)
            for i in range(len(episode_links)):
                episode_title = episode_titles[i]
                episode_title = episode_title.replace("'", "\\'")
                episode_title = episode_title.replace(";", "\\;")
                episode_title = episode_title.replace("&", "\\&")
                episode_title = episode_title.replace("%", "%%")
                #print("episode_title is ", episode_title )
                episode_link = episode_links[i]
                episode_link = episode_link.replace("'", "\\'")
                episode_link = episode_link.replace(";", "\\;")
                episode_link = episode_link.replace("&", "\\&")
                episode_link = episode_link.replace("%", "%%")
                episode_link = '<a href="' + episode_link + '">' + episode_title + '</a> '
                #print("episode_link is ", episode_link )
                try:
                    template = """
                                INSERT INTO reminder_schedule (contact_type, contact_account, reminder_time, 
                                episode_title, episode_link) 
                                Values ('{contact_type}', '{contact_account}', '{reminder_time}', 
                                '{episode_title}', '{episode_link}')
                               """
                    query = template.format(contact_type = contact_type, contact_account = contact_account, reminder_time= reminder_time, episode_title=episode_title, episode_link=episode_link)
                    conn = self.internal.connect()
                    conn.execute(query)
                    conn.close()
                except: 
                    print("listener_reminder: Error in saving task into reminder_schedule table.")
                    raise
        else:
            episode_title = "None"
            episode_link = "None"
            try:
                template = """
                            INSERT INTO reminder_schedule (contact_type, contact_account, reminder_time, 
                            episode_title, episode_link) 
                            Values ('{contact_type}', '{contact_account}', '{reminder_time}', 
                            '{episode_title}', '{episode_link}')
                           """
                query = template.format(contact_type = contact_type, contact_account = contact_account, reminder_time= reminder_time, episode_title=episode_title, episode_link=episode_link)
                conn = self.internal.connect()
                conn.execute(query)
                conn.close()
            except: 
                print("listen_reminder: Error in saving task into reminder_schedule table.")
                raise
    def send_message(self, contact_type, contact_account,episode_title = None, episode_link = None):
        message = 'Listen to Data Skeptic on iTunes, Spotify, Stitcher, or at dataskeptic.com'
        html_message = '<p>' + message + '</p>'
        if len(episode_link) > 5:
            html_message = html_message + episode_link
        if contact_type == 'email':
            client = boto3.client('ses',
                        region_name = 'us-east-1', 
                        aws_access_key_id = self.user, 
                        aws_secret_access_key = self.pw
                        )
            source_email = "kyle@dataskeptic.com"
            destination_email = [contact_account] #add "kyle@dataskeptic.com" later when everything is fixed.
            reply_to_email = source_email
            try:
                response = client.send_email(
                            Source= source_email,
                            Destination={'ToAddresses': destination_email},
                            Message={
                                'Subject': {
                                    'Data': 'A reminder from Data Skeptic!'
                                },
                                'Body': {
                                    'Html': {
                                        'Data': html_message
                                    }
                                }
                            },
                            ReplyToAddresses=[reply_to_email]
                        )
            except:
                print('listener_reminder: error in sending email. Check the email address.')
            #return response if 'ErrorResponse' in response else 'successful. Check email box.' 
    def send_message2(self, contact_type, contact_account,episode_titles = [], episode_links = []):
        message = 'Listen to Data Skeptic on iTunes, Spotify, Stitcher, or at dataskeptic.com'
        html_message = '<p>' + message + '</p>'
        for link in episode_links:
            html_message = html_message + link + "\n" 
        if contact_type == 'email':
            client = boto3.client('ses',
                        region_name = 'us-east-1', 
                        aws_access_key_id = self.user, 
                        aws_secret_access_key = self.pw
                        )
            source_email = "kyle@dataskeptic.com"
            destination_email = [contact_account] #add "kyle@dataskeptic.com" later when everything is fixed.
            reply_to_email = source_email
            try:
                response = client.send_email(
                            Source= source_email,
                            Destination={'ToAddresses': destination_email},
                            Message={
                                'Subject': {
                                    'Data': 'A reminder from Data Skeptic!'
                                },
                                'Body': {
                                    'Html': {
                                        'Data': html_message
                                    }
                                }
                            },
                            ReplyToAddresses=[reply_to_email]
                        )
            except:
                print('listener_reminder: error in sending email. Check the email address.')
            #return response if 'ErrorResponse' in response else 'successful. Check email box.'  
        if contact_type == 'sms':
            sms_message = message
            for i in range(len(episode_links)):
                episode_link = episode_links[i]
                episode_title = episode_titles[i]
                if len(episode_link) > 5:
                    episode_link = re.findall(r'"([^"]*)"', episode_link)[0]
                    sms_message = sms_message + " " + episode_title+ " " + episode_link + " "
            
            client = boto3.client(
                "sns",
                aws_access_key_id = self.user,
                aws_secret_access_key = self.pw,
                region_name="us-east-1"
            )
            try:
                response = client.publish(
                    PhoneNumber = contact_account,  
                    Message = sms_message)
            except:
                print('listener_reminder: error in sending message. Check the phone number.')

    def checkForReminders(self):
        query = "SELECT * FROM reminder_schedule WHERE scheduled = 0 and reminder_time > NOW() and reminder_time < DATE_ADD(NOW(), INTERVAL 5 MINUTE) "
        r = self.internal.execute(query)
        n= r.rowcount
        if n > 0:
            print("listener_reminder: The number of new task is ", n)
        for i in range(n):
            reminder_task = r.fetchone()
            reminder_id = reminder_task['task_id']
            reminder_time = reminder_task['reminder_time']
            contact_type = reminder_task['contact_type']
            contact_account = reminder_task['contact_account']
            episode_title = reminder_task['episode_title']
            episode_link = reminder_task['episode_link']
            print("listener_reminder: reminder task is ", reminder_time, contact_type, contact_account, episode_title, episode_link)
            self.send_message(contact_type, contact_account,episode_title, episode_link)
            template = "UPDATE reminder_schedule SET scheduled=1 WHERE task_id = '{reminder_id}' "
            query =  template.format(reminder_id = reminder_id)
            self.internal.execute(query)

    def checkForReminders2(self):
        query = "SELECT * FROM reminder_schedule WHERE scheduled = 0 and reminder_time > NOW() and reminder_time < DATE_ADD(NOW(), INTERVAL 5 MINUTE) "
        r = self.internal.execute(query)
        n= r.rowcount
        if n > 0:
            print("listener_reminder: The number of new task is ", n)
        tasks_dict = {}
        for i in range(n):
            reminder_task = r.fetchone()
            reminder_id = reminder_task['task_id']
            reminder_time = reminder_task['reminder_time']
            contact_type = reminder_task['contact_type']
            contact_account = reminder_task['contact_account']
            episode_title = reminder_task['episode_title']
            if episode_title == "None":
                episode_title = ""
                
            episode_link = reminder_task['episode_link']
            if episode_link == "None":
                episode_link = ""
            print("listener_reminder: reminder task is ", reminder_time, contact_type, contact_account, episode_title, episode_link)
            if contact_account not in tasks_dict.keys():
                tasks_dict[contact_account] = {"contact_type": contact_type, "episode_titles":[episode_title],'episode_links':[episode_link]}
            else:
                print('listen_reminder: episode_title and episode_link are ', episode_title, episode_link)
                tasks_dict[contact_account]['episode_titles'].append(episode_title)
                tasks_dict[contact_account]['episode_links'].append(episode_link)
            template = "UPDATE reminder_schedule SET scheduled=1 WHERE task_id = '{reminder_id}' "
            query =  template.format(reminder_id = reminder_id)
            self.internal.execute(query)
        if len(tasks_dict) > 0:
            print('listener_reminder: tasks_dict is ', tasks_dict)
        for contact_account, value in tasks_dict.items():      
            self.send_message2(value['contact_type'], contact_account,value['episode_titles'], value['episode_links'])
        

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
   
