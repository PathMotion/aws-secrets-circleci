FROM python:3.6-stretch

RUN pip install boto3 jq

ADD ./run.py /bin/load-aws-secrets

RUN chmod +x /bin/load-aws-secrets

ENTRYPOINT ["/bin/load-aws-secrets"]