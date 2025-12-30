#!/usr/bin/env bash
set -euo pipefail

export AIRFLOW_HOME="${AIRFLOW_HOME:-/opt/airflow}"
export PROJECT_ROOT="${PROJECT_ROOT:-/opt/project}"

# Wait for Postgres
echo "Waiting for Postgres..."
python - <<'PY'
import os, time
import psycopg2
host=os.getenv("POSTGRES_HOST","postgres")
port=int(os.getenv("POSTGRES_PORT","5432"))
for i in range(60):
    try:
        psycopg2.connect(host=host, port=port, user="airflow", password="airflow", dbname="airflow").close()
        print("Postgres is ready.")
        break
    except Exception as e:
        time.sleep(2)
else:
    raise SystemExit("Postgres not reachable after 120s")
PY

# Init / migrate Airflow DB
airflow db migrate

# Create admin user (idempotent)
airflow users create   --username "${AIRFLOW_ADMIN_USER:-admin}"   --password "${AIRFLOW_ADMIN_PASSWORD:-admin}"   --firstname "Admin"   --lastname "User"   --role "Admin"   --email "admin@example.com"   || true

# Start scheduler + webserver
airflow scheduler &
exec airflow webserver
