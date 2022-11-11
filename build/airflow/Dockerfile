FROM library/ubuntu:latest

COPY . /airflow

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get install -y python3 python3-pip tzdata

RUN pip3 install -r /airflow/requirements.txt

ENV AIRFLOW_HOME=/airflow

RUN airflow db init
RUN airflow users create --role Admin -u edm_admin -f Admin -l admin -e admin@ulsu.ru --password edm_admin

RUN chmod +x /airflow/run.sh
ENTRYPOINT bash /airflow/run.sh
