FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV CITADOR_TOKEN YOUR_TOKEN_HERE

RUN mkdir /src
COPY . /src
RUN pip install -r /src/requirements.txt
RUN chmod +x /src/*
WORKDIR /src

CMD ["/usr/local/bin/python","/src/bot.py"]
