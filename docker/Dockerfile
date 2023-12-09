FROM python:3.11-alpine

ARG CHLOE_DIR=/chloe

WORKDIR ${CHLOE_DIR}

RUN apk update
RUN apk add --no-cache git ffmpeg wget

RUN git clone https://github.com/DiamondGo/chloe-py.git ${CHLOE_DIR}

RUN pip install -r requirements.txt --break-system-packages

ENTRYPOINT [ "python", "/chloe/main.py" ]
