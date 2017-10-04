# How to use it?

1. First download **word2vector_model_question_answer_200_6_2.csv** from  my google driver: https://drive.google.com/file/d/0Bz-4FukuZM1Kbm81UkF3RnRjY2c/view?usp=sharing

After downloading it, save the csv file in the folder bot-survey-engine/episodes/word_vec/.

What is  **word2vector_model_question_answer_200_6_2.csv**?  It stores vector representations for all words in the bodies and titles of all posts from stack exchange statistics session. One can also run **gensim_models_question_answer python 3.ipynb** to generate it. 200 is the size of the hidden layer, i.e. the dimension of the word vectors.  6 is the window size and 2 is the min_count in the word2vec models.  

2. **vocab_dict_question_answer_200_6_2** in the folder **vocab_dic** is also generated from **gensim_models_question_answer       python 3.ipynb**. Since its size is small, it has already been uploaded at github. 

3. Add **config/config.json** in the **bot-survey-engine** folder.

4. Run **api_episode.py** directly in one of the following cases:
  - This is the first time you run it. 
  - This is not the first time you run it but you want to get the latest episodes from Data Skeptic.
  
  Otherwise, you have to do the following thing:
  - Open api_episodes.py
  - update_episode = True   change it to update_episode = False
  
  When `python api_episode.py` is executed, two folders **text** and **episode_vec** will be generated and corresponding files       will be saved inside.

5. At rest console, type in the request url “http://0.0.0.0:3500/episode/random_recommendation”. The method is get. 
It is expected to return a random episode. 

6. At rest console, type in the request url “http://0.0.0.0:3500/episode/recommendation”. The method is post. 
RAW_body is {“request”: “string of user’s request”}.  
For example, {“request”: “ I would like to listen to an episode on random forest and decision tree. ”} Make sure that the quote signs are in the right form. 

It will return a related episode. 
