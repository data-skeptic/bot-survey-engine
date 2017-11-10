import pandas as pd
import requests
import xmltodict
from bs4 import BeautifulSoup
import pickle
import json
import os
import gensim
import csv
import time
import smart_open
from nltk.corpus import stopwords
import boto3
import warnings
warnings.filterwarnings('ignore')

class episode_prepare():
    def __init__(self):
        #step1 
        start1 = time.time()
        self.SO_bigram = self.bigram()
        print("EP: the size of the vocab from SO including bigram is ",len(self.SO_bigram.vocab.keys()))   
        end1 = time.time()
        print("EP downloading SO_bigram time is ", end1-start1)
        #step2
        self.crawl_episode_info()
        print("EP: crawling episodes is done.")
        #step3
        #self.vocab_dic, self.word_vecs_df = self.get_word_vec()
        start2 = time.time()
        self.vocab = self.get_word_vec()
        end2 = time.time()
        print("EP: get word vec time ", end2 -start2)

        start3 = time.time()
        episodes_words_filtered = self.get_episode_corpus_bigram()
        end3 = time.time()
        print("EP: How long does it take to preprocess episodes ", end3 - start3)

        mdir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(mdir+'/episodes_preprocess/'):
            os.makedirs(mdir+'/episodes_preprocess/')
        fname = '/episodes_preprocess/episodes_words_filtered.pickle'
        with open(mdir+fname, 'wb') as f:
            pickle.dump(episodes_words_filtered, f)

        episdoes_words_filtered_title = self.get_episode_title_corpus_bigram()
        fname = '/episodes_preprocess/episodes_words_filtered_title.pickle'
        with open(mdir+fname, 'wb') as f:
            pickle.dump(episdoes_words_filtered_title, f)
        
    def get_word_vec(self):
        # fname = "/word_vec_bigram/all_posts_word_vec.csv"
        # mdir = os.path.dirname(os.path.abspath(__file__))
        # word_vecs_df = pd.read_csv(mdir+fname,index_col=0)
        # vocab = set(word_vecs_df.index)
        #vocab_dic = {vocab[i]:i for i in range(word_vecs_df.shape[0])}
        #return vocab_dic, word_vecs_df
        mdir = os.path.dirname(os.path.abspath(__file__))
        with open(mdir + '/vocab.plk', 'rb') as f:
            vocab = pickle.load(f)
        return vocab

    def bigram(self):
        mdir = os.path.dirname(os.path.abspath(__file__))
        fname = "/SO_bigram/SO_bigram.pkl"
        with open(mdir+fname,'rb') as f:
            bigram = pickle.load(f)
        return bigram

    def crawl_episode_info(self):
        mdir =os.path.dirname(os.path.abspath(__file__))
        fname = mdir+'/feed.xml'
        url = 'http://dataskeptic.com/feed.rss'
        if not(os.path.isfile(fname)):
            print('EP:fetching')
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
            if len(desc) >= 5:
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

        with open(mdir+'/text/episode_titles.txt','w') as thefile:
            for i in range(len(descriptions)):
                desc = descriptions[i]
                title = descToTitle[desc]
                title = title.replace('[MINI]', "")
                title = title.encode('utf-8').strip()
                title = str(title).replace('\n', "") 
                thefile.write("%s\n" % str(title))

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

    def get_episode_corpus_bigram(self):
        mdir = os.path.dirname(os.path.abspath(__file__))
        fname = mdir+'/text/episode_descs_titles.txt'
        sentences = []
        #bigram = Phrases(min_count=5)
        with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
            for i, line in enumerate(f):
                sentence = gensim.utils.simple_preprocess(line)
                sentences.append(sentence)
        episodes_words_filtered = []
        for i in range(len(sentences)):
            temp = self.SO_bigram[sentences[i]] # temp is a list of words(unigram and bigram)
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
            episodes_words_filtered.append(list(set(result).intersection(self.vocab)))            
        return episodes_words_filtered # a list of lists of words
    
    def get_episode_title_corpus_bigram(self):
        mdir = os.path.dirname(os.path.abspath(__file__))
        fname = mdir+'/text/episode_descs_titles.txt'
        fname = mdir+"/text/episode_titles.txt"
        sentences = []
        with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
            for i, line in enumerate(f):
                sentence = gensim.utils.simple_preprocess(line)
                sentences.append(sentence)
        episodes_words_filtered_title = []
        for i in range(len(sentences)):
            temp = self.SO_bigram[sentences[i]] # temp is a list of words(unigram and bigram)
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
            episodes_words_filtered_title.append(list(set(result).intersection(self.vocab)))    
        return episodes_words_filtered_title

def run(update):
    if update:
        ins = episode_prepare()
    
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()


   


