import requests
import time
from typing import Dict, List, Optional
from django.conf import settings
import logging

logger = logging.getLogger('trading_analysis')

class BinanceClient:
    def __init__(self):
        self.base_url = settings.BINANCE_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradingAnalysis/1.0'
        })

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance API error: {e}")
            raise Exception(f"Binance API unavailable: {str(e)}")

    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[List]:
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        logger.info(f"Fetching klines: {symbol} | {interval} | {limit}")
        return self._make_request(endpoint, params)

    def get_order_book(self, symbol: str, limit: int = 1000) -> Dict:
        endpoint = "/api/v3/depth"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        logger.info(f"Fetching order book: {symbol} | {limit}")
        return self._make_request(endpoint, params)

    def get_24hr_ticker(self, symbol: str) -> Dict:
        endpoint = "/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        logger.info(f"Fetching 24hr ticker: {symbol}")
        return self._make_request(endpoint, params)

    def get_exchange_info(self) -> Dict:
        endpoint = "/api/v3/exchangeInfo"
        return self._make_request(endpoint)

    def get_symbols(self) -> List[str]:
        exchange_info = self.get_exchange_info()
        symbols = []
        for symbol_info in exchange_info['symbols']:
            if symbol_info['status'] == 'TRADING' and symbol_info['quoteAsset'] == 'USDT':
                symbols.append(symbol_info['symbol'])
        return sorted(symbols)