FROM pytorch/pytorch:1.9.1-cuda11.1-cudnn8-runtime

USER root
WORKDIR /workspace/
COPY requirements.txt ./
RUN pip install -r requirements.txt
