from __future__ import annotations

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="de_end_to_end",
    description="Local end-to-end DE pipeline (generate -> pandas -> spark -> dbt)",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["local", "lab"],
) as dag:
    generate = BashOperator(
        task_id="generate_data",
        bash_command="cd /opt/project && python pipelines/generate_data.py",
    )

    pandas_etl = BashOperator(
        task_id="pandas_etl_to_parquet_and_minio",
        bash_command="cd /opt/project && python pipelines/etl_pandas.py",
    )

    spark_load = BashOperator(
        task_id="spark_batch_load_to_postgres",
        bash_command="cd /opt/project && python pipelines/spark_batch_load.py",
    )

    dbt_build = BashOperator(
        task_id="dbt_build_marts",
        bash_command="cd /opt/project && dbt build --project-dir dbt --profiles-dir dbt",
    )

    generate >> pandas_etl >> spark_load >> dbt_build
