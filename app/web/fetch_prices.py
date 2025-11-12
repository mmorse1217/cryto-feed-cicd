import os
import random
import threading
import time
from datetime import datetime
from typing import Dict, List, Tuple

from flask import Flask, jsonify

from app.sources import ALL_SOURCES
from app.storage.writer import write_snapshot

app = Flask(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "data")
DEFAULT_ASSETS = ["bitcoin", "ethereum", "solana"]
FETCH_ASSETS = [
    asset.strip().lower()
    for asset in os.environ.get("FETCH_ASSETS", ",".join(DEFAULT_ASSETS)).split(",")
    if asset.strip()
]
FETCH_INTERVAL_SECONDS = int(os.environ.get("FETCH_INTERVAL_SECONDS", "60"))

_state_lock = threading.Lock()
_fetch_lock = threading.Lock()
_worker_lock = threading.Lock()
_worker_started = False
_state = {
    "status": "idle",
    "last_run": None,
    "last_success": None,
    "last_error": None,
    "last_source": None,
    "last_path": None,
    "prices": 0,
}


def _assets() -> List[str]:
    return FETCH_ASSETS if FETCH_ASSETS else DEFAULT_ASSETS


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _backoff(base: float = 0.5, factor: float = 2.0, jitter: float = 0.2, attempt: int = 0) -> None:
    delay = base * (factor ** attempt)
    delay *= random.uniform(1 - jitter, 1 + jitter)
    time.sleep(min(delay, 10.0))


def _try_sources(assets: List[str]) -> Tuple[str, Dict[str, float], dict]:
    last_exc = None
    for i, src in enumerate(ALL_SOURCES):
        try:
            prices, meta = src.get_prices(assets)
            return src.name, prices, meta
        except Exception as exc:  # pragma: no cover - relies on live APIs
            last_exc = exc
            if i < len(ALL_SOURCES) - 1:
                _backoff(attempt=i)
    raise RuntimeError(f"all sources failed: {last_exc}")


def _update_state(**kwargs) -> None:
    with _state_lock:
        _state.update(kwargs)


def _perform_fetch() -> str:
    with _fetch_lock:
        _update_state(status="fetching", last_run=_now_iso(), last_error=None)
        assets = _assets()
        source, prices, meta = _try_sources(assets)
        path = write_snapshot(DATA_DIR, source, prices, meta)
        _update_state(
            status="ok",
            last_success=_now_iso(),
            last_source=source,
            last_path=path,
            prices=len(prices),
        )
        return path


def _fetch_loop() -> None:
    interval = max(FETCH_INTERVAL_SECONDS, 5)
    while True:
        started = time.monotonic()
        try:
            _perform_fetch()
        except Exception as exc:  # pragma: no cover - defensive logging
            _update_state(status="error", last_error=str(exc))
        elapsed = time.monotonic() - started
        sleep_for = max(0.0, interval - elapsed)
        time.sleep(sleep_for)


def ensure_worker() -> None:
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        thread = threading.Thread(target=_fetch_loop, name="price-fetcher", daemon=True)
        thread.start()
        _worker_started = True


def _snapshot_state() -> dict:
    with _state_lock:
        return dict(_state)


@app.get("/health")
def health():
    state = _snapshot_state()
    payload = {
        "status": state["status"],
        "time": _now_iso(),
        "last_success": state["last_success"],
        "last_error": state["last_error"],
    }
    if state["last_path"]:
        payload["last_path"] = state["last_path"]
    if state["last_source"]:
        payload["last_source"] = state["last_source"]
    payload["prices"] = state["prices"]
    status_code = 200 if state["status"] == "ok" else 503
    return jsonify(payload), status_code


@app.get("/status")
def status():
    state = _snapshot_state()
    state["time"] = _now_iso()
    return jsonify(state)


@app.post("/fetch")
def fetch_now():
    try:
        path = _perform_fetch()
        state = _snapshot_state()
        return jsonify({"status": "ok", "file": path, "prices": state["prices"]})
    except Exception as exc:
        _update_state(status="error", last_error=str(exc))
        return jsonify({"status": "error", "error": str(exc)}), 500


ensure_worker()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("FETCH_PORT", os.environ.get("PORT", 8001))))
