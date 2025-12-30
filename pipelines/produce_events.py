from __future__ import annotations

import argparse
import json
import os
import time
from kafka import KafkaProducer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVENTS = os.path.join(ROOT, "data", "raw", "order_events.jsonl")

def main(rate: int):
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
    topic = os.getenv("KAFKA_TOPIC", "order_events")

    producer = KafkaProducer(
        bootstrap_servers=bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8"),
        linger_ms=50,
    )

    if not os.path.exists(EVENTS):
        raise SystemExit("Missing data/raw/order_events.jsonl. Run pipelines/generate_data.py first.")

    with open(EVENTS, "r", encoding="utf-8") as f:
        for line in f:
            ev = json.loads(line)
            key = ev["order_id"]
            producer.send(topic, key=key, value=ev)
            producer.flush()
            time.sleep(1 / max(rate, 1))

    print(f"✅ Published events to topic '{topic}' at ~{rate}/sec.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=int, default=5, help="events per second")
    args = ap.parse_args()
    main(args.rate)
