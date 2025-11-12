import time
from typing import Dict, List, Tuple
import requests

from .base import PriceSource

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

class Binance(PriceSource):
    name = "binance"

    def _symbol(self, asset: str) -> str:
        # Map common ids to Binance symbols
        mapping = {
            "bitcoin": "BTCUSDT",
            "ethereum": "ETHUSDT",
            "solana": "SOLUSDT",
        }
        return mapping.get(asset.lower(), f"{asset.upper()}USDT")

    def get_prices(self, assets: List[str]) -> Tuple[Dict[str, float], dict]:
        prices: Dict[str, float] = {}
        http_status = 200
        attempts = 0
        t0 = time.time()
        for a in assets:
            attempts += 1
            sym = self._symbol(a)
            r = requests.get(BINANCE_URL, params={"symbol": sym}, timeout=10)
            http_status = r.status_code
            r.raise_for_status()
            j = r.json()
            p = j.get("price")
            if p is not None:
                prices[a] = float(p)  # quoted in USDT ~ USD
        latency_ms = int((time.time() - t0) * 1000)
        if not prices:
            raise RuntimeError("Binance returned no prices")
        meta = {"http_status": http_status, "latency_ms": latency_ms, "attempts": attempts}
        return prices, meta
