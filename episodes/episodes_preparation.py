
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
    def __init__(self):
        self.crawl_episode_info()
        self.get_word_vec()
        print("crawling episodes is done.")
        vocab_dic = self.vocab_dic()
        corpus = self.get_episode_corpus()
        self.vectorizer = TfidfVectorizer(min_df=1,vocabulary = vocab_dic)
        self.X = self.vectorizer.fit_transform(corpus)

        with open ("../config/config.json", "r") as myfile:
            data = json.load(myfile)
            size = data['model_paras']['size']
            min_count = data['model_paras']['min_count']
            window = data['model_paras']['window']
            self.name = str(size) + "_" + str(window) + "_"+ str(min_count) 
            
    def get_word_vec(self):
        fname = './word_vec/word2vector_model_question_answer_' + self.name + '.csv'
        word_vecs_df = pd.read_csv(fname,index_col=0)
        vocab = word_vecs_df.index
        print("the size of the vocab is ",len(vocab))
        self.vocab = vocab
        self.word_vecs_df = word_vecs_df

    def vocab_dic(self):

        fname = './vocab_dict/vocab_dict_question_answer_'+ self.name +'.csv'
        with open(fname, 'r') as csv_file:
            reader = csv.reader(csv_file)
            vocab_dic = dict(reader)
        for k, value in vocab_dic.items():
            vocab_dic[k] = int(value)
        return vocab_dic

    def crawl_episode_info(self):
        fname = 'feed.xml'
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
        if not os.path.exists('./text/'):
            os.makedirs('./text/')
        with open('./text/episodes_json.txt', 'w') as outfile:  
            json.dump(result, outfile)
        with open('./text/episode_descs_titles.txt', 'w') as thefile:  
            for i in range(len(descriptions)):
                desc = descriptions[i]
                title = descToTitle[desc]
                desc = desc.encode('utf-8').strip()
                desc = str(desc).replace('\n', "") 
                title = title.replace('[MINI]', "")
                title = title.encode('utf-8').strip()
                title = "*"+ str(i)+str(title).replace('\n', "") 
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
        fname = './text/episode_descs_titles.txt'
        self.episode_desc_title_corpus = list(self.read_corpus(fname, tokens_only= True))
        corpus = []
        for desc in self.episode_desc_title_corpus:
            corpus.append(" ".join(desc))

        fname = './text/episode_corpus.txt'
        with open(fname, 'w') as f:
            for c in corpus:
                f.write("%s\n" % c)
        return corpus

    def get_doc_weighted_vec(self, i, doc_corpus, tf_idf, weighted = True): # ith documents. doc_corpus a list of words
        df = self.word_vecs_df
        vocab = self.vocab
        related_rows = df.loc[sorted(list(set(doc_corpus).intersection(set(vocab)))), :] 
        if weighted:
            weights = []
            ind = sorted(tf_idf[i,:].nonzero()[1])
            if sum([self.vectorizer.vocabulary_[related_rows.index[j]] != ind[j] for j in range(len(ind))]) != 0:
                print("words position don't match")
                return 
            for j in ind:
                weights.append(tf_idf[i,j])
            weights = np.array(weights)/sum(weights)
        else:
            weights = [1/related_rows.shape[0]] * related_rows.shape[0]
        if related_rows.shape[0] != len(weights):
            print(i)
            print(related_rows.shape[0])
            print(len(weights))
        result = related_rows.T * weights
        return result.sum(axis = 1)
    def get_episode_weighted_vec(self):
        episode_vec_weighted = []
        total = len(self.descriptions)
        for i in range(total):
            doc_corpus = self.episode_desc_title_corpus[i]
            episode_vec_weighted.append(self.get_doc_weighted_vec(i,doc_corpus, self.X))

        if not os.path.exists('./episode_vec/'):
            os.makedirs('./episode_vec/')

        episode_vec_weighted_df = pd.DataFrame(episode_vec_weighted)
        episode_vec_weighted_df.to_csv("./episode_vec/episode_vec_weighted.csv")
    # def run(self):
    #     ins = episodes_preparation.episode_prepare()

def run(updata):
    if updata:
        ins = episode_prepare()
        ins.get_episode_weighted_vec() 
    
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()


   


