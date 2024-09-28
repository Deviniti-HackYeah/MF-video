FROM python:3.12

WORKDIR /mf-video
COPY requirements.txt requirements.txt

RUN apt-get update
RUN apt-get -y install apt-utils
RUN apt-get update && \
    apt-get -y install wget curl unzip libpq-dev gcc iputils-ping g++ git \
    gnupg ffmpeg
RUN apt-get clean

RUN pip install --upgrade pip

RUN pip install -r requirements.txt 
COPY .flaskenv .flaskenv
COPY app.py app.py
COPY config.py config.py
COPY app app
COPY migrations migrations

ENV PYTHONUNBUFFERED=1
EXPOSE 8013

CMD ["sh","-c", "flask db upgrade && python -m flask run --host=0.0.0.0 --port=8013"]
