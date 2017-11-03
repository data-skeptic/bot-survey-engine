FROM mhart/alpine-node:latest

RUN apt-get update

# TODO: Install python3
sudo apt-get install python3.6

# TODO: Install necessary libraries with pip3
pip install -r requirements.txt

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# TODO: Copy source files into the image
RUN cp -r config episodes listener_reminder survey /usr/src/app
RUN cp api.py test_episode_recommendation.py /usr/src/app

# TODO: Run the code
CMD ["python3", "api.py"]

