FROM python:3.7-buster

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY ./run.py /bin/load-aws-secrets

ENTRYPOINT ["/bin/load-aws-secrets"]
