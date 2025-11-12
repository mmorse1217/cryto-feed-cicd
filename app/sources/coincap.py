import time
from typing import Dict, List, Tuple
import requests

from .base import PriceSource

CC_URL = "https://api.coincap.io/v2/assets"

class CoinCap(PriceSource):
    name = "coincap"

    def get_prices(self, assets: List[str]) -> Tuple[Dict[str, float], dict]:
        params = {"ids": ",".join(assets)}
        t0 = time.time()
        r = requests.get(CC_URL, params=params, timeout=10)
        latency_ms = int((time.time() - t0) * 1000)
        meta = {"http_status": r.status_code, "latency_ms": latency_ms, "attempts": 1}
        r.raise_for_status()
        payload = r.json()
        data = payload.get("data", [])
        prices: Dict[str, float] = {}
        for item in data:
            asset_id = item.get("id")
            price = item.get("priceUsd")
            if asset_id and price is not None:
                prices[asset_id] = float(price)
        if not prices:
            raise RuntimeError("CoinCap returned no prices")
        return prices, meta
