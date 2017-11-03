import boto3
import json
import os

class load_word_vec():
  def __init__(self):
    mdir = os.path.dirname(os.path.abspath(__file__))
    local_filename = mdir + '/all_posts_word_vec.csv'
    if not os.path.exists(local_filename):
      config_path = "/".join(local_filename.split("/")[0:-3]) + "/config/config.json"
      with open (config_path, "r") as myfile:
              data = json.load(myfile)
              user = data['aws']['accessKeyId']
              pw = data['aws']['secretAccessKey']
              region = data['aws']['region']
              BUCKET_NAME = data['aws']['bucket_name']
              s3_filename = data['aws']['file_name']
              print(BUCKET_NAME)
      s3= boto3.resource('s3',region_name = region, 
                          aws_access_key_id = user, 
                          aws_secret_access_key = pw)
      #s3_filename = 'all_posts_word_vec.csv'
      s3_filename = 'README.md'
      print(BUCKET_NAME, s3_filename, "downloading...")
      s3.Bucket(BUCKET_NAME).download_file(s3_filename, local_filename)

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
