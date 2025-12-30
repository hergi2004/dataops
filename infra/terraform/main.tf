locals {
  # repo root relative to infra/terraform
  project_root = abspath("${path.module}/../..")
}

resource "docker_network" "de_net" {
  name = "de-net"
}

resource "docker_volume" "postgres_data" {
  name = "de-postgres-data"
}

resource "docker_volume" "minio_data" {
  name = "de-minio-data"
}

# Build the Airflow+Pipelines image
resource "docker_image" "airflow" {
  name = "de-airflow:local"
  build {
    context    = "${local.project_root}/docker/airflow"
    dockerfile = "Dockerfile"
  }
}

resource "docker_container" "postgres" {
  name  = "de-postgres"
  image = "postgres:16"

  env = [
    "POSTGRES_PASSWORD=postgres",
    "POSTGRES_USER=postgres",
    "POSTGRES_DB=postgres"
  ]

  networks_advanced {
    name = docker_network.de_net.name
    aliases = ["postgres"]
  }

  ports {
    internal = 5432
    external = 5432
  }

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  volumes {
    host_path      = "${local.project_root}/docker/postgres/init"
    container_path = "/docker-entrypoint-initdb.d"
    read_only      = true
  }
}

resource "docker_container" "minio" {
  name  = "de-minio"
  image = "minio/minio:latest"

  env = [
    "MINIO_ROOT_USER=minioadmin",
    "MINIO_ROOT_PASSWORD=minioadmin"
  ]

  command = ["server", "/data", "--console-address", ":9001"]

  networks_advanced {
    name = docker_network.de_net.name
    aliases = ["minio"]
  }

  ports {
    internal = 9000
    external = 9000
  }

  ports {
    internal = 9001
    external = 9001
  }

  volumes {
    volume_name    = docker_volume.minio_data.name
    container_path = "/data"
  }
}

resource "docker_container" "redpanda" {
  name  = "de-redpanda"
  image = "docker.redpanda.com/redpandadata/redpanda:v24.3.7"

  networks_advanced {
    name = docker_network.de_net.name
    aliases = ["redpanda"]
  }

  # Internal broker: redpanda:9092
  # External broker on host: localhost:19092
  command = [
    "redpanda", "start",
    "--overprovisioned",
    "--smp", "1",
    "--memory", "1G",
    "--reserve-memory", "0M",
    "--node-id", "0",
    "--check=false",
    "--kafka-addr", "PLAINTEXT://0.0.0.0:9092,OUTSIDE://0.0.0.0:19092",
    "--advertise-kafka-addr", "PLAINTEXT://redpanda:9092,OUTSIDE://localhost:19092"
  ]

  ports {
    internal = 19092
    external = 19092
  }

  ports {
    internal = 9644
    external = 9644
  }
}

resource "docker_container" "airflow" {
  name  = "de-airflow"
  image = docker_image.airflow.image_id

  depends_on = [
    docker_container.postgres,
    docker_container.minio,
    docker_container.redpanda
  ]

  networks_advanced {
    name = docker_network.de_net.name
    aliases = ["airflow"]
  }

  ports {
    internal = 8080
    external = 8080
  }

  # Mount repo into container (so you can edit locally and Airflow sees it)
  volumes {
    host_path      = local.project_root
    container_path = "/opt/project"
  }

  env = [
    "PROJECT_ROOT=/opt/project",
    # Airflow auth
    "AIRFLOW_ADMIN_USER=admin",
    "AIRFLOW_ADMIN_PASSWORD=admin",

    # Airflow config
    "AIRFLOW__CORE__LOAD_EXAMPLES=False",
    "AIRFLOW__CORE__DAGS_FOLDER=/opt/project/airflow/dags",
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__WEBSERVER__RBAC=True",

    # Pipeline env
    "POSTGRES_HOST=postgres",
    "POSTGRES_PORT=5432",
    "WAREHOUSE_DB=warehouse",
    "WAREHOUSE_USER=warehouse",
    "WAREHOUSE_PASSWORD=warehouse",

    "MINIO_ENDPOINT=http://minio:9000",
    "MINIO_ACCESS_KEY=minioadmin",
    "MINIO_SECRET_KEY=minioadmin",
    "MINIO_BUCKET=lake",
    "MINIO_REGION=us-east-1",

    "KAFKA_BOOTSTRAP_SERVERS=redpanda:9092",
    "KAFKA_TOPIC=order_events",

    "SPARK_MASTER=local[*]"
  ]
}

# Optional streaming containers
resource "docker_container" "producer" {
  count = var.enable_streaming ? 1 : 0

  name  = "de-producer"
  image = docker_image.airflow.image_id

  depends_on = [docker_container.redpanda]

  networks_advanced {
    name = docker_network.de_net.name
    aliases = ["producer"]
  }

  volumes {
    host_path      = local.project_root
    container_path = "/opt/project"
  }

  command = ["bash", "-lc", "python /opt/project/pipelines/produce_events.py --rate 5"]

  env = docker_container.airflow.env
}

resource "docker_container" "stream_consumer" {
  count = var.enable_streaming ? 1 : 0

  name  = "de-stream-consumer"
  image = docker_image.airflow.image_id

  depends_on = [
    docker_container.redpanda,
    docker_container.postgres
  ]

  networks_advanced {
    name = docker_network.de_net.name
    aliases = ["stream-consumer"]
  }

  volumes {
    host_path      = local.project_root
    container_path = "/opt/project"
  }

  command = ["bash", "-lc", "python /opt/project/pipelines/spark_stream_events.py"]

  env = docker_container.airflow.env
}
