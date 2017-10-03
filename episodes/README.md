# How to use it?

1. First run **gensim_models_question_answer python 3.ipynb** to generate vector representations for all words in the bodies and 
titles of all posts from stack exchange statistics session. The result will be saved in the folder word_vec with name 
**word2vector_model_question_answer_200_6_2.csv**. 200 is the size of the hidden layer, i.e. the dimension of the word vectors. 
6 is the window size and 2 is the min_count in the word2vec models.  

2. The size of the file **word2vector_model_question_answer_200_6_2.csv** is large, so I didn’t upload it to GitHub. 
In case one doesn’t want to run **gensim_models_question_answer python 3.ipynb**, **word2vector_model_question_answer_200_6_2.csv**  
is accessible at my google driver: https://drive.google.com/file/d/0Bz-4FukuZM1Kbm81UkF3RnRjY2c/view?usp=sharing
After downloading it, save the csv file in the folder word_vec.

3. Second run episodes_all.ipynb to get vector representations of all episodes. They will be saved in the folder 
**episode_vec**. Make sure that there are 179 episodes before 10/3/2017.

4. Then in terminal run **api_episode.py** 

5. At rest console, type in the request url “http://0.0.0.0:3500/episode/random_recommendation”. The method is get. 
It is expected to return a random episode. 

6. At rest console, type in the request url “http://0.0.0.0:3500/episode/recommendation”. The method is post. 
RAW_body is {“request”: “string of user’s request”}.  
For example, {“request”: “ I would like to listen to an episode on random forest and decision tree. ”}  
It will return a related episode.
