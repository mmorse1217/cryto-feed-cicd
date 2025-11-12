import csv
import os
from datetime import datetime, timezone
from typing import Dict

SCHEMA = ["timestamp_utc", "source", "asset", "price_usd", "http_status", "latency_ms", "attempt"]

def _ensure_dir(base_out: str) -> str:
    now = datetime.now(timezone.utc)
    dirpath = os.path.join(base_out, f"{now.year:04d}", f"{now.month:02d}", f"{now.day:02d}")
    os.makedirs(dirpath, exist_ok=True)
    return dirpath

def write_snapshot(base_out: str, source: str, prices: Dict[str, float], meta: dict) -> str:
    dirpath = _ensure_dir(base_out)
    now = datetime.now(timezone.utc)
    fname = f"prices-{now.hour:02d}{now.minute:02d}.csv"
    fpath = os.path.join(dirpath, fname)

    file_exists = os.path.exists(fpath)
    with open(fpath, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        if not file_exists:
            w.writeheader()
        for asset, price in prices.items():
            w.writerow({
                "timestamp_utc": now.isoformat(),
                "source": source,
                "asset": asset,
                "price_usd": price,
                "http_status": meta.get("http_status"),
                "latency_ms": meta.get("latency_ms"),
                "attempt": meta.get("attempts"),
            })
    return fpath
