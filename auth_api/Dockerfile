FROM python:3.11-slim-buster

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app/src

RUN apt-get update && apt-get install -y netcat

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x /opt/app/flask-entrypoint.sh

ENTRYPOINT ["/opt/app/flask-entrypoint.sh"]