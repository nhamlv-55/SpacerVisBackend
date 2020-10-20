FROM buildpack-deps:bionic-scm

RUN apt-get update && \
    apt-get install -y python3.6 && \
    apt-get install -y python3-pip && \
    pip3 install boto3 && \
    echo "import boto3" >> test.py && \
    python3 test.py && \
    echo success
