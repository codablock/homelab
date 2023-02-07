FROM python:3.10-slim-buster

RUN apt update && apt install -y procps

RUN mkdir /shelly-mqtt
WORKDIR /shelly-mqtt

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD *.py .

CMD python main.py
