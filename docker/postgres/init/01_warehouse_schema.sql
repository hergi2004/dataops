\connect warehouse;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS mart;

-- Streaming landing table (created if missing by the consumer too)
CREATE TABLE IF NOT EXISTS raw.order_events (
  event_ts      TIMESTAMPTZ NOT NULL,
  order_id      TEXT NOT NULL,
  event_type    TEXT NOT NULL,
  amount        NUMERIC(12,2),
  customer_id   TEXT,
  source        TEXT,
  inserted_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Allow warehouse role to create/write tables in raw and mart
GRANT USAGE, CREATE ON SCHEMA raw TO warehouse;
GRANT USAGE, CREATE ON SCHEMA mart TO warehouse;

-- Ensure current and future tables are writable
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO warehouse;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mart TO warehouse;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT ALL PRIVILEGES ON TABLES TO warehouse;
ALTER DEFAULT PRIVILEGES IN SCHEMA mart GRANT ALL PRIVILEGES ON TABLES TO warehouse;
