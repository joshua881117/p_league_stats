# 由於 continuumio/miniconda3:4.3.27 中的 Debian
# 版本太舊，因此改用 ubuntu 系統
FROM ubuntu

# 系統升級、安裝 python
RUN apt-get update && apt-get install python3.10 -y && apt-get install python3-pip -y

RUN mkdir /p_league_project
COPY . /p_league_project/
COPY ./airflow.cfg /p_league_project/dataflow/airflow.cfg
WORKDIR /p_league_project/

# env
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# install package
RUN pip3 install pipenv
RUN pipenv lock
RUN pipenv sync

# airflow 環境變數
ARG AIRFLOW_USER_HOME=/p_league_project/dataflow
ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

WORKDIR /p_league_project/
