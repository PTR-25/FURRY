from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import requests
import time
from typing import Dict, List, Optional
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import io
import lz4.frame
import pandas as pd
from typing import Optional

class BinanceDataCollector():
    """Data collector for Binance Futures."""
    
    BASE_URL = "https://fapi.binance.com"
            
    def get_historical_perpetual_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get historical kline data from Binance Futures by looping over pages
        to avoid rate limits.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '1h', '4h', '1d')
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of records per API call (max 1000)

        Returns:
            DataFrame with columns: [timestamp, open, high, low, close, volume]
        """
        endpoint = f"{self.BASE_URL}/fapi/v1/continuousKlines"
        all_data = []
        current_start = start_time

        while True:
            params = {
                "pair": symbol,
                "contractType": "PERPETUAL",
                "interval": interval,
                "limit": limit
            }
            if current_start:
                params["startTime"] = current_start
            if end_time:
                params["endTime"] = end_time

            try:
                response = requests.get(endpoint, params=params)
                # If rate limited, wait before retrying
                if response.status_code == 429:
                    print("Rate limit hit, sleeping for 60 seconds...")
                    time.sleep(60)
                    continue

                response.raise_for_status()
                data = response.json()

                # If no more data is returned, break out of the loop.
                if not data:
                    break

                all_data.extend(data)

                # Last returned timestamp (assumed to be in the first column)
                last_timestamp = data[-1][0]

                # If we reached or passed the end time, or if fewer than `limit` entries were returned,
                # we assume we've fetched all the data.
                if (end_time and last_timestamp >= end_time) or len(data) < limit:
                    break

                # Set the next start time (avoid duplicate data by adding 1 ms)
                current_start = last_timestamp + 1

                # Pause briefly to reduce request frequency.
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from Binance: {e}")
                break

        # Convert accumulated data to a DataFrame.
        df = pd.DataFrame(all_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades_count',
            'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
        ])

        # Convert timestamp to datetime and numeric columns to float.
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_columns] = df[numeric_columns].astype(float)

        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]


class HyperliquidDataCollector():
    """
    Data collector for Hyperliquid's historical perpetual data.
    Since Hyperliquid does not offer this data via their API, we fetch from
    their public AWS S3 bucket.
    """
    
    S3_BUCKET = "hyperliquid-archive"
    S3_PREFIX = "market_data"  # data is stored under market_data/YYYYMMDD/HH/l2Book/<coin>.lz4

    def __init__(self):
        # Create an S3 client that does unsigned (public) requests.
        self.s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    
    def get_historical_perpetual_klines(
        self,
        symbol: str,
        interval: str,  # not used for retrieval; could be used later for aggregation
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500  # not used here
    ) -> pd.DataFrame:
        """
        Fetch historical L2 book snapshots for a given coin from Hyperliquid's S3 archive.
        
        Args:
            symbol: Coin symbol (e.g., "BTC")
            interval: Time interval (e.g., "1h"). This parameter can be used for aggregation if needed.
            start_time: Start time in milliseconds.
            end_time: End time in milliseconds.
            limit: Not used in this implementation.
            
        Returns:
            A pandas DataFrame with the combined data from each available hourly file.
        """
        if start_time is None or end_time is None:
            raise ValueError("start_time and end_time must be provided in milliseconds")
        
        # Convert milliseconds to datetime objects.
        start_dt = datetime.fromtimestamp(start_time / 1000)
        end_dt = datetime.fromtimestamp(end_time / 1000)
        
        current_dt = start_dt
        data_frames = []
        
        # Iterate over each hour in the requested time range.
        while current_dt <= end_dt:
            date_str = current_dt.strftime("%Y%m%d")
            hour_str = current_dt.strftime("%H")
            # Build the S3 key for this hour's L2 book data.
            s3_key = f"{self.S3_PREFIX}/{date_str}/{hour_str}/l2Book/{symbol}.lz4"
            
            try:
                response = self.s3_client.get_object(Bucket=self.S3_BUCKET, Key=s3_key)
                compressed_data = response["Body"].read()
                # Decompress the LZ4 file.
                decompressed_data = lz4.frame.decompress(compressed_data)
                # Assume the decompressed file is in CSV format.
                df_hour = pd.read_csv(io.BytesIO(decompressed_data))
                
                # Optionally convert a timestamp column if it exists.
                if "timestamp" in df_hour.columns:
                    # If timestamps appear to be in seconds, convert them to datetime.
                    if df_hour["timestamp"].max() < 1e12:
                        df_hour["timestamp"] = pd.to_datetime(df_hour["timestamp"], unit='s')
                    else:
                        df_hour["timestamp"] = pd.to_datetime(df_hour["timestamp"], unit='ms')
    
                data_frames.append(df_hour)
                print(f"Fetched data from S3 key: {s3_key}")
            except self.s3_client.exceptions.NoSuchKey:
                print(f"No data found for S3 key: {s3_key}")
            except Exception as e:
                print(f"Error fetching data for S3 key {s3_key}: {e}")
            
            # Move to the next hour.
            current_dt += timedelta(hours=1)
        
        if data_frames:
            full_df = pd.concat(data_frames, ignore_index=True)
            # Optional: Filter rows to ensure timestamps lie within the requested range.
            if "timestamp" in full_df.columns:
                full_df = full_df[
                    (full_df["timestamp"] >= pd.to_datetime(start_time, unit='ms')) &
                    (full_df["timestamp"] <= pd.to_datetime(end_time, unit='ms'))
                ]
            return full_df
        else:
            return pd.DataFrame()
    
    
def get_collector(exchange: str):
    """Factory function to get the appropriate data collector."""
    collectors = {
        'binance': BinanceDataCollector,
        'hyperliquid': HyperliquidDataCollector
    }
    
    collector_class = collectors.get(exchange.lower())
    if not collector_class:
        raise ValueError(f"Unsupported exchange: {exchange}")
        
    return collector_class() 