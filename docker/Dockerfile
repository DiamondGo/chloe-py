# FROM debian:stable-slim
# 
# ARG CHLOE_DIR=/chloe
# 
# RUN apt-get update
# RUN apt-get install -y python3 python3-virtualenv python3-pip ffmpeg curl git
# 
# RUN git clone https://github.com/DiamondGo/chloe-py.git ${CHLOE_DIR}
# 
# WORKDIR ${CHLOE_DIR}
# 
# RUN cd ${CHLOE_DIR} && virtualenv --copies venv
# 
# RUN cd ${CHLOE_DIR} && . ./venv/bin/activate && pip install -r requirements.txt
# 
# ENTRYPOINT [ "/bin/bash", "-c", "source ./venv/bin/activate && python main.py" ]

FROM python:latest

ARG CHLOE_DIR=/chloe

RUN apt update
RUN apt install -y ffmpeg git virtualenv bash

RUN git clone https://github.com/DiamondGo/chloe-py.git ${CHLOE_DIR}

WORKDIR ${CHLOE_DIR}

RUN cd ${CHLOE_DIR} && virtualenv --copies venv

RUN cd ${CHLOE_DIR} && . ./venv/bin/activate && pip install -r requirements.txt

ENTRYPOINT [ "/bin/bash", "-c", "source ./venv/bin/activate && python main.py" ]

