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
        self.word_vec_file = mdir+'/word_vec/word2vector_model_question_answer_' + name + '.csv'
        self.voc_dic_file = mdir+'/vocab_dict/vocab_dict_question_answer_' + name +'.csv' # store vocab_dictionary
        self.weighted_vecs_file = mdir+'/episode_vec/episode_vec_weighted.csv' # store weighted vectors

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

        # get vocab_dic from SO
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

        self.bigram, self.episode_corpus,self.vocab_tf_idf,self.vocab_dict_tf_idf = self.bigram_recommendation_prepare()

        print("Initialization is done.")



    def get_doc_weighted_vec(self, doc_corpus, weighted = True): #  doc_corpus a list of words
        all_tf_idf = self.vectorizer.fit_transform(self.corpus + [" ".join(doc_corpus)])
        tf_idf = all_tf_idf[-1,:]
        df = self.word_vecs_df 
        return tf_idf.dot(df)[0]
    
    def bigram_recommendation_prepare(self):
        translation = str.maketrans(string.punctuation,' '*len(string.punctuation))
        def preprocess():
            lemmatizer = nltk.WordNetLemmatizer()
            sentences = [] # a list of lists of words
            bigram = Phrases()
            episode_corpus = [] # used to save corpus of episodes a list of sentences
            with open(self.episodes_desc, "r") as f:
                for line in f:
                    # remove common punctuations and transform all words to their lower cases.
                    sentence =  [lemmatizer.lemmatize(word) for word in line.translate(translation).lower().split()]
                    line = " ".join(sentence)
                    episode_corpus.append(line)
                    # sentence = [word
                    #             for word in nltk.word_tokenize(line)
                    #             if word not in string.punctuation]
                    sentences.append(sentence)
                    bigram.add_vocab([sentence])
            return bigram, episode_corpus, sentences
        bigram, episode_corpus, sentences = preprocess()

        def get_ngram(bigram):
            vocab_dict = Counter()
            for key,value in bigram.vocab.items():
                words = key.decode("utf-8").split("_")
                if len(words) == 1:
                    if key.decode("utf-8") not in stopwords.words("english"):
                        vocab_dict[key.decode('utf-8')] = value    
                else:
                    if not any([word in stopwords.words('english') for word in words]):
                        vocab_dict[key.decode('utf-8').replace("_", " ")] = value
            vocab = list(vocab_dict.keys())
            return vocab, vocab_dict


        vocab, vocab_dict = get_ngram(bigram)
        
        # print all bi_words to get an idea of what are included.
        print("We have the following bi_word: ")
        # bi_words = []
        # for word in vocab:
        #     if len(word.split(" ")) == 2:
        #         bi_words.append(word)
        # print(bi_words)

        return bigram, episode_corpus,vocab,vocab_dict
    

    def get_tf_idf(self,vocab,corpus):
        vectorizer = CountVectorizer(ngram_range=(1, 2),vocabulary = self.vocab_tf_idf)
        X = vectorizer.fit_transform(corpus)
        transformer = TfidfTransformer(smooth_idf=True)
        tfidf = transformer.fit_transform(X)
        return tfidf

    def bigram_recommendation(self, user_request):
        lemmatizer = nltk.WordNetLemmatizer()
        translation = str.maketrans(string.punctuation,' '*len(string.punctuation))
        user_request_corpus = " ".join([lemmatizer.lemmatize(word) for word in user_request.translate(translation).lower().split()])
        #user_request_corpus = [user_request.translate(translation).lower()]
        corpus = self.episode_corpus + [user_request_corpus]
        tfidf = self.get_tf_idf(self.vocab_tf_idf, corpus)
        #print(tfidf.shape) # (N+1) * |V| N is the number of episodes and |V| is the size of the vocab in the bigram dict.
        #find cos similarities
        cos_similarities = cosine_similarity(X = tfidf)[-1]
        most_similar_index = cos_similarities.argsort()[-4:][::-1][1:]# except itself
        return cos_similarities, most_similar_index

    def doc_vec_recommendation(self,user_request):
        all_episode = self.episode_vec_weighted_df.values
        user_request_corpus = gensim.utils.simple_preprocess(user_request)

        # use doc vec to make recommendation
        user_weighted_vec = self.get_doc_weighted_vec(user_request_corpus).reshape(1, -1)
        cos_similarities = cosine_similarity(X=user_weighted_vec, Y=all_episode)[0]
        most_similar_index = cos_similarities.argsort()[-4:][::-1]
        return cos_similarities, most_similar_index

    def recommend_episode(self,user_request): # add parameter user_request 
        length_threshold = 5
        threshold_tf_idf = 0.15
        threshold_vec= 0.65
        #most_similar = list(set(most_similar_tf_idf).union(most_similar_tf_idf))
        if len(user_request.split()) < length_threshold:
            cos_similarities, most_similar_index = self.bigram_recommendation(user_request)
            threshold = threshold_tf_idf
        else:
            cos_similarities, most_similar_index = self.doc_vec_recommendation(user_request)
            threshold = threshold_vec

        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& User's request is:  " + user_request + " &&&&&&&&&&&&&&&&&&&&&&&&\n" )
        result = {}
        rank  = 1
        print('most_similary index are ', most_similar_index)
        for i in most_similar_index:
            if cos_similarities[i] > threshold:
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
   
    
   


