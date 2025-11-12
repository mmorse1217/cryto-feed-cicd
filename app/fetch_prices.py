import argparse
import random
import time
from typing import Dict, List, Tuple

from app.sources import ALL_SOURCES
from app.storage.writer import write_snapshot
from app.web.fetch_prices import _backoff, _try_sources

DEFAULT_ASSETS = ["bitcoin", "ethereum", "solana"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch crypto prices and write a timestamped CSV snapshot")
    parser.add_argument(
        "--assets",
        default=",".join(DEFAULT_ASSETS),
        help="Comma-separated asset ids (e.g., bitcoin,ethereum,solana)",
    )
    parser.add_argument("--out", default="data", help="Base output directory")
    return parser.parse_args()


def main():
    args = parse_args()
    assets = [a.strip().lower() for a in args.assets.split(",") if a.strip()]
    source, prices, meta = _try_sources(assets)

    path = write_snapshot(args.out, source, prices, meta)
    print(f"wrote {len(prices)} prices from {source} to {path}")


if __name__ == "__main__":
    main()
