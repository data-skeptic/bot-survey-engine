import pandas as pd
import numpy as np
import json
import pickle
import os
import gensim
import csv
import time
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer
import episodes_preparation as ep
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
import sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from itertools import repeat
from multiprocessing import Pool

import logging
logname = "roam-crawl"
logger = logging.getLogger(logname)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.DEBUG)

hdlr = logging.FileHandler('/var/tmp/' + logname + '.log')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

stdout = logging.StreamHandler()
stdout.setFormatter(formatter)
logger.addHandler(stdout)


class episode():
    def __init__(self, update_episode, username, address,password,databasename):
        #print('enter episode Initialization function')
        engine_internal = sqlalchemy.create_engine("mysql://%s:%s@%s/%s" % (username, password, address,databasename),pool_size=3, pool_recycle=3600)
        self.internal = engine_internal
        #test
        try:
            self.internal.execute("SHOW DATABASES;")
            #print('The connection is successful in episode recommenation.')
        except:
            #print('The connection fails in episode recommendation.')
            raise
        start1 = time.time()
        ep.run(update_episode) # episode preparation.
        end1 = time.time()
        #print("update episode and prepared time is ", end1 - start1)
        start2 = time.time()
        # get episodes information
        mdir = os.path.dirname(os.path.abspath(__file__))
        self.episodes_json_fname = mdir+'/text/episodes_json.txt'
        with open(self.episodes_json_fname) as data_file:    
            episode_json = json.load(data_file)
        #print('The total number of episodes is ',len(episode_json.keys()))
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
        end2 = time.time()
        #print('get episodes info time is ', end2 - start2)
        start3 = time.time()
        #get word_vectors trained from SO
        self.word_vec_file = mdir + "/word_vec_bigram/all_posts_word_vec.csv"
        self.word_vectors = pd.read_csv(self.word_vec_file, index_col=0)
        self.word_vectors = self.word_vectors.drop(self.word_vectors.index[122692])
        print("------------------------------------------------------------------------------")
        logger.debug("*** self_word_vectors shape is ")
        print(self.word_vectors.shape)
        print("------------------------------------------------------------------------------")
        logger.debug("*** the 122692 row of self_word_vectors is ")
        print(self.word_vectors.iloc[122692, 0:10])

        #get vocabulary dictionary from SO
        vocab = list(self.word_vectors.index)
        print("----------------------------------------------------")
        logger.debug("*** the word with index  122692 in the vocab is: ")
        print(vocab[122692])
        #self.vocab_dic = dict(zip(vocab, range(len(vocab))))
        self.vocab_dic = {vocab[i]:i for i in range(self.word_vectors.shape[0])}

        

        #get Phrase object SO_bigram trained from SO
        end3 = time.time()
        #print('time of getting word vectors and vocab_dict is', end3 - start3)
        fname = mdir+'/SO_bigram/SO_bigram.pkl'
        with open(fname, 'rb') as f:
            self.bigram = pickle.load(f)
            #print("test bigram....", b'random_walk' in self.bigram.vocab.keys())
            print("Recommendation: size of bigram.vocab is ",len(self.bigram.vocab.keys()))
        
        start4 = time.time()
        fname = mdir + "/episodes_preprocess/episodes_words_filtered.pickle"
        with open(fname, 'rb') as f:
            self.episodes_words_filtered = pickle.load(f)
        self.episodes_corpus = []
        for item in self.episodes_words_filtered:
            self.episodes_corpus.append(" ".join(item))
        print('self.episodes_corpus ', self.episodes_corpus[0:5])
        fname = mdir + "/episodes_preprocess/episodes_words_filtered_title.pickle"
        with open(fname, 'rb') as f:
            self.episodes_words_filtered_title = pickle.load(f)
        self.episodes_corpus_title = []
        for item in self.episodes_words_filtered_title:
            self.episodes_corpus_title.append(" ".join(item))
        print("Recommendation: the time it takes to download the episodes pickles is ", time.time() - start4)
        print("Recommendation: Initialization is done.")
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
            result = list(set(user_corpus).intersection(set(self.vocab_dic.keys())))

        #print("after preprocess, the result of user_request is ", result)
        print("------------------------------------------------------------------------------")
        logger.debug('*** after preprocessing, user_request becomes ${0}'.format(result))
        print( result)
        return result, len(set(user_corpus)) # a list of words with bigram, without stopwords and remove words not in vocabulary.

    def get_user_tf_idf(self, user_words):
        vectorizer = TfidfVectorizer(min_df=1,vocabulary = self.vocab_dic)
        print("vectorizer is ", vectorizer)
        print("--------------------------------------------------------------------------------------------------------")
        logger.debug('*** the word with index 122692 is: ' )
        for word, index in self.vocab_dic.items():
            if index == 122692:
                print(word)       
        print('len of self.vocab_dic is ', len(self.vocab_dic))
        print("------------------------------------------------------------------------------")
        logger.debug("self.episodes_corpus + [" ".join(user_words)] is ")
        test_corpus = self.episodes_corpus + [" ".join(user_words)]
        for i in range(len(test_corpus)):
            print(i, ":" ,test_corpus[i][0:3])
        
        all_tf_idf = vectorizer.fit_transform(self.episodes_corpus + [" ".join(user_words)])
        vocab_test = vectorizer.vocabulary_
        
        print('vocab_test length is ', len(vocab_test))
        print('after fitting transform, the index of the word nan is  ', vocab_test.get('aa_'), vocab_test.get('NaN'), vocab_test.get('nan'))
        print('after fitting transformation, the 122692 word is  ', list(vocab_test.keys())[122692])
        print("------------------------------------------------------------------------------")
        logger.debug("*** after fitting transform, shape of all_tf_idf is ")
        print( all_tf_idf.shape)
        user_tf_idf = all_tf_idf[-1,:]
        user_tf_idf_dict = {word:user_tf_idf[0,self.vocab_dic[word]] for word in user_words}
        user_tf_idf_df = pd.DataFrame([user_tf_idf_dict], columns = user_tf_idf_dict.keys()).T
        user_tf_idf_df.columns = ['tf_idf']
        user_tf_idf_df /=user_tf_idf_df.sum(axis = 0)
        user_tf_idf_df.sort_index(inplace=True)
        return user_tf_idf_df

    def get_score(self, i, user_words,user_tf_idf_df): # the ith episode
        episode_words = self.episodes_words_filtered[i]
        X = self.word_vectors.loc[episode_words,:]
        Y = self.word_vectors.loc[user_words,:]
        if X.shape[0] > 0 and Y.shape[0] > 0:
            cos_similarities = cosine_similarity(X = X.values, Y = Y.values)
            cos_similarities_df = pd.DataFrame(cos_similarities, index = episode_words, columns = user_words) 
            max_cos_similarities = cos_similarities_df.max(axis = 0)
            max_cos_similarities.sort_index(inplace=True)
            score = np.dot(max_cos_similarities.values, user_tf_idf_df.values)[0]
            # return score, cos_similarities_df
            result = {}
            result[i] = score
        else:
            score = 0
        return score

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
            score = max_cos_similarities.values.mean()
        else:
            score = 0
        # result = {}
        # result[i] = score
        return score
   
    def recommend_episode(self, user_request):
        by_title = True
        score_threshold_not_by_title  = 0.70
        score_threshold_by_title  = 0.30
        start1 = time.time()
        user_words,total = self.preprocess(user_request)
        end1 = time.time()
        #print("user request preprocess takes ", end1 - start1)
        ratio = len(user_words)/total
        start2 = time.time()
        user_tf_idf_df = self.get_user_tf_idf(user_words)
        print("------------------------------------------------------------------------------")
        logger.debug("user_tf_idf_df is obtained.")
        end2 = time.time()
        #print("to get tf_idf of user request ", end2 - start2)
        start3 = time.time()
        scores = np.array([self.get_score(i, user_words,user_tf_idf_df)*ratio for i in range(len(self.episodes_corpus))]) 
        
        # can not be pickled. If the target self.get_score is some function outside of the class, then it is fine.
        # num = len(self.episodes_corpus)
        # with Pool() as pool:
        #     scores_dict = pool.starmap(self.get_score,list(zip(range(num), repeat(user_words), repeat(user_tf_idf_df))))
        # print(len(scores_dict))

        end3 = time.time()
        #print("get all scores ", end3 - start3)
        max_score = scores.max()
        episode_indice = np.where(scores == max_score)[0]
        #print('episode_indice are', episode_indice)
        if len(episode_indice) == 1:
            by_title = False
            best_index = episode_indice
            most_similar_indice = np.array(scores).argsort()[-2:][::-1]
        else: # there are more than one episodes with the highest similarity. We need to use title to decide.
            start4 = time.time()
            by_title = True
            title_cos_similarities = {}
            for i in episode_indice:
                title_cos_similarities[i] = self.get_score_titles(i, user_words)
            most_similar_indice = heapq.nlargest(2, title_cos_similarities, key=title_cos_similarities.get)
            end4 = time.time()
            #print('if multi score ==1, then by titles, it takes ', end4 - start4)
        #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& User's request is:  " + user_request + " &&&&&&&&&&&&&&&&&&&&&&&&\n" )
        result = {}
        rank  = 1
        #print('most_similary index are ', most_similar_indice)
        if not by_title:
            for i in most_similar_indice:
                if scores[i] >= score_threshold_not_by_title:
                    j = len(self.descriptions) - i  
                    desc = [key for key, value in self.descToNum.items() if value == j][0]
                    result['rank_'+str(rank)] = ({'title':self.descToTitle[desc],'link':self.descToLink[desc],'desc':desc, 'body_cos_similarity': scores[i]})
                    rank += 1
        else:
            for i in most_similar_indice:
                if title_cos_similarities[i] >= score_threshold_by_title and scores[i] >= 0.5:
                    j = len(self.descriptions) - i  
                    desc = [key for key, value in self.descToNum.items() if value == j][0]
                    result['rank_'+str(rank)] = ({'title':self.descToTitle[desc],'link':self.descToLink[desc],'desc':desc, 'body_cos_similarity': scores[i], 'title_cos_similarity': title_cos_similarities[i]})
                    rank += 1  
        
        return result
    def save_recommendation_table(self, user_request, result):
        start1 = time.time()
        user_request = user_request.replace("'", "\\'").replace(";", "\\;").replace("&", "\\&").replace("%", "%%")
        #print('replacing special characters in user requests takes', time.time() - start1)
        #save request and result to database
        if  (not result) or len(result) == 0:
            try: 
                start2 = time.time()
                template = """
                            INSERT INTO record_recommendation
                            (user_request) VALUES('{user_request}')
                            """
                query = template.format(user_request = user_request)
                conn = self.internal.connect()
                conn.execute(query)
                conn.close()
                #print('When there is no recommendation, how long does it take to save the request? ',time.time() - start2)
                #print("Successful in inserting into record_recommendation table.")                                                   
            except: 
                print("recommendation: Error in inserting into record_recommendation table.")
                raise
        else:
            for key, value in result.items():
                start3 = time.time()
                recommended_episode_title = value["title"]
                recommended_episode_title = recommended_episode_title.replace("'", "\\'").replace(";", "\\;").replace("&", "\\&").replace("%", "%%")

                top = int(key.split("_")[1])
                body_cos_similarity = value.get('body_cos_similarity')
                title_cos_similarity = value.get("title_cos_similarity")
                #print("title_cos_similarity is ", title_cos_similarity)
                try: 
                    template = """
                                INSERT INTO record_recommendation
                                (user_request, recommended_episode_title, top, body_cos_similarity, title_cos_similarity) 
                                VALUES('{user_request}','{recommended_episode_title}','{top}','{body_cos_similarity}','{title_cos_similarity}')
                                """
                    query = template.format(user_request = user_request, recommended_episode_title = recommended_episode_title , top = top, body_cos_similarity = body_cos_similarity, title_cos_similarity = title_cos_similarity)
                    conn = self.internal.connect()
                    conn.execute(query)
                    conn.close()
                    #print("Successful in inserting into record_recommendation table.")  
                    #print("The time it spends on saving one piece of recommendation is ", time.time() - start3)                                                 
                except: 
                    print("recommendation: Error in inserting into record_recommendation table.")
                    raise
def my_get_score(i, user_words,user_tf_idf_df): # the ith episode
    episode_words = self.episodes_words_filtered[i]
    X = self.word_vectors.loc[episode_words,:]
    Y = self.word_vectors.loc[user_words,:]
    cos_similarities = cosine_similarity(X = X.values, Y = Y.values)
    cos_similarities_df = pd.DataFrame(cos_similarities, index = episode_words, columns = user_words) 
    max_cos_similarities = cos_similarities_df.max(axis = 0)
    max_cos_similarities.sort_index(inplace=True)
    score = np.dot(max_cos_similarities.values, user_tf_idf_df.values)[0]
    # return score, cos_similarities_df
    result = {}
    result[i] = score
    return result

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()

    
