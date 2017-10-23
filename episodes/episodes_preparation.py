
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
import json
import os
import gensim
import csv
import smart_open
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

import warnings
warnings.filterwarnings('ignore')

class episode_prepare():
    def __init__(self,size, min_count, window, name):
        self.name = name    
        self.crawl_episode_info()
        self.get_word_vec()
        #self.get_word_vec_200_glove()
        print("crawling episodes is done.")
        vocab_dic = self.vocab_dic()
        #vocab_dic = self.vocab_dic_200_glove()
        print('size of vocab in vocab_dic is ', len(vocab_dic))
        corpus = self.get_episode_corpus()
        self.vectorizer = TfidfVectorizer(min_df=1,vocabulary = vocab_dic)
        self.X = self.vectorizer.fit_transform(corpus)
    

    def get_word_vec(self):
        #fname = '/word_vec/word2vector_model_question_answer_' + self.name + '.csv'
        fname = "/word_vec_bigram/all_posts_word_vec.csv"
        mdir = os.path.dirname(os.path.abspath(__file__))
        word_vecs_df = pd.read_csv(mdir+fname,index_col=0)
        vocab = word_vecs_df.index
        print("the size of the vocab is ",len(vocab))
        self.vocab = vocab
        self.word_vecs_df = word_vecs_df

    # def get_word_vec_200_glove(self):
    #     path = "/Users/XiaofeiZheng/Downloads/word_vec_pickle_glove_200.pickle"
    #     with open(path, 'rb') as f:
    #         word_vecs_df = pickle.load(f)
    #     vocab = word_vecs_df.index
    #     print("the size of the vocab is ",len(vocab))
    #     self.vocab = vocab
    #     self.word_vecs_df = word_vecs_df

    def vocab_dic(self):
        #fname = '/vocab_dict/vocab_dict_question_answer_'+ self.name +'.csv'
        fname = '/vocab_dict_bigram/vocab_dict_question_answer.csv'
        mdir = os.path.dirname(os.path.abspath(__file__))
        with open(mdir+fname, 'r') as csv_file:
            reader = csv.reader(csv_file)
            vocab_dic = dict(reader)
        for k, value in vocab_dic.items():
            vocab_dic[k] = int(value)
        return vocab_dic
    def vocab_dic_200_glove(self):
        path = "/Users/XiaofeiZheng/Downloads/vocab_dic_glove_200.pickle"
        with open(path, 'rb') as f:
            vocab_dic = dict(pickle.load(f))
        return vocab_dic


    def crawl_episode_info(self):
        mdir =os.path.dirname(os.path.abspath(__file__))
        fname = mdir+'/feed.xml'
        url = 'http://dataskeptic.com/feed.rss'
        if not(os.path.isfile(fname)):
            print('fetching')
            r = requests.get(url)
            f = open(fname, 'wb')
            f.write(r.text.encode('utf-8'))
            f.close()
        with open(fname) as fd:
            xml = xmltodict.parse(fd.read())
        episodes = xml['rss']['channel']['item']
        descriptions = []
        descToTitle = {}
        descToLink = {}
        descToNum = {}
        l = len(episodes)
        for episode in episodes:
            enclosure = episode['enclosure']
            desc = episode['description']
            desc = desc.replace(u'\xa0', u' ')
            desc = desc.replace(u'\n', u' ')
            desc = desc.replace(u'\xc2', u' ')
            desc = BeautifulSoup(desc, "lxml").text
            descriptions.append(desc)
            descToTitle[desc] = episode['title']
            descToLink[desc] = episode['link']
            descToNum[desc] = l
            l = l - 1
        result = {}
        for desc in descriptions:
            info = {}
            info["link"] = descToLink[desc]
            info["title"] = descToTitle[desc]
            info["num"] = descToNum[desc]
            result[desc] = info
        mdir = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(mdir+'/text/'):
            os.makedirs(mdir+'/text/')
        with open(mdir+'/text/episodes_json.txt', 'w') as outfile:  
            json.dump(result, outfile)
        with open(mdir+'/text/episode_descs_titles.txt', 'w') as thefile:  
            for i in range(len(descriptions)):
                desc = descriptions[i]
                title = descToTitle[desc]
                desc = desc.encode('utf-8').strip()
                desc = str(desc).replace('\n', "") 
                title = title.replace('[MINI]', "")
                title = title.encode('utf-8').strip()
                title = str(title).replace('\n', "") 
                thefile.write("%s\n" % str(title+", "+desc)) 
        self.descriptions = descriptions


    def read_corpus(self,fname, tokens_only=False):
        with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
            for i, line in enumerate(f):
                if tokens_only:
                    yield gensim.utils.simple_preprocess(line)
                else:
                    yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

    def get_episode_corpus(self):
        mdir = os.path.dirname(os.path.abspath(__file__))
        fname = mdir+'/text/episode_descs_titles.txt'
        self.episode_desc_title_corpus = list(self.read_corpus(fname, tokens_only= True))
        corpus = []
        for desc in self.episode_desc_title_corpus:
            corpus.append(" ".join(desc))

        fname = mdir+'/text/episode_corpus.txt'
        with open(fname, 'w') as f:
            for c in corpus:
                f.write("%s\n" % c)
        return corpus
    
    def get_episode_weighted_vec(self):
        episode_weighted_vec = self.X.dot(self.word_vecs_df)
        print("episode_weighted_vec shape is ",episode_weighted_vec.shape) # should be N * 200 where N is the number of episodes

        mdir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(mdir+'/episode_vec/'):
            os.makedirs(mdir+'/episode_vec/')

        episode_vec_weighted_df = pd.DataFrame(episode_weighted_vec)
        episode_vec_weighted_df.to_csv(mdir+"/episode_vec/episode_vec_weighted.csv")
    
def run(update,size, min_count, window, name):
    if update:
        ins = episode_prepare(size, min_count, window, name)
        ins.get_episode_weighted_vec() 
    
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()


   


