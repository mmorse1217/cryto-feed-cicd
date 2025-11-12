from .coingecko import CoinGecko
from .coincap import CoinCap
from .binance import Binance
from .coinbase import Coinbase

ALL_SOURCES = [CoinGecko(), CoinCap(), Binance(), Coinbase()]
