from __future__ import annotations

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
WAREHOUSE_DB = os.getenv("WAREHOUSE_DB", "warehouse")
WAREHOUSE_USER = os.getenv("WAREHOUSE_USER", "warehouse")
WAREHOUSE_PASSWORD = os.getenv("WAREHOUSE_PASSWORD", "warehouse")
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "order_events")

JDBC_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{WAREHOUSE_DB}"
JDBC_PROPS = {
    "user": WAREHOUSE_USER,
    "password": WAREHOUSE_PASSWORD,
    "driver": "org.postgresql.Driver",
}

schema = StructType([
    StructField("event_ts", StringType(), False),
    StructField("order_id", StringType(), False),
    StructField("customer_id", StringType(), True),
    StructField("event_type", StringType(), False),
    StructField("amount", DoubleType(), True),
    StructField("source", StringType(), True),
])

def main():
    spark = (
        SparkSession.builder
        .appName("de-local-stream-consumer")
        .master(SPARK_MASTER)
        .config("spark.jars.packages",
                ",".join([
                    "org.postgresql:postgresql:42.7.3",
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3"
                ]))
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = (
        df.selectExpr("CAST(value AS STRING) AS json_str")
        .select(from_json(col("json_str"), schema).alias("v"))
        .select("v.*")
    )

    # For simplicity: micro-batch write to Postgres
    def write_batch(batch_df, batch_id: int):
        (batch_df
            .withColumnRenamed("event_ts", "event_ts")
            .write
            .mode("append")
            .jdbc(JDBC_URL, "raw.order_events", properties=JDBC_PROPS)
        )
        print(f"Wrote batch {batch_id} rows={batch_df.count()}")

    query = (
        parsed.writeStream
        .foreachBatch(write_batch)
        .outputMode("append")
        .option("checkpointLocation", "/tmp/spark_checkpoints/order_events")
        .start()
    )

    print("✅ Streaming consumer running. Ctrl+C to stop.")
    query.awaitTermination()

if __name__ == "__main__":
    main()
