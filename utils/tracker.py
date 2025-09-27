# utils/tracker.py
import csv
import os
from datetime import datetime
import pandas as pd

CSV_PATH = "downloads.csv"
HEADER = ["timestamp", "seller_name", "pattern_name", "buyer_name", "buyer_email", "license_type", "event", "notes"]

def _ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)

def log_event(seller_name, pattern_name, buyer_name, buyer_email, license_type, event="delivered", notes=""):
    _ensure_csv()
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), seller_name, pattern_name, buyer_name, buyer_email, license_type, event, notes])

def read_events(limit=200):
    _ensure_csv()
    try:
        df = pd.read_csv(CSV_PATH)
        if limit:
            return df.tail(limit)
        return df
    except Exception:
        return None
