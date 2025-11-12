import csv
import os
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "data")


def _latest_csv_path(base: str) -> str | None:
    # Walk date folders to find the most recent CSV
    if not os.path.isdir(base):
        return None
    newest: tuple[float, str | None] = (0, None)
    for root, _dirs, files in os.walk(base):
        if os.stat(root).st_mtime <= newest[0]:
            continue
        for f in files:
            if f.endswith('.csv'):
                path = os.path.join(root, f)
                mtime = os.stat(path).st_mtime
                if mtime > newest[0]:
                    newest = (mtime, path)
    return newest[1]


def _requested_assets() -> list[tuple[str, str]]:
    raw_values = [
        value for key in ("coin", "asset")
        for value in request.args.getlist(key)
    ]
    split_values = [
        piece.strip() for value in raw_values for piece in value.split(",")
    ]
    cleaned = [value for value in split_values if value]
    deduped = {value.lower(): value for value in cleaned}
    return [(original, normalized) for normalized, original in deduped.items()]


def _load_latest_snapshot(
) -> tuple[str | None, dict[str, str] | None, dict[str, dict[str, str]]]:
    path = _latest_csv_path(DATA_DIR)
    if not path:
        return None, None, {}
    last_row: dict[str, str] | None = None
    latest_by_asset: dict[str, dict[str, str]] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            last_row = row
            asset = row.get("asset")
            if asset:
                latest_by_asset[asset.lower()] = row
    return path, last_row, latest_by_asset


def _coins_response(path: str, latest_by_asset: dict[str, dict[str, str]],
                    requested: list[tuple[str, str]]):
    coins_payload = {
        original: latest_by_asset.get(normalized) or {
            "error": "price not available in latest snapshot"
        }
        for original, normalized in requested
    }
    missing = [
        original for original, normalized in requested
        if normalized not in latest_by_asset
    ]
    response = {"file": path, "coins": coins_payload}
    if missing:
        response["missing"] = missing
        return jsonify(response), 404
    return jsonify(response)


def _snapshot_response(path: str, last_row: dict[str, str] | None):
    return jsonify({"file": path, "last": last_row})


@app.get("/health")
def health():
    path = _latest_csv_path(DATA_DIR)
    payload = {"time": datetime.utcnow().isoformat()}
    if not path:
        payload.update({
            "status": "degraded",
            "error": "no snapshot available"
        })
    else:
        payload.update({"status": "ok", "snapshot": path})
    return jsonify(payload)


@app.get("/latest")
def latest():
    path, last_row, latest_by_asset = _load_latest_snapshot()
    if not path:
        return jsonify({"error": "no data"}), 404

    requested = _requested_assets()
    if requested:
        return _coins_response(path, latest_by_asset, requested)

    return _snapshot_response(path, last_row)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
