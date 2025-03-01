from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
import requests
import time
from typing import Dict, List, Optional


class BaseDataCollector(ABC):
    """Base class for collecting historical data from exchanges."""

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """Get historical kline/candlestick data.

        Args:
            symbol: Trading pair symbol
            interval: Kline interval (e.g., '1h', '4h', '1d')
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of records to fetch

        Returns:
            DataFrame with columns: [timestamp, open, high, low, close, volume]
        """
        pass
    @abstractmethod
    def get_historical_funding_rates(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get historical funding rates data.

        Args:
            symbol: Trading pair symbol
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of records to fetch

        Returns:
            DataFrame with columns: [....]
        """
        pass


class BinanceDataCollector(BaseDataCollector):
    """Data collector for Binance Futures."""

    BASE_URL = "https://fapi.binance.com"

    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__(api_key, api_secret)

    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """Get historical kline data from Binance Futures."""
        endpoint = f"{self.BASE_URL}/fapi/v1/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades_count',
                'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
            ])

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_columns] = df[numeric_columns].astype(float)

            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Binance: {e}")
            return pd.DataFrame()

    def get_historical_funding_rates(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get historical kline data from Binance Futures."""

        endpoint = f"{self.BASE_URL}/fapi/v1/fundingRate"
        all_records = []
        current_start = start_time
        while current_start <= end_time:
            params = {
                "symbol": symbol,
                "limit": limit,
                "startTime": current_start,
                "endTime": end_time
            }
            try:
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                if not data:
                    print(f"No data available for time range {current_start} {end_time} in Binance funding rates. Moving forward by 1 day.")
                    current_start += 24 * 60 * 60 * 1000
                    continue
                all_records.extend(data)
                last_time = data[-1]["fundingTime"]
                current_start = last_time + 1
                time.sleep(0.2)
            except Exception as e:
                print(f"Error fetching data from Binance: {e}")
                break

        all_records.sort(key=lambda x: x["fundingTime"])
        return pd.DataFrame.from_records(all_records)


class HyperliquidDataCollector(BaseDataCollector):
    """Data collector for Hyperliquid."""

    BASE_URL = "https://api.hyperliquid.xyz"

    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__(api_key, api_secret)

    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """Get historical kline data from Hyperliquid."""
        endpoint = f"{self.BASE_URL}/info"

        # Convert interval to minutes
        interval_map = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360,
            '12h': 720, '1d': 1440, '1w': 10080
        }

        minutes = interval_map.get(interval)
        if not minutes:
            raise ValueError(f"Unsupported interval: {interval}")

        # Format payload according to Hyperliquid API specs
        payload = {
            "type": "meta",
            "coin": symbol,
            "interval": minutes,
            "limit": limit
        }

        if start_time:
            payload["startTime"] = start_time // 1000  # Convert to seconds
        if end_time:
            payload["endTime"] = end_time // 1000  # Convert to seconds

        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list):
                print(
                    f"Warning: Unexpected response format from Hyperliquid: {data}")
                return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])

            if len(df) > 0:
                # Convert timestamp to datetime (Hyperliquid uses seconds)
                df['timestamp'] = pd.to_datetime(
                    df['timestamp'] * 1000, unit='ms')

                # Convert numeric columns
                numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                df[numeric_columns] = df[numeric_columns].astype(float)

            return df

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Hyperliquid: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    def get_historical_funding_rates(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Retrieve Hyperliquid historical funding data via pagination.
        Returns a sorted list of records.
        """
        url = "https://api.hyperliquid.xyz/info"
        headers = {"Content-Type": "application/json"}

        all_records = []
        current_start = start_time
        while current_start <= end_time:
            payload = {
                "type": "fundingHistory",
                "coin": symbol,
                "startTime": current_start,
                "endTime": end_time
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data:
                    print(f"No data available for time range {current_start} {end_time} in Hyperliquid funding rates. Moving forward by 1 day.")
                    #DEBUG: SHOULD IT BE 1 DAY OR 1 HOUR?
                    current_start += 24 * 60 * 60 * 1000
                    continue
                all_records.extend(data)                
                if len(data) >= limit:
                    last_time = data[-1]["time"]
                    current_start = last_time + 1
                else:
                    break
                time.sleep(0.2)
            except Exception as e:
                print(f"Error fetching data from Hyperliquid: {e}")
                break
        all_records.sort(key=lambda x: x["time"])
        print(all_records)
        return pd.DataFrame.from_records(all_records)

def get_collector(exchange: str) -> BaseDataCollector:
    """Factory function to get the appropriate data collector."""
    collectors = {
        'binance': BinanceDataCollector,
        'hyperliquid': HyperliquidDataCollector
    }

    collector_class = collectors.get(exchange.lower())
    if not collector_class:
        raise ValueError(f"Unsupported exchange: {exchange}")

    return collector_class()
