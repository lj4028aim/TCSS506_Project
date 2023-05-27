FROM python:3.9-slim-bullseye
ARG DEBIAN_FRONTEND=noninteractive
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV TZ=America/Los_Angeles
COPY flask-project /usr/local/bin/flask-project
#CMD /usr/local/bin/flask-project/app.py
