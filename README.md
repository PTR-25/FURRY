# Crypto Funding Rates Arbitrage

A Python-based system for analyzing and executing funding rate arbitrage opportunities between perpetual futures markets across different cryptocurrency exchanges.

## Features

- Real-time funding rate monitoring for Hyperliquid and Binance
- Historical data collection and analysis
- Backtesting engine for strategy validation
- Visualization tools for funding rate differences
- Automated trade execution (planned)

## Project Structure

```
├── src/
│   ├── exchanges/      # Exchange-specific implementations
│   ├── data/          # Data collection and storage
│   ├── strategy/      # Trading strategy implementation
│   ├── backtesting/   # Backtesting engine
│   ├── analysis/      # Data analysis and visualization
│   └── utils/         # Helper functions and utilities
├── tests/             # Unit and integration tests
├── config/            # Configuration files
├── logs/              # Application logs
├── data/              # Historical and cached data
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-funding-arbitrage.git
cd crypto-funding-arbitrage
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example configuration file and add your API keys:
```bash
cp config/config.example.yml config/config.yml
```

## Usage

1. Configure your API keys in `config/config.yml`
2. Run the data collection script:
```bash
python src/data/collect_historical_data.py
```

3. Run the backtesting engine:
```bash
python src/backtesting/run_backtest.py
```

## Strategy

The basic strategy involves:
1. Monitoring funding rate differences between exchanges
2. Opening positions when the annualized funding rate difference exceeds 10%
3. Closing positions when the difference falls below the threshold
4. Managing risk through position sizing and stop-loss orders

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Cryptocurrency trading carries significant risks. Use at your own risk.
