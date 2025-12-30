from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    postgres_host: str
    postgres_port: int
    warehouse_db: str
    warehouse_user: str
    warehouse_password: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    minio_region: str

    kafka_bootstrap: str
    kafka_topic: str

    spark_master: str

def get_settings() -> Settings:
    return Settings(
        postgres_host=os.getenv("POSTGRES_HOST", "postgres"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        warehouse_db=os.getenv("WAREHOUSE_DB", "warehouse"),
        warehouse_user=os.getenv("WAREHOUSE_USER", "warehouse"),
        warehouse_password=os.getenv("WAREHOUSE_PASSWORD", "warehouse"),
        minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        minio_bucket=os.getenv("MINIO_BUCKET", "lake"),
        minio_region=os.getenv("MINIO_REGION", "us-east-1"),
        kafka_bootstrap=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092"),
        kafka_topic=os.getenv("KAFKA_TOPIC", "order_events"),
        spark_master=os.getenv("SPARK_MASTER", "local[*]"),
    )
