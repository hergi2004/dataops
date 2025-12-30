from __future__ import annotations

import os
import random
import string
from datetime import datetime, timedelta, timezone
import csv
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")

def rid(prefix: str, n: int = 8) -> str:
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)

def gen():
    random.seed(7)
    ensure_dirs()

    customers = []
    for _ in range(500):
        customers.append({
            "customer_id": rid("C_"),
            "email": f"user{random.randint(1,99999)}@example.com",
            "state": random.choice(["IL","TX","CA","NY","FL","WA","MA","OH"]),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))).isoformat(),
        })

    products = []
    for _ in range(200):
        products.append({
            "product_id": rid("P_"),
            "category": random.choice(["coffee","tea","snacks","gear","books"]),
            "price": round(random.uniform(5, 120), 2),
        })

    orders = []
    order_items = []
    now = datetime.now(timezone.utc)
    for _ in range(2000):
        c = random.choice(customers)
        order_id = rid("O_")
        order_ts = now - timedelta(days=random.randint(0, 60), minutes=random.randint(0, 1440))
        status = random.choices(["PLACED","PAID","SHIPPED","CANCELLED"], weights=[40, 35, 20, 5])[0]

        n_items = random.randint(1, 5)
        total = 0.0
        for _i in range(n_items):
            p = random.choice(products)
            qty = random.randint(1, 3)
            line = round(p["price"] * qty, 2)
            total += line
            order_items.append({
                "order_id": order_id,
                "product_id": p["product_id"],
                "category": p["category"],
                "unit_price": p["price"],
                "quantity": qty,
                "line_amount": line,
            })

        orders.append({
            "order_id": order_id,
            "customer_id": c["customer_id"],
            "order_ts": order_ts.isoformat(),
            "status": status,
            "order_total": round(total, 2),
        })

    # Events for Kafka topic (JSONL)
    events_path = os.path.join(RAW_DIR, "order_events.jsonl")
    with open(events_path, "w", encoding="utf-8") as f:
        for o in orders[:1000]:
            base_ts = datetime.fromisoformat(o["order_ts"])
            for ev in ["PLACED", "PAID", "SHIPPED"]:
                if o["status"] == "CANCELLED" and ev != "PLACED":
                    continue
                event = {
                    "event_ts": (base_ts + timedelta(minutes=random.randint(0, 240))).isoformat(),
                    "order_id": o["order_id"],
                    "customer_id": o["customer_id"],
                    "event_type": ev,
                    "amount": o["order_total"],
                    "source": "generator",
                }
                f.write(json.dumps(event) + "\n")

    def write_csv(name: str, rows: list[dict]):
        path = os.path.join(RAW_DIR, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    write_csv("customers.csv", customers)
    write_csv("orders.csv", orders)
    write_csv("order_items.csv", order_items)

    print(f"Wrote raw files to: {RAW_DIR}")
    print(" - customers.csv, orders.csv, order_items.csv, order_events.jsonl")

if __name__ == "__main__":
    gen()
