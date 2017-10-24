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
from datetime import datetime, timedelta

sys.path.insert(0, './episodes')
import rcm
from rcm import episode

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
update_episode = True
print('name in episode part is ', name)
episode_instance = episode(update_episode, size, min_count, window, name)

## long request
user_requests = [
"machine learning",
"recommender system",
"random walk",
"random forest",
"neural network",
"open source",
"deep learning",
"something statistics",
"mcmc",
"music",
"AI",
"artificial intelligence",
"skeptical thinking",
"dropout",
"conference and contest",
"applications of AI",
"I am currently in belgrade for one of my clients. We are working on some interesting algorithms. The food here is very heavy and I think i will need a diet when I get back to LA. But at least it is not raining too much.",
"I want to listen to episodes on decision tree and random forest.",
"I am at my house now and the weather is not good today. So I want to listen to something related to markov chain and Monte Carlo simulation.",
"Could you recommend some episodes on data science projects for beginners?",
"What can artificial intelligence do for human beings? What is the future of artificial intelligence?",
"The error percentage of regression changes with change in the train and test data which I am deciding randomly. Cross validation can overcome this but how do I apply it for my regression model?",
"Evaluating the quality of data.",
"Is there any episode on Facial Recognition? How does Facial Recognition work?",
" I am interested in knowing musical stuff.",
"How to learn machine learning? What books or website do you recommend?",
" Looking for projects on criminal analysis?",
"How to take advantage of Internet, computer,  cloud and other  platform in an effective way?",
"What are the most important knowledge in statistics or probability when doing machine learning?",
"I would like to learn something about random walk, how random walk works in some algorithmes?"
]


## short requests
# user_requests = [
# "random walk",
# "something statistics",
# "mcmc",
# "music",
# "AI",
# "artificial intelligence",
# "skeptical thinking",
# "dropout",
# "machine learning",
# "conference and contest",
# "applications of AI"
# ]
for user_request in user_requests:
	result = episode_instance.recommend_episode(user_request)
	

