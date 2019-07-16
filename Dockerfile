FROM python:3.6-stretch

RUN pip install boto3 jq

ADD ./run.py /app/run.py
ADD ./entrypoint.sh /app/entrypoint.sh

RUN mkdir -p ~/.aws/

ENTRYPOINT /app/entrypoint.sh