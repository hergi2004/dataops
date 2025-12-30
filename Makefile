SHELL := /bin/bash

TF_DIR := infra/terraform

.PHONY: help init up down logs status airflow bootstrap run_dag psql minio_console stream_up stream_down

help:
	@echo "Targets:"
	@echo "  make init        - terraform init"
	@echo "  make up          - terraform apply (starts stack)"
	@echo "  make down        - terraform destroy (stops stack)"
	@echo "  make status      - show running containers"
	@echo "  make logs        - tail airflow logs"
	@echo "  make airflow     - open Airflow UI info"
	@echo "  make bootstrap   - create MinIO bucket + quick warehouse checks"
	@echo "  make run_dag     - trigger the end-to-end DAG once"
	@echo "  make psql        - open psql into warehouse db"
	@echo "  make minio_console - show MinIO console url"
	@echo "  make stream_up   - start Kafka producer + Spark streaming consumer"
	@echo "  make stream_down - stop streaming containers (if enabled)"

init:
	cd $(TF_DIR) && terraform init

up:
	cd $(TF_DIR) && terraform apply -auto-approve

down:
	cd $(TF_DIR) && terraform destroy -auto-approve

status:
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

logs:
	@docker logs -f de-airflow | tail -n 200

airflow:
	@echo "Airflow UI: http://localhost:8080"
	@echo "Default user/pass from .env: admin/admin (change it!)"

bootstrap:
	@docker exec -it de-airflow bash -lc "python pipelines/bootstrap.py"

run_dag:
	@docker exec -it de-airflow bash -lc "airflow dags trigger de_end_to_end && airflow dags list-runs -d de_end_to_end | head"

psql:
	@docker exec -it de-postgres psql -U warehouse -d warehouse

minio_console:
	@echo "MinIO API:     http://localhost:9000"
	@echo "MinIO Console: http://localhost:9001"
	@echo "User/pass from .env: minioadmin/minioadmin"

stream_up:
	cd $(TF_DIR) && terraform apply -auto-approve -var enable_streaming=true

stream_down:
	cd $(TF_DIR) && terraform apply -auto-approve -var enable_streaming=false
