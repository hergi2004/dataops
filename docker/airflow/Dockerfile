FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt

# Make sure user-level pip binaries are on PATH
ENV PATH="/home/airflow/.local/bin:${PATH}"

USER root
COPY airflow_entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow
WORKDIR /opt/project
ENTRYPOINT ["/entrypoint.sh"]
