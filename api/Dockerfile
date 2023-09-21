FROM ubuntu

RUN apt-get update && apt-get install python3.11 -y && apt-get install python3-pip -y

RUN mkdir /P_League
COPY . /P_League/
WORKDIR /P_League/

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip3 install pipenv
RUN pipenv sync

RUN VERSION=RELEASE python3 genenv.py

CMD ["pipenv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8888"]