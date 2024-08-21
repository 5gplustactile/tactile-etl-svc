FROM apache/airflow:2.9.2


COPY r.txt /opt/airflow/
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r  /opt/airflow/r.txt
