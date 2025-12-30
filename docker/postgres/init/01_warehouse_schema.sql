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

GRANT USAGE ON SCHEMA raw TO warehouse;
GRANT USAGE ON SCHEMA mart TO warehouse;
