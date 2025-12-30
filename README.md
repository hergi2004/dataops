# Local Data Engineering End-to-End Lab (Terraform + Docker)

This repo spins up a **local** data-engineering stack with **Terraform** using the Docker provider:

- **Postgres** (warehouse)
- **MinIO** (S3-compatible data lake)
- **Redpanda** (Kafka-compatible broker)
- **Airflow** (orchestration + runs the pipelines)
- Optional: **Streaming** container (Spark Structured Streaming consumer + Python producer)

You’ll build a small end-to-end pipeline:
1) Generate synthetic raw data (CSV/JSONL)
2) Pandas ETL → Parquet + upload to MinIO
3) PySpark batch load → Postgres (raw schema)
4) dbt models → star schema + marts (mart schema)
5) Airflow DAG orchestrates (1→4)
6) Optional: Kafka → Spark streaming → Postgres (raw.order_events)

---

## Prereqs

- Docker Desktop (or Docker Engine)
- Terraform (>= 1.5)
- `make` (or just run the commands manually)

> Windows: Use WSL2 + Docker Desktop. Run commands from WSL.

---

## Quick start

```bash
cp .env.example .env
make init
make up
make status
```

Open Airflow:
- http://localhost:8080  
Login: `admin` / `admin` (from `.env`, change it if you care)

Create the MinIO bucket + sanity checks:
```bash
make bootstrap
```

Trigger the pipeline once:
```bash
make run_dag
```

---

## What to look at (learning checklist)

### SQL + Modeling
- `dbt/models/marts/*` shows a simple **star schema**:
  - `dim_customers`
  - `fct_orders`
  - `fct_revenue_daily`

### Python ETL
- `pipelines/etl_pandas.py` cleans + writes Parquet and uploads to MinIO

### Spark
- `pipelines/spark_batch_load.py` reads Parquet and loads to Postgres via JDBC

### Orchestration (Airflow)
- `airflow/dags/de_end_to_end.py` runs the whole thing

### Streaming (optional)
Enable streaming containers:
```bash
make stream_up
```
Then watch events accumulate:
```bash
make psql
# in psql:
select count(*) from raw.order_events;
```

Disable streaming:
```bash
make stream_down
```

---

## Tear down

```bash
make down
```

---

## Notes / gotchas

- This is a **learning lab**, not production.
- Spark runs via **PySpark** inside the Airflow container (so you get real Spark APIs locally).
- If you want this on Kubernetes later, easiest path is: **k3d + Helm charts**. But don’t hide behind “k8s” if you can’t explain the pipeline logic.

