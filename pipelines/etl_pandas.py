from __future__ import annotations

import os
import sys
from pathlib import Path
import pandas as pd

# Ensure project root is on sys.path so absolute imports work when run as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from pipelines.common.s3 import s3_client
from pipelines.common.config import get_settings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(ROOT, "data", "raw")
STAGE_DIR = os.path.join(ROOT, "data", "stage_parquet")
PARQUET_KWARGS = {
    "index": False,
    # Force ms precision so Spark can read the files (Spark barfs on ns timestamps)
    "coerce_timestamps": "ms",
    "allow_truncated_timestamps": True,
}

def ensure_dirs():
    os.makedirs(STAGE_DIR, exist_ok=True)

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    df["email"] = df["email"].str.lower().str.strip()
    df["state"] = df["state"].str.upper().str.strip()
    return df

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_ts"] = pd.to_datetime(df["order_ts"], utc=True, errors="coerce")
    df["status"] = df["status"].str.upper().str.strip()
    df["order_total"] = pd.to_numeric(df["order_total"], errors="coerce").fillna(0.0)
    return df

def main():
    ensure_dirs()
    s = get_settings()

    customers = clean_customers(pd.read_csv(os.path.join(RAW_DIR, "customers.csv")))
    orders = clean_orders(pd.read_csv(os.path.join(RAW_DIR, "orders.csv")))
    items = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))
    items["unit_price"] = pd.to_numeric(items["unit_price"], errors="coerce")
    items["quantity"] = pd.to_numeric(items["quantity"], errors="coerce")
    items["line_amount"] = pd.to_numeric(items["line_amount"], errors="coerce")

    # Write local Parquet (lake-like format)
    customers_p = os.path.join(STAGE_DIR, "customers.parquet")
    orders_p = os.path.join(STAGE_DIR, "orders.parquet")
    items_p = os.path.join(STAGE_DIR, "order_items.parquet")

    customers.to_parquet(customers_p, **PARQUET_KWARGS)
    orders.to_parquet(orders_p, **PARQUET_KWARGS)
    items.to_parquet(items_p, **PARQUET_KWARGS)

    # Upload to MinIO (S3-compatible)
    s3 = s3_client()

    # Create bucket if missing
    try:
        s3.head_bucket(Bucket=s.minio_bucket)
    except Exception:
        s3.create_bucket(Bucket=s.minio_bucket)

    def upload(local_path: str, key: str):
        s3.upload_file(local_path, s.minio_bucket, key)

    upload(customers_p, "stage/customers.parquet")
    upload(orders_p, "stage/orders.parquet")
    upload(items_p, "stage/order_items.parquet")

    print("✅ Parquet written locally to:", STAGE_DIR)
    print(f"✅ Uploaded to MinIO bucket '{s.minio_bucket}': s3://{s.minio_bucket}/stage/...")

if __name__ == "__main__":
    main()
