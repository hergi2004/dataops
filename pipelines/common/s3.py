from __future__ import annotations
import boto3
from botocore.client import Config
from .config import get_settings

def s3_client():
    s = get_settings()
    # Path-style addressing to work smoothly with MinIO
    return boto3.client(
        "s3",
        endpoint_url=s.minio_endpoint,
        aws_access_key_id=s.minio_access_key,
        aws_secret_access_key=s.minio_secret_key,
        region_name=s.minio_region,
        config=Config(s3={"addressing_style": "path"}),
    )
