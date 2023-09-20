# 由於 continuumio/miniconda3:4.3.27 中的 Debian
# 版本太舊，因此改用 ubuntu 系統
FROM ubuntu

# 系統升級、安裝 python
RUN apt-get update && apt-get install python3.11 -y && apt-get install python3-pip -y

RUN mkdir /stats
COPY . /stats/
WORKDIR /stats/

# env
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Asia/Taipei

# install package
RUN pip3 install pipenv
RUN pipenv lock
RUN pipenv sync

# genenv
RUN VERSION=RELEASE python3 genenv.py
