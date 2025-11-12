import time
from typing import Dict, List, Tuple
import requests

from .base import PriceSource

CG_URL = "https://api.coingecko.com/api/v3/simple/price"

class CoinGecko(PriceSource):
    name = "coingecko"

    def get_prices(self, assets: List[str]) -> Tuple[Dict[str, float], dict]:
        params = {
            "ids": ",".join(assets),
            "vs_currencies": "usd",
        }
        t0 = time.time()
        r = requests.get(CG_URL, params=params, timeout=10)
        latency_ms = int((time.time() - t0) * 1000)
        meta = {"http_status": r.status_code, "latency_ms": latency_ms, "attempts": 1}
        r.raise_for_status()
        data = r.json()
        prices: Dict[str, float] = {}
        for a in assets:
            node = data.get(a)
            if not node or "usd" not in node:
                continue
            prices[a] = float(node["usd"])
        if not prices:
            raise RuntimeError("CoinGecko returned no prices")
        return prices, meta
