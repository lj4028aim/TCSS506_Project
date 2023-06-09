FROM python:3.9-slim-bullseye
ARG DEBIAN_FRONTEND=noninteractive
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /usr/local/bin/app/
WORKDIR /usr/local/bin/app/
CMD gunicorn -b 0.0.0.0:8000 app:app
#COPY app.py /usr/local/bin/app.py
#CMD app.py
