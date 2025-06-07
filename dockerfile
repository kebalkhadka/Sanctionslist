FROM apache/airflow:2.10.5-python3.10
USER root
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get clean
USER airflow
RUN pip install --no-cache-dir mysqlclient pandas lxml