# coding: utf-8
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import numpy as np
import configparser
import json
import requests
import xmltodict
from bs4 import BeautifulSoup
import time
import pickle
import os
import gensim
import csv
import seaborn as sns
import smart_open

import json
from sklearn.feature_extraction.text import TfidfVectorizer
import episodes_preparation as ep

import nltk
import string
from nltk.corpus import stopwords
from collections import Counter

import scipy.sparse as sparse

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer

from gensim.models import Phrases

import warnings
warnings.filterwarnings('ignore')

########################## load files ######################
class episode():
    def __init__(self, update_episode, size, min_count, window, name):
        # episode preparation
        ep.run(update_episode, size, min_count, window, name)
        mdir = os.path.dirname(os.path.abspath(__file__))
        self.episodes_json_fname = mdir+'/text/episodes_json.txt'  # store all information
        self.episodes_desc = mdir+'/text/episode_descs_titles.txt' # store all descriptions
        self.episodes_corpus = mdir+'/text/episode_corpus.txt' # store corpus: a list of sentences (words in sentences are tokenlized, lowercased and so on)
        # self.word_vec_file = mdir+'/word_vec/word2vector_model_question_answer_' + name + '.csv'
        # self.voc_dic_file = mdir+'/vocab_dict/vocab_dict_question_answer_' + name +'.csv' # store vocab_dictionary
        self.word_vec_file = mdir + "/word_vec_bigram/all_posts_word_vec.csv"
        self.voc_dic_file = mdir + '/vocab_dic_bigram/vocab_dict_question_answer.csv'
        self.weighted_vecs_file = mdir+'/episode_vec_bigram/episode_vec_weighted.csv' # store weighted vectors

        # load episode informaiton and save it to variables.
        file_name = self.episodes_json_fname
        with open(file_name) as data_file:    
            episode_json = json.load(data_file)
        print('The total number of episodes is ',len(episode_json.keys()))
        descriptions = list(episode_json.keys())
        descToTitle = {}
        descToLink = {}
        descToNum = {}
        for desc  in descriptions:
            descToTitle[desc] = episode_json[desc]['title']
            descToLink[desc] = episode_json[desc]['link']
            descToNum[desc] = episode_json[desc]['num'] 

        self.descriptions = descriptions
        self.descToNum = descToNum
        self.descToTitle = descToTitle
        self.descToLink = descToLink
        print('Retrival of episodes information is done.') 
        # this is for future print. when we recommend some episodes, we should also be able to print the link, title, descriptions.

        # get vocab_dic from SO
        with open(self.voc_dic_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            self.vocab_dic = dict(reader)
        for k, value in self.vocab_dic.items():
            self.vocab_dic[k] = int(value)

        print("Getting vocab_dictionary are done in recommendation python file.")
        self.vocab = list(self.vocab_dic.keys())
    
        self.vectorizer = TfidfVectorizer(min_df=1,vocabulary = self.vocab_dic)

        self.episode_vec_weighted_df = pd.read_csv(self.weighted_vecs_file, index_col=0)
        print("Getting weighted vectors for all episodes is done.")

        self.word_vecs_df = pd.read_csv(self.word_vec_file, index_col = 0)
        print('Getting word vectors trained from SO is done in rcm.py')
        
        #self.bigram, self.episode_corpus,self.vocab_tf_idf,self.vocab_dict_tf_idf = self.bigram_recommendation_prepare()
        mdir = os.path.dirname(os.path.abspath(__file__))
        fname = '/episodes_preprocess/episodes_sentences_nonstopwords.pickle'
        with open(mdir+fname, 'rb') as f:
            self.episodes_sentences_nonstopwords = pickle.load(f)
        fname = '/episodes_preprocess/episodes_corpus.pickle'
        with open(mdir+fname, 'rb') as f:
            self.episodes_corpus = pickle.load(f)
        fname = '/SO_bigram/SO_bigram.pkl'
        with open(mdir+fname, 'rb') as f:
            self.bigram = pickle.load(f)
            #print("test bigram....", b'random_walk' in self.bigram.vocab.keys())
            print("size of bigram.vocab is ",len(self.bigram.vocab.keys()))
        print("Initialization is done.")

    def recommend_episode(self,user_request):
        all_episode = self.episode_vec_weighted_df.values
        user_request_corpus = gensim.utils.simple_preprocess(user_request)
        # wordnet_lemmatizer = WordNetLemmatizer()
        # st = LancasterStemmer()
        # #user_request_corpus = [wordnet_lemmatizer.lemmatize(word) for word in user_request_corpus]
        # user_request_corpus = [st.stem(word) for word in user_request_corpus]
        temp = self.bigram[user_request_corpus]# temp is a list of words(unigram and bigram)
        result = []
        for element in temp:
            key = element.split("_")
            if len(key) == 1:
                if element not in stopwords.words('english'):
                    result.append(element)
            if len(key) > 1 and not any([word in stopwords.words("english") for word in key]):
                result.append(element)
            for word in key:
                if word not in stopwords.words("english"):
                    result.append(word)
            result = list(set(result))
        # use doc vec to make recommendation
        print("after preprocessing, the result of user's request is", result)
        temp = self.episodes_corpus + [" ".join(result)]
        all_tf_idf = self.vectorizer.fit_transform(self.episodes_corpus + [" ".join(result)])
        user_tf_idf = all_tf_idf[-1,:]
        episodes_tf_idf = all_tf_idf[0:-1,:]
        # print("user_tf_idf is ", user_tf_idf.nonzero())
        # for j in range(episodes_tf_idf.shape[0]):
        #     if sum([episodes_tf_idf[j,k] for k in user_tf_idf.nonzero()[1]]) > 0:
        #         print(cosine_similarity(X=user_tf_idf,Y =episodes_tf_idf[j,:]))

        threshold = 4
        if len(result) < threshold:
            print(cosine_similarity(X=episodes_tf_idf, Y=user_tf_idf).shape)
            cos_similarities = cosine_similarity(X=user_tf_idf,Y=episodes_tf_idf)[0]
            similarity_threshold = 0.10

        else:
            similarity_threshold = 0.70
            df = self.word_vecs_df 
            user_weighted_vec = user_tf_idf.dot(df)[0].reshape(1, -1)
            cos_similarities = cosine_similarity(X=user_weighted_vec, Y=all_episode)[0]
        
        most_similar_index = cos_similarities.argsort()[-4:][::-1]

        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& User's request is:  " + user_request + " &&&&&&&&&&&&&&&&&&&&&&&&\n" )
        result = {}
        rank  = 1
        print('most_similary index are ', most_similar_index)
        for i in most_similar_index:
            if cos_similarities[i] >= similarity_threshold:
                print("--------------------The episode has cosine similarity "+str(cos_similarities[i])+ "-------------------\n")
                print( "\n")
                j = len(self.descriptions) - i  
                desc = [key for key, value in self.descToNum.items() if value == j][0]
                print(str(self.descToTitle[desc]) + "\n")
                print(str(self.descToLink[desc]) + "\n")
                print(str(desc.encode('utf-8')) + "\n")
                result['rank_'+str(rank)] = ({'title':self.descToTitle[desc],'link':self.descToLink[desc],'desc':desc})
                rank += 1 
        return result

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()
