from pandas import DataFrame
import pandas as pd
import boto3

class listener_reminder():
    def __init__(self):
        self.message = "It is time to listen to Data Skeptic's podcasts!"
        with open ("../config/config.json", "r") as myfile:
                data = json.load(myfile)
                self.user = data['aws']['accessKeyId']
                self.pw= data['aws']['secretAccessKey']

    def send_email(self, user_email):
            client = boto3.client('ses',
                        region_name = 'us-east-1', 
                        aws_access_key_id = self.user, 
                        aws_secret_access_key = self.pw
                        )
            source_email = "kyle@dataskeptic.com"
            destination_email = ["fayezheng1010@gmail.com", user_email] #add "kyle@dataskeptic.com" later when everything is fixed.
            reply_to_email = source_email
            response = client.send_email(
                        Source= source_email,
                        Destination={'ToAddresses': destination_email},
                        Message={
                            'Subject': {
                                'Data': 'A reminder from Data Skeptic!'
                            },
                            'Body': {
                                'Data': self.message # 
                            }
                        },
                        ReplyToAddresses=[reply_to_email]
                    )
            return response if 'ErrorResponse' in response else 'successful. Check email box.'  
            
    def send_sms(self, user_phone):
        client = boto3.client(
            "sns",
            aws_access_key_id=self.user,
            aws_secret_access_key=self.pw,
            region_name="us-east-1"
        )
        client.publish(
            # phone number has to be in this form: "+12223334444"
            PhoneNumber = user_phone,  # Note the formate of the phone number. It's got to be in something called E.164 format.
            Message = self.message
        )
def run_reminder(contact_type, contact_account):
    reminder_ins = listener_reminder()
    if contact_type == 'email':
        reminder_ins.send_email(contact_account)
    if contact_type == "sms":
        reminder_ins.send_sms(contact_account)
    print("message has been sent. Please check.")

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
   
