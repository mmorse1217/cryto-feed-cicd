from app.sources.coingecko import CoinGecko
from app.sources.coincap import CoinCap
from app.sources.coinbase import Coinbase

CG_SAMPLE = {"bitcoin": {"usd": 100}, "ethereum": {"usd": 200}}
CC_SAMPLE = {"data": [{"id": "bitcoin", "priceUsd": "101.0"}, {"id": "ethereum", "priceUsd": "202.5"}]}
CB_SAMPLE = {"data": {"rates": {"BTC": "0.001", "ETH": "0.002"}}}

def test_coingecko_parse(monkeypatch):
    class R:
        status_code = 200
        def raise_for_status(self): return None
        def json(self): return CG_SAMPLE
    monkeypatch.setattr("app.sources.coingecko.requests.get", lambda *a, **k: R())
    prices, meta = CoinGecko().get_prices(["bitcoin", "ethereum"])
    assert prices["bitcoin"] == 100
    assert prices["ethereum"] == 200

def test_coincap_parse(monkeypatch):
    class R:
        status_code = 200
        def raise_for_status(self): return None
        def json(self): return CC_SAMPLE
    monkeypatch.setattr("app.sources.coincap.requests.get", lambda *a, **k: R())
    prices, meta = CoinCap().get_prices(["bitcoin", "ethereum"])
    assert prices["bitcoin"] == 101.0
    assert prices["ethereum"] == 202.5

def test_coinbase_parse(monkeypatch):
    class R:
        status_code = 200
        def raise_for_status(self): return None
        def json(self): return CB_SAMPLE
    monkeypatch.setattr("app.sources.coinbase.requests.get", lambda *a, **k: R())
    prices, meta = Coinbase().get_prices(["bitcoin", "ethereum"])
    # 1 / rate
    assert round(prices["bitcoin"], 3) == 1000.0
    assert round(prices["ethereum"], 3) == 500.0
