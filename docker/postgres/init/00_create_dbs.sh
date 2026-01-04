#!/usr/bin/env bash
set -euo pipefail

# Create roles if missing
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'EOSQL'
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'airflow') THEN
    CREATE ROLE airflow LOGIN PASSWORD 'airflow';
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'warehouse') THEN
    CREATE ROLE warehouse LOGIN PASSWORD 'warehouse';
  END IF;
END
$$;
EOSQL

# Create databases if missing
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_database WHERE datname='airflow'" | grep -q 1 \
  || psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "CREATE DATABASE airflow OWNER airflow;"

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_database WHERE datname='warehouse'" | grep -q 1 \
  || psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "CREATE DATABASE warehouse OWNER warehouse;"
