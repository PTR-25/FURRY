import requests
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Tolerance in milliseconds for matching timestamps between the two APIs
TIME_TOLERANCE_MS = 300000  # 5 minutes

def format_timestamp(ts_ms):
    """Convert a millisecond timestamp to a formatted string including milliseconds."""
    dt = datetime.fromtimestamp(ts_ms / 1000.0)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def get_hyperliquid_funding_history_paginated(coin, start_time=None, end_time=None,
                                              max_records=500, sleep_time=0.2, max_retries=5):
    """
    Retrieve Hyperliquid historical funding data via pagination.
    Returns a sorted list of records.
    """
    url = "https://api.hyperliquid.xyz/info"
    headers = {"Content-Type": "application/json"}
    now_ms = int(time.time() * 1000)
    if end_time is None:
        end_time = now_ms
    if start_time is None:
        one_week_ms = 7 * 24 * 60 * 60 * 1000
        start_time = end_time - one_week_ms

    all_records = []
    current_start = start_time
    retries = 0

    while current_start <= end_time:
        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": current_start,
            "endTime": end_time
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Hyperliquid API error: {response.status_code} {response.text}")
            data = response.json()
            if not data:
                # If no data is returned, move forward by 1 day
                current_start += 24 * 60 * 60 * 1000
                continue
            all_records.extend(data)
            if len(data) >= max_records:
                last_time = data[-1]["time"]
                current_start = last_time + 1
            else:
                break
            retries = 0
            time.sleep(sleep_time)
        except Exception as e:
            retries += 1
            if retries > max_retries:
                break
            time.sleep(2)
    all_records.sort(key=lambda x: x["time"])
    return all_records

def get_binance_funding_history(symbol, start_time=None, end_time=None, max_retries=5):
    """
    Retrieve Binance funding data in batches of 1000.
    Returns a sorted list of records.
    """
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    now_ms = int(time.time() * 1000)
    if end_time is None:
        end_time = now_ms
    if start_time is None:
        one_week_ms = 7 * 24 * 60 * 60 * 1000
        start_time = end_time - one_week_ms

    all_records = []
    current_start = start_time
    retry_count = 0

    while current_start <= end_time:
        params = {
            "symbol": symbol,
            "limit": 1000,
            "startTime": current_start,
            "endTime": end_time
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                raise Exception(f"Binance API error: {response.status_code} {response.text}")
            data = response.json()
            if not data:
                retry_count += 1
                if retry_count > max_retries:
                    break
                time.sleep(1)
                continue
            retry_count = 0
            all_records.extend(data)
            last_time = data[-1]["fundingTime"]
            current_start = last_time + 1
            time.sleep(0.2)
        except Exception as e:
            time.sleep(2)
            continue

    all_records.sort(key=lambda x: x["fundingTime"])
    return all_records

def compare_funding_rates_over_time(hype_coin, binance_symbol, days=7, multiplier=8):
    """
    Retrieve funding data from both APIs over the past `days` days, match records using a timestamp tolerance,
    and return a DataFrame containing:
      - Hyperliquid timestamp and rate (hourly rate, multiplied by multiplier to convert to an equivalent funding period)
      - Binance timestamp and rate
      - Annualized percentage difference computed as:
          diff_rate * 100 * (24/multiplier * 365)
        (For example, with multiplier=8, this is diff_rate * 100 * 1095.)
    """
    now_ms = int(time.time() * 1000)
    start_time = now_ms - (days * 24 * 60 * 60 * 1000)
    hyper_data = get_hyperliquid_funding_history_paginated(hype_coin, start_time, now_ms)
    binance_data = get_binance_funding_history(binance_symbol, start_time, now_ms)
    
    results = []
    i, j = 0, 0
    while i < len(hyper_data) and j < len(binance_data):
        hyper_time = hyper_data[i]["time"]
        binance_time = binance_data[j]["fundingTime"]
        if abs(hyper_time - binance_time) <= TIME_TOLERANCE_MS:
            hyper_rate = float(hyper_data[i]["fundingRate"])
            binance_rate = float(binance_data[j]["fundingRate"])
            # Multiply Hyperliquid's hourly rate by the multiplier (e.g., 8 for an 8h equivalent)
            hyper_adjusted = hyper_rate * multiplier
            diff_rate = hyper_adjusted - binance_rate
            # Annualize the difference:
            # For an 8h funding period, there are 24/8 * 365 = 1095 periods per year.
            # In general, annualized factor = (24/multiplier * 365)
            annualized_diff = diff_rate * (24/multiplier * 365) * 100
            results.append({
                "Timestamp_Hyperliquid": format_timestamp(hyper_time),
                "Timestamp_Binance": format_timestamp(binance_time),
                "Hyperliquid_Rate (%)": hyper_rate * 100,
                "Hyperliquid_Adjusted (%)": hyper_adjusted * 100,
                "Binance_Rate (%)": binance_rate * 100,
                "Annualized_Difference (%)": annualized_diff
            })
            i += 1
            j += 1
        elif hyper_time < binance_time:
            i += 1
        else:
            j += 1

    df = pd.DataFrame(results)
    return df

def plot_funding_rate_difference_over_time(df):
    """Plot the annualized percentage funding rate difference over time from the DataFrame."""
    df["Timestamp"] = pd.to_datetime(df["Timestamp_Hyperliquid"])
    plt.figure(figsize=(12, 6))
    plt.plot(df["Timestamp"], df["Annualized_Difference (%)"], marker='o', linestyle='-', 
             label="Annualized % Difference")
    plt.xlabel("Timestamp")
    plt.ylabel("Annualized Difference (%)")
    plt.title("Annualized % Difference in Funding Rates Over Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example: Retrieve and plot 14 days of data using a multiplier of 4 or 8.
    days_to_fetch = 14
    multiplier = 4  # Set to 8 for an 8h funding period or 4 if applicable
    try:
        df = compare_funding_rates_over_time("ENA", "ENAUSDT", days=days_to_fetch, multiplier=multiplier)
        print(df)
        plot_funding_rate_difference_over_time(df)
    except Exception as e:
        print("An error occurred:", e)
