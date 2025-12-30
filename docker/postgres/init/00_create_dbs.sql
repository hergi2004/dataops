-- Create Airflow metadata DB + user
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'airflow') THEN
    CREATE ROLE airflow LOGIN PASSWORD 'airflow';
  END IF;
END
$$;

DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow') THEN
    CREATE DATABASE airflow OWNER airflow;
  END IF;
END
$$;

-- Create Warehouse DB + user
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'warehouse') THEN
    CREATE ROLE warehouse LOGIN PASSWORD 'warehouse';
  END IF;
END
$$;

DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'warehouse') THEN
    CREATE DATABASE warehouse OWNER warehouse;
  END IF;
END
$$;
