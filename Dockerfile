FROM ubuntu:latest

RUN apt-get update

# TODO: Install python3
RUN apt-get install -y python3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# TODO: Install necessary libraries with pip3
RUN apt-get install -y python3-pip 
COPY requirements.txt /usr/src/app
#RUN pip3 install -r requirements.txt

# TODO: Copy source files into the image

COPY ./api.py /usr/src/app
COPY ./test_episode_recommendation.py /usr/src/app

COPY config /usr/src/app
COPY episodes /usr/src/app
COPY listener_reminder /usr/src/app
COPY survey /usr/src/app


# TODO: Run the code
# CMD ["python3", "api.py"]

# docker build -t bot .
# docker build -t dataskeptic.com .
# docker run -i -t -d -p 443:443 -p 80:80 -p 3000:3000 -p 9001:9001 dataskeptic.com
