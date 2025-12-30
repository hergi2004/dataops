from __future__ import annotations

from pipelines.common.s3 import s3_client
from pipelines.common.config import get_settings
from pipelines.common.db import exec_sql, engine

def main():
    s = get_settings()

    # MinIO bucket
    s3 = s3_client()
    try:
        s3.head_bucket(Bucket=s.minio_bucket)
        print(f"✅ MinIO bucket exists: {s.minio_bucket}")
    except Exception:
        s3.create_bucket(Bucket=s.minio_bucket)
        print(f"✅ Created MinIO bucket: {s.minio_bucket}")

    # Warehouse ping + schemas already created by init script, but verify
    exec_sql("CREATE SCHEMA IF NOT EXISTS raw; CREATE SCHEMA IF NOT EXISTS mart;")
    print("✅ Verified Postgres schemas raw, mart")

    # Quick sanity query
    with engine().connect() as cxn:
        v = cxn.exec_driver_sql("select version();").scalar_one()
        print("✅ Warehouse connected:", v)

if __name__ == "__main__":
    main()
