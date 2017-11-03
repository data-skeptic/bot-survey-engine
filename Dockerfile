FROM mhart/alpine-node:latest

RUN apt-get update

# TODO: Install python3
# TODO: Install necessary libraries with pip3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# TODO: Copy source files into the image
# TODO: Run the code

COPY config/config.json /usr/src/app/config

CMD ["python3", "api.py"]
