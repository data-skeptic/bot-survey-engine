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
import episodes_preparation as ep
import warnings
warnings.filterwarnings('ignore')

########################## load files ######################
class episode():
	def __init__(self, update_episode, size, min_count, window, name):
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
		all_tf_idf = self.vectorizer.fit_transform(self.corpus + [" ".join(doc_corpus)])
		tf_idf = all_tf_idf[-1,:]
		df = self.word_vecs_df 
		return tf_idf.dot(df)[0]
     
	# def recommend_episode(self,user_request): # add parameter user_request 
	# 	all_episode = self.episode_vec_weighted_df.values
	# 	print("*****************************************************" + "\n")
	# 	user_request_corpus = gensim.utils.simple_preprocess(user_request)
	# 	length_threshold = 1000

	# 	# use tf-idf as features to make recommendation
	# 	all_tf_idf = self.vectorizer.fit_transform(self.corpus + [" ".join(user_request_corpus)])
	# 	tf_idf_user = all_tf_idf[-1,:]
	# 	cos_similarities_tf_idf = cosine_similarity(X=tf_idf_user,Y=all_tf_idf[0:-1,:])[0]
			

	# 	user_weighted_vec = self.get_doc_weighted_vec(user_request_corpus).reshape(1, -1)
	# 	cos_similarities_vec = cosine_similarity(X=user_weighted_vec, Y=all_episode)[0]
	# 	# lens = [len(user_request_corpus)]
	# 	# for c in self.corpus:
	# 	# 	lens.append(len(c))
	# 	# min_episode = min(lens)
	# 	# max_episode = max(lens) 
	# 	min_episode = 1
	# 	max_episode = 500
	# 	#print("range of episode length is ", min_episode, max_episode)
	# 	# ratio  = radio of tf_idf method
	# 	ratio =   np.exp(-50*(len(user_request_corpus) - min_episode)/(max_episode - min_episode))
	# 	print('ratio for tf_idf is ', ratio)
	# 	cos_similarities =ratio * cos_similarities_tf_idf * 5 + (1-ratio)*cos_similarities_vec 
	# 	most_similar = cos_similarities.argsort()[-4:][::-1]
	# 	threshold = 0.40
	# 	print("User's request is: " + user_request + "\n" )
	# 	result = {}
	# 	rank  = 1
	# 	print('most_similary index are ', most_similar)
	# 	for i in most_similar:
	# 		if cos_similarities[i] > threshold:# or (len(user_request_corpus) < length_threshold and cos_similarities[i] > 0):
	# 			print("--------------------The episode has cosine similarity is "+str(cos_similarities[i])+" with user's request-------------------------\n")
	# 			print( "\n")
	# 			j = len(self.descriptions) - i  # j = 111; i = 68
	# 			desc = [key for key, value in self.descToNum.items() if value == j][0]
	# 			print(str(self.descToTitle[desc]) + "\n")
	# 			print(str(self.descToLink[desc]) + "\n")
	# 			print(str(desc.encode('utf-8')) + "\n")
	# 			result['rank_'+str(rank)] = ({'title':self.descToTitle[desc],'link':self.descToLink[desc],'desc':desc})
	# 			rank += 1 
	# 	return result
	def recommend_episode(self,user_request): # add parameter user_request 
		all_episode = self.episode_vec_weighted_df.values
		print("*****************************************************" + "\n")
		user_request_corpus = gensim.utils.simple_preprocess(user_request)
		length_threshold = 1000

		# use tf-idf as features to make recommendation
		all_tf_idf = self.vectorizer.fit_transform(self.corpus + [" ".join(user_request_corpus)])
		tf_idf_user = all_tf_idf[-1,:]
		cos_similarities_tf_idf = cosine_similarity(X=tf_idf_user,Y=all_tf_idf[0:-1,:])[0]
			
		# use doc vec to make recommendation
		user_weighted_vec = self.get_doc_weighted_vec(user_request_corpus).reshape(1, -1)
		cos_similarities_vec = cosine_similarity(X=user_weighted_vec, Y=all_episode)[0]
		
		threshold_tf_idf = 0.16
		threshold_vec= 0.65

		most_similar_tf_idf = cos_similarities_tf_idf.argsort()[-4:][::-1]
		most_similar_vec = cos_similarities_vec.argsort()[-4:][::-1]
		#most_similar = list(set(most_similar_tf_idf).union(most_similar_tf_idf))
		if len(user_request_corpus) < 6:
			most_similar = most_similar_tf_idf
			cos_similarities = cos_similarities_tf_idf
			threshold = threshold_tf_idf
		else:
			most_similar = most_similar_vec
			cos_similarities = cos_similarities_vec
			threshold = threshold_vec

		print("User's request is: " + user_request + "\n" )
		result = {}
		rank  = 1
		print('most_similary index are ', most_similar)
		for i in most_similar:
			# the ranking is complex. Fix it later. 
			#if cos_similarities_tf_idf[i] > threshold_tf_idf or cos_similarities_vec[i] > threshold_vec:# or (len(user_request_corpus) < length_threshold and cos_similarities[i] > 0):
			#if cos_similarities_tf_idf[i] + cos_similarities_vec[i] > threshold or (cos_similarities_tf_idf[i] > threshold_tf_idf or cos_similarities_vec[i] > threshold_vec):
			if cos_similarities[i] > threshold:
				print("--------------------The episode has doc vector cosine similarity "+str(cos_similarities_vec[i])+ "-------------------\n")
				print("--------------------The episode has tf idf cosine similarity "+str(cos_similarities_tf_idf[i])+ "-------------------\n")
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
   
    
   


