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

class episode():
    def __init__(self, update_episode):
        ep.run(update_episode) # episode preparation.
        # get episodes information
        mdir = os.path.dirname(os.path.abspath(__file__))
        self.episodes_json_fname = mdir+'/text/episodes_json.txt'
        with open(self.episodes_json_fname) as data_file:    
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
        #get word_vectors trained from SO

        self.word_vec_file = mdir + "/word_vec_bigram/all_posts_word_vec.csv"
        self.word_vectors = pd.read_csv(self.word_vec_file, index_col=0)
        print('Recommendation: The shape of word_vectors is ',self.word_vectors.shape)
        #get vocabulary dictionary from SO
        voc_dic_file = mdir +"/vocab_dic_bigram/vocab_dict_question_answer.csv"
        with open(voc_dic_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            self.vocab_dic = dict(reader)
        for k, value in self.vocab_dic.items():
            self.vocab_dic[k] = int(value)
        #get Phrase object SO_bigram trained from SO
        fname = mdir+'/SO_bigram/SO_bigram.pkl'
        with open(fname, 'rb') as f:
            self.bigram = pickle.load(f)
            #print("test bigram....", b'random_walk' in self.bigram.vocab.keys())
            print("size of bigram.vocab is ",len(self.bigram.vocab.keys()))
        # get preprocessed results of episodes
        fname = mdir +'/episodes_preprocess/episodes_corpus.pickle'
        with open(fname, 'rb') as f:
            self.episodes_corpus = pickle.load(f)

        fname = mdir +'/episodes_preprocess/episodes_sentences_nonstopwords.pickle'
        with open(fname, 'rb') as f:
            self.episodes_sentences_nonstopwords = pickle.load(f)

        self.episodes_words_filtered = []
        for e in self.episodes_sentences_nonstopwords:
            self.episodes_words_filtered.append(list(set(e).intersection(set(self.vocab_dic.keys()))))

        fname = mdir +'/episodes_preprocess/episodes_title_corpus.pickle'
        with open(fname, 'rb') as f:
            self.episodes_corpus_title = pickle.load(f)

        fname = mdir +'/episodes_preprocess/episodes_sentences_nonstopwords_title.pickle'
        with open(fname, 'rb') as f:
            self.episodes_sentences_nonstopwords_title = pickle.load(f)

        self.episodes_words_filtered_title = []
        for e in self.episodes_sentences_nonstopwords_title:
            self.episodes_words_filtered_title.append(list(set(e).intersection(set(self.vocab_dic.keys()))))

        print("Initialization is done.")
    #preprocess user's request

    def preprocess(self, user_request):
        user_request_corpus = gensim.utils.simple_preprocess(user_request)
        temp = self.bigram[user_request_corpus]# temp is a list of words(unigram and bigram)
        user_corpus = []
        for element in temp:
            key = element.split("_")
            if len(key) == 1:
                if element not in stopwords.words('english'):
                    user_corpus.append(element)
            if len(key) > 1 and not any([word in stopwords.words("english") for word in key]):
                user_corpus.append(element)
            for word in key:
                if word not in stopwords.words("english"):
                    user_corpus.append(word)
            user_words = list(set(user_corpus).intersection(set(self.vocab_dic.keys())))
        return user_words # a list of words with bigram, without stopwords and remove words not in vocabulary.

    def get_user_tf_idf(self, user_words):
        vectorizer = TfidfVectorizer(min_df=1,vocabulary = self.vocab_dic)
        all_tf_idf = vectorizer.fit_transform(self.episodes_corpus + [" ".join(user_words)])
        user_tf_idf = all_tf_idf[-1,:]
        user_tf_idf_dict = {word:user_tf_idf[0,self.vocab_dic[word]] for word in user_words}
        user_tf_idf_df = pd.DataFrame([user_tf_idf_dict], columns = user_tf_idf_dict.keys()).T
        user_tf_idf_df.columns = ['tf_idf']
        user_tf_idf_df /=user_tf_idf_df.sum(axis = 0)
        return user_tf_idf_df

    def get_score(self, i, user_words,user_tf_idf_df): # the ith episode
        episode_words = self.episodes_words_filtered[i]
        X = self.word_vectors.loc[episode_words,:]
        Y = self.word_vectors.loc[user_words,:]
        cos_similarities = cosine_similarity(X = X.values, Y = Y.values)
        cos_similarities_df = pd.DataFrame(cos_similarities, index = episode_words, columns = user_words) 
        max_cos_similarities = cos_similarities_df.max(axis = 0)
        max_cos_similarities.sort_index(inplace=True)
        user_tf_idf_df.sort_index(inplace=True)
        score = np.dot(max_cos_similarities.values, user_tf_idf_df.values)[0]
        return score, cos_similarities_df

    def get_score_titles(self,i,user_words):   
        episode_words = self.episodes_words_filtered_title[i]
        #print(episode_words)
        X = self.word_vectors.loc[episode_words,:]
        Y = self.word_vectors.loc[user_words,:]
        if X.shape[0] > 0 and Y.shape[0] > 0:
            cos_similarities = cosine_similarity(X = X.values, Y = Y.values)
            cos_similarities_df = pd.DataFrame(cos_similarities, index = episode_words, columns = user_words)
            max_cos_similarities = cos_similarities_df.max(axis = 0)
            max_cos_similarities.sort_index(inplace=True)
            score = max_cos_similarities.values.sum()
        else:
            score = 0
        return score

    def recommend_episode(self, user_request):
        by_title = True
        user_words = self.preprocess(user_request)
        user_tf_idf_df = self.get_user_tf_idf(user_words)
        scores = np.array([self.get_score(i, user_words,user_tf_idf_df)[0] for i in range(len(self.episodes_corpus))]) 
        max_score = scores.max()
        episode_indice = np.where(scores == max_score)[0]
        #print('episode_indice are', episode_indice)
        result = {}
        if len(episode_indice) == 1:
            by_title = False
            best_index = episode_indice
            most_similar_indice = np.array(scores).argsort()[-4:][::-1]
        else:
            by_title = True
            title_scores = [self.get_score_titles(i, user_words) for i in episode_indice]
            most_similar_indice = [episode_indice[i] for i in np.array(title_scores).argsort()[-4:][::-1]]
        
        score_threshold_not_by_title  = 0.70
        score_threshold_by_title  = 0.2
        if by_title:
            score_threshold = score_threshold_by_title
        else:
            score_threshold = score_threshold_not_by_title
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& User's request is:  " + user_request + " &&&&&&&&&&&&&&&&&&&&&&&&\n" )
        result = {}
        rank  = 1
        print('most_similary index are ', most_similar_indice)
        for i in most_similar_indice:
            if scores[i] >= score_threshold:
                print("--------------------The episode has cosine similarity "+str(scores[i])+ "-------------------\n")
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

    
