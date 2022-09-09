FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

USER root
RUN apt-get update
RUN yes | apt-get install --reinstall build-essential
RUN mkdir /storage
WORKDIR /workspace/
COPY requirements.txt ./
COPY storage/ /storage
RUN pip install -r requirements.txt
