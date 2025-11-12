from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class PriceSource(ABC):
    name: str

    @abstractmethod
    def get_prices(self, assets: List[str]) -> Tuple[Dict[str, float], dict]:
        """
        Return (prices, meta)
        - prices: mapping asset -> price in USD (float)
        - meta:   dict with optional keys {"http_status", "latency_ms", "attempts"}
        Should raise Exception on logical/HTTP errors so the caller can failover.
        """
        raise NotImplementedError
