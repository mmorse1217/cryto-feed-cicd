import time
from typing import Dict, List, Tuple
import requests

from .base import PriceSource

CB_URL = "https://api.coinbase.com/v2/exchange-rates"

# Coinbase responds with ticker symbols (BTC, ETH, ...), but the rest of the app
# uses slug-style identifiers (bitcoin, ethereum, ...). Keep a small override
# map so we can keep accepting slugs from callers and translate to tickers for
# Coinbase lookups.
ASSET_SYMBOL_OVERRIDES = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "cardano": "ADA",
    "ripple": "XRP",
    "dogecoin": "DOGE",
    "polkadot": "DOT",
    "litecoin": "LTC",
    "tron": "TRX",
    "binancecoin": "BNB",
}

class Coinbase(PriceSource):
    name = "coinbase"

    def get_prices(self, assets: List[str]) -> Tuple[Dict[str, float], dict]:
        # We request USD base and invert for the asset price in USD.
        params = {"currency": "USD"}
        t0 = time.time()
        r = requests.get(CB_URL, params=params, timeout=10)
        latency_ms = int((time.time() - t0) * 1000)
        meta = {"http_status": r.status_code, "latency_ms": latency_ms, "attempts": 1}
        r.raise_for_status()
        data = r.json().get("data", {}).get("rates", {})
        prices: Dict[str, float] = {}
        for a in assets:
            sym = ASSET_SYMBOL_OVERRIDES.get(a.lower(), a).upper()
            rate = data.get(sym)
            if rate:
                try:
                    prices[a] = 1.0 / float(rate)
                except Exception:
                    continue
        if not prices:
            raise RuntimeError("Coinbase returned no prices")
        return prices, meta
