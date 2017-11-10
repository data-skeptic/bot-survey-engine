FROM ubuntu:latest

RUN apt-get update

# TODO: Install python3
RUN apt-get install -y python3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# TODO: Install necessary libraries with pip3
RUN apt-get install -y python3-pip 
COPY requirements.txt /usr/src/app
RUN pip3 install -r requirements.txt

# TODO: Copy source files into the image

COPY ./api.py /usr/src/app
COPY ./test_episode_recommendation.py /usr/src/app

COPY config /usr/src/app/config
COPY episodes /usr/src/app/episodes
COPY listener_reminder /usr/src/app/listener_reminder
COPY survey /usr/src/app/survey


# TODO: Run the code
# CMD ["python3", "api.py"]

# docker build -t bot .
# docker run -i -t -p 3500:3500 bot 

# in docker, python3 api.py
