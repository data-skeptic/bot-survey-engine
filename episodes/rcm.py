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
from sklearn.metrics.pairwise import cosine_similarity
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

########################## load files ######################
class episode():

    def __init__(self): 
        self.episodes_json_fname = './text/episodes_json.txt'  # store all information
        self.episodes_desc = './text/episode_descs_titles.txt' # store all descriptions
        self.episodes_corpus = './text/episode_corpus.txt' # store corpus: a list of sentences (words in sentences are tokenlized, lowercased and so on)
        self.word_vec_file = './word_vec/word2vector_model_question_answer_200_6_2.csv'
        self.voc_dic_file = './vocab_dict/vocab_dict_question_answer_200_6_2.csv' # store vocab_dictionary
        self.weighted_vecs_file = './episode_vec/episode_vec_weighted.csv' # store weighted vectors

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
        
        ## get vocab_dic from SO
        
        with open(self.voc_dic_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            self.vocab_dic = dict(reader)

        for k, value in self.vocab_dic.items():
            self.vocab_dic[k] = int(value)
        print("Getting word vectors trained from SO and getting vocab_dictionary are done.")
        self.vocab = list(self.vocab_dic.keys())

        # get corpus of episodes
        self.corpus = []
        fname = self.episodes_corpus
        with open(fname, 'r') as f:
            for line in f:
                self.corpus.append(line)
  
        self.vectorizer = TfidfVectorizer(min_df=1,vocabulary = self.vocab_dic)
        self.episode_vec_weighted_df = pd.read_csv(self.weighted_vecs_file, index_col=0)
        self.word_vecs_df = pd.read_csv(self.word_vec_file, index_col = 0)
        print("Initialization is done.")


    def get_doc_weighted_vec(self, doc_corpus, weighted = True): #  doc_corpus a list of words
        self.tf_idf = self.vectorizer.fit_transform(self.corpus)
        tf_idf = self.vectorizer.fit_transform([" ".join(doc_corpus)])
        #tf_idf = self.vectorizer.fit_transform([" ".join(doc_corpus)]+self.corpus)
        df = self.word_vecs_df 
        related_rows = df.loc[sorted(list(set(doc_corpus).intersection(set(self.vocab)))), :] 
        print(related_rows.shape)
        print(tf_idf)
        print(tf_idf[0,:])
        if weighted:
            weights = []
            ind = sorted(tf_idf[0,:].nonzero()[1])
            print(ind)
            if sum([self.vectorizer.vocabulary_[related_rows.index[j]] != ind[j] for j in range(len(ind))]) != 0:
                print("words position don't match")
                return 
            for j in ind:
                weights.append(tf_idf[0,j])
            weights = np.array(weights)/sum(weights)
        else:
            weights = [1/related_rows.shape[0]] * related_rows.shape[0]
        
        if related_rows.shape[0] != len(weights):
            print(i)
            print(related_rows.shape[0])
            print(len(weights))
        
        result = related_rows.T * weights
        print('weighted vector is ', result.sum(axis = 1))
        return result.sum(axis = 1)

    

     ######################## make recommendation ######################
    def recommend_episode(self,user_request): # add parameter user_request 
        print("Hello.", user_request)
        all_episode = self.episode_vec_weighted_df.values
        print("*****************************************************" + "\n")
        user_request_corpus = gensim.utils.simple_preprocess(user_request)
        print(user_request_corpus)
        #X_user = self.vectorizer.fit_transform([" ".join(user_request_corpus)])
        #print(str(X_user.shape) + "\n")
        user_weighted_vec = self.get_doc_weighted_vec(user_request_corpus)
        cos_similarities = cosine_similarity(X=user_weighted_vec, Y=all_episode)

        cos_similarities = cos_similarities[0]
        print(cos_similarities.shape)

        most_similar = cos_similarities.argsort()[-4:][::-1]
        #print(str(most_similar) + "\n")
        threshold = 0.60
        print("User's request is: " + user_request + "\n" )
        result = {}
        rank  = 1
        print('most_similary index are ', most_similar)
        for i in most_similar:
            if cos_similarities[i] > threshold:
                print("--------------------The episode has cosine similarity is "+str(cos_similarities[i])+" with user's request-------------------------\n")
                print( "\n")
                j = len(self.descriptions) - i  # j = 111; i = 68
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
   
    
   


