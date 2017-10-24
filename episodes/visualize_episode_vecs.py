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

import pandas as pd
import sys
import numpy as np
from sklearn.decomposition import PCA
from ggplot import *
import matplotlib.pyplot as plt
import matplotlib as mpl


# the goal of this document is to visualize/ cluster all of the 181 episodes in 2 dimensions to see whether the doc vectors are good enough.


file_name = "/Users/XiaofeiZheng/Desktop/10_23_17/episodes/text/episodes_json.txt"
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
	descToNum[desc] = str(episode_json[desc]['num']) 


path = "/Users/XiaofeiZheng/Desktop/10_23_17/episodes/episode_vec_bigram/episode_vec_weighted.csv"
doc_vecs = pd.read_csv(path, index_col = 0)


print(doc_vecs.shape)
print(doc_vecs.head(5))

#PCA for doc_vecs
pca = PCA(n_components=30)
feature = doc_vecs
pca_result = pca.fit_transform(feature.values)

doc_vecs['pca-one'] = pca_result[:,0]
doc_vecs['pca-two'] = pca_result[:,1] 
doc_vecs['pca-three'] = pca_result[:,2]
doc_vecs['Name'] = descToTitle.values()

print(doc_vecs.head())
print ('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))

#rndperm = np.random.permutation(df.shape[0])

c12_1 = ggplot(doc_vecs, aes(x='pca-one', y='pca-two', label = 'Name') ) \
        + geom_point(color = 'red', size = 5) \
        + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
        + ggtitle("First and Second Principal Components") \
        + scale_x_continuous(limits=(-20,5)) \
        + scale_y_continuous(limits=(-20,20))
 
print("the first figure is ")
print(c12_1)


# c12_2 = ggplot(doc_vecs, aes(x='pca-one', y='pca-two', label = 'Name') ) \
#         + geom_point(color = 'red', size = 5) \
#         + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
#         + ggtitle("First and Second Principal Components") \
#         + scale_x_continuous(limits=(-20,5)) \
#         + scale_y_continuous(limits=(0,20))

# print(c12_2)

# c12_3 = ggplot(doc_vecs, aes(x='pca-one', y='pca-two', label = 'Name') ) \
#         + geom_point(color = 'red', size = 5) \
#         + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
#         + ggtitle("First and Second Principal Components") \
#         + scale_x_continuous(limits=(5,30)) \
#         + scale_y_continuous(limits=(0,20))
 
# print(c12_3)





# #________________#

# c23_1 = ggplot(doc_vecs, aes(x='pca-one', y='pca-three', label = 'Name') ) \
#         + geom_point(color = 'blue', size = 5) \
#         + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
#         + ggtitle("First and Third Principal Components") \
#         + scale_x_continuous(limits=(0,20)) \
#         + scale_y_continuous(limits=(-20,0))
 
# print(c23_1)

# c23_2 = ggplot(doc_vecs, aes(x='pca-one', y='pca-three', label = 'Name') ) \
#         + geom_point(color = 'blue', size = 5) \
#         + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
#         + ggtitle("First and Third Principal Components") \
#         + scale_x_continuous(limits=(0,20)) \
#         + scale_y_continuous(limits=(0,20))
# print(c23_2)

# c23_3 = ggplot(doc_vecs, aes(x='pca-one', y='pca-three', label = 'Name') ) \
#         + geom_point(color = 'blue', size = 5) \
#         + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
#         + ggtitle("First and Third Principal Components") \
#         + scale_x_continuous(limits=(-20,0)) \
#         + scale_y_continuous(limits=(-20,0))
# print(c23_3)

c23_4 = ggplot(doc_vecs, aes(x='pca-one', y='pca-three', label = 'Name') ) \
        + geom_point(color = 'blue', size = 5) \
        + geom_text(aes(label='Name', size = 4, alpha = 0.8),hjust=0, vjust=0) \
        + ggtitle("First and Third Principal Components") \
        + scale_x_continuous(limits=(-20,0)) \
        + scale_y_continuous(limits=(0,20))

print(c23_4)




