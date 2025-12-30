from __future__ import annotations
import sqlalchemy as sa
from .config import get_settings

def engine():
    s = get_settings()
    url = sa.URL.create(
        "postgresql+psycopg2",
        username=s.warehouse_user,
        password=s.warehouse_password,
        host=s.postgres_host,
        port=s.postgres_port,
        database=s.warehouse_db,
    )
    return sa.create_engine(url, pool_pre_ping=True)

def exec_sql(sql: str) -> None:
    eng = engine()
    with eng.begin() as cxn:
        cxn.exec_driver_sql(sql)
