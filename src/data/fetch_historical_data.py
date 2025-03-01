import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.data.collectors import get_collector

def fetch_historical_data(
    symbol: str,
    interval: str = '1h',
    days: int = 30,
    save_path: str = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch historical data from both Binance and Hyperliquid.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC' for Hyperliquid, 'BTCUSDT' for Binance)
        interval: Time interval (e.g., '1h', '4h', '1d')
        days: Number of days of historical data to fetch
        save_path: Optional path to save the data
        
    Returns:
        Tuple of (binance_df, hyperliquid_df)
    """
    # Calculate time range
    # end_time = int(datetime.now().timestamp() * 1000)
    #start_time = end_time - (days * 24 * 60 * 60 * 1000)
    # Define your custom dates (format: YYYY-MM-DD)
    start_date_str = "2023-09-01"
    end_date_str = "2023-09-03"

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Convert datetime objects to timestamps in milliseconds
    start_time = int(start_date.timestamp() * 1000)
    end_time = int(end_date.timestamp() * 1000)
    
    # Initialize collectors
    binance_collector = get_collector('binance')
    hyperliquid_collector = get_collector('hyperliquid')
    
    # Fetch data
    print(f"Fetching {days} days of {interval} data for {symbol}...")
    
    binance_symbol = f"{symbol}USDT"  # Binance uses USDT pairs
    binance_df = binance_collector.get_historical_perpetual_klines(
        symbol=binance_symbol,
        interval=interval,
        start_time=start_time,
        end_time=end_time
    )
    
    hyperliquid_df = hyperliquid_collector.get_historical_perpetual_klines(
        symbol=symbol,
        interval=interval,
        start_time=start_time,
        end_time=end_time
    )

    
    print(f"Fetched {len(binance_df)} records from Binance")
    print(f"Fetched {len(hyperliquid_df)} records from Hyperliquid")
    
    # Save data if path provided
    if save_path and (len(binance_df) > 0 or len(hyperliquid_df) > 0):
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if len(binance_df) > 0:
            binance_file = save_dir / f"binance_{symbol}_{interval}.csv"
            binance_df.to_csv(binance_file, index=False)
            print(f"Binance data saved to {binance_file}")
            
        if len(hyperliquid_df) > 0:
            hyperliquid_file = save_dir / f"hyperliquid_{symbol}_{interval}.csv"
            hyperliquid_df.to_csv(hyperliquid_file, index=False)
            print(f"Hyperliquid data saved to {hyperliquid_file}")
    
    return binance_df, hyperliquid_df

if __name__ == "__main__":
    # Example usage
    symbol = "BTC"
    interval = "1h"
    days = 30
    save_path = "data/historical"
    
    binance_df, hyperliquid_df = fetch_historical_data(
        symbol=symbol,
        interval=interval,
        days=days,
        save_path=save_path
    )
    
    # Print some statistics
    print("\nData Summary:")
    
    print("\nBinance:")
    if len(binance_df) > 0:
        print(binance_df.describe())
    else:
        print("No data available")
        
    print("\nHyperliquid:")
    if len(hyperliquid_df) > 0:
        print(hyperliquid_df.describe())
    else:
        print("No data available") 