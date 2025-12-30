from __future__ import annotations

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE_DIR = os.path.join(ROOT, "data", "stage_parquet")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
WAREHOUSE_DB = os.getenv("WAREHOUSE_DB", "warehouse")
WAREHOUSE_USER = os.getenv("WAREHOUSE_USER", "warehouse")
WAREHOUSE_PASSWORD = os.getenv("WAREHOUSE_PASSWORD", "warehouse")
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")

JDBC_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{WAREHOUSE_DB}"
JDBC_PROPS = {
    "user": WAREHOUSE_USER,
    "password": WAREHOUSE_PASSWORD,
    "driver": "org.postgresql.Driver",
}

def spark() -> SparkSession:
    # Pull postgres driver from Maven (works when container has outbound internet).
    # If your environment blocks this, bake the driver jar into the image.
    return (
        SparkSession.builder
        .appName("de-local-batch-load")
        .master(SPARK_MASTER)
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
        .getOrCreate()
    )

def main():
    s = spark()

    customers = s.read.parquet(os.path.join(STAGE_DIR, "customers.parquet"))
    orders = s.read.parquet(os.path.join(STAGE_DIR, "orders.parquet"))
    items = s.read.parquet(os.path.join(STAGE_DIR, "order_items.parquet"))

    # Minimal type hygiene
    customers = customers.withColumn("created_at", to_timestamp(col("created_at")))
    orders = orders.withColumn("order_ts", to_timestamp(col("order_ts")))

    # Write into Postgres raw schema
    customers.write.mode("overwrite").jdbc(JDBC_URL, "raw.customers", properties=JDBC_PROPS)
    orders.write.mode("overwrite").jdbc(JDBC_URL, "raw.orders", properties=JDBC_PROPS)
    items.write.mode("overwrite").jdbc(JDBC_URL, "raw.order_items", properties=JDBC_PROPS)

    print("✅ Loaded raw tables into Postgres schema raw.*")
    s.stop()

if __name__ == "__main__":
    main()
