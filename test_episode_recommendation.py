# import numpy as np
# import pandas as pd
import json
# import os
# import random
import sys
# import datetime
# import logging
# import time
# import boto3
# from datetime import datetime, timedelta

sys.path.insert(0, './episodes')
import recommendation
from recommendation import episode

with open ("./config/config.json", "r") as myfile:
        data = json.load(myfile)
        #mysql
        username = data['mysql']['username']
        address = data['mysql']['address']
        password = data['mysql']['password']
        databasename = data['mysql']['databasename']
        #gensim model
        
update_episode = False
episode_instance = episode(update_episode,username, address,password,databasename)

user_requests = [
"machine learning",
"Data science",
"statistics",
"something statistics",
"recommender system",
"Causal Impact",
"random walk",
"random forest",
"neural network",
"deep learning",
"mcmc",
"music",
"artists and data science",
"open source",
"data source,",
"data lake",
"finance",
"AI",
"artificial intelligence",
"applications of AI",
"conference and contest",
"Computer Vision and Pattern Recognition",
"I am currently in belgrade for one of my clients. We are working on some interesting algorithms. The food here is very heavy and I think i will need a diet when I get back home. But at least it is not raining too much.",
"I want to listen to episodes on decision tree and random forest.",
"Can I trust my machine learning models?",
"Is there any model describing family and marriage?",
"How to reduce false positive and false negative?",
" I want to listen to something related to markov chain and Monte Carlo simulation.",
"It is raining outside today and I am at home. I want to listen to something related to markov chain and Monte Carlo simulation.",
"What can artificial intelligence do for human beings? What is the future of artificial intelligence?",
"The error percentage of regression changes with change in the train and test data which I am deciding randomly. Cross validation can overcome this but how do I apply it for my regression model?",
"How to evaluate the quality of data and the source of the datasets?", 
"Is there any episode on Facial Recognition? How does Facial Recognition work?",
"Is there any episode on facial detection? How does facial Recognition work",
" I am interested in knowing musical stuff",
"How to learn machine learning? What books or websites do you recommend?",
" Looking for projects on criminal analysis.",
"How to take advantage of Internet, computer,  cloud and other platforms in an effective way?",
"What are the most important knowledge in statistics and probability for data scientists?",
"I would like to learn something about random walk. How does random walk work in some algorithms?",
"How can we calculate AUC for classification algorithms?",
"What's the similarities and differences between these 3 methods: bagging, boosting and stacking? Which is the best one? And why?",
"Could you introduce the procedures in neural networks?",
"What are possible problems in training neural network?"
]



# user_requests = [
# "stats",
# "bonferroni adjustment",
# "macaroni adjustment",
# "tesla",
# "cloud ML models",
# "google adwords",
# "depth perception",
# "computerized depth perception",
# "deep learning and healthcare",
# "python",
# "sklearn",
# "unsupervised learning",
# "complexity",
# "computational complexity",
# "microsoft",
# "LSTMs",
# "zestimate",
# "RNNs",
# "statistical testing",
# "what two do with two continuous variables",
# "databases",
# "docker",
# "GANs",
# "elections",
# "police and data",
# "finance",
# "bicycling",
# "variance",
# "anova",
# "protocols",
# "LIME",
# "noisy data",
# "Hadley Wickham",
# "game theory",
# "time series analysis",
# "word clouds"]

for user_request in user_requests:
	#print(user_request)
	result = episode_instance.recommend_episode(user_request)
	

