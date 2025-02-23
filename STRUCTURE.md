# Repository Structure

## Overview

The repository is organized following a modular structure that separates different components of the system. Below is a detailed breakdown of each directory and its purpose.

```
├── src/                          # Source code directory
│   ├── exchanges/               # Exchange connectors and interfaces
│   │   ├── __init__.py
│   │   ├── base.py             # Base exchange connector interface
│   │   ├── binance.py          # Binance exchange implementation
│   │   └── hyperliquid.py      # Hyperliquid exchange implementation
│   │
│   ├── data/                   # Data handling and storage
│   │   ├── __init__.py
│   │   ├── collectors.py       # Data collection implementations
│   │   ├── storage.py          # Data storage implementations
│   │   └── validation.py       # Data validation utilities
│   │
│   ├── strategy/               # Trading strategy implementation
│   │   ├── __init__.py
│   │   ├── base.py            # Base strategy interface
│   │   ├── funding_arb.py     # Funding rate arbitrage strategy
│   │   └── risk.py            # Risk management implementation
│   │
│   ├── backtesting/           # Backtesting engine
│   │   ├── __init__.py
│   │   ├── engine.py          # Backtesting engine implementation
│   │   └── metrics.py         # Performance metrics calculation
│   │
│   ├── analysis/              # Analysis and visualization tools
│   │   ├── __init__.py
│   │   ├── metrics.py         # Analysis metrics implementation
│   │   └── visualization.py   # Plotting and visualization tools
│   │
│   └── utils/                 # Utility functions and helpers
│       ├── __init__.py
│       ├── config.py          # Configuration handling
│       ├── logger.py          # Logging setup
│       └── helpers.py         # General helper functions
│
├── docs/                       # Documentation directory
│   ├── hyperliquid_api.md     # Hyperliquid API documentation summary
│   └── binance_api.md         # Binance API documentation summary (to be added)
│
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── test_exchanges/        # Exchange connector tests
│   ├── test_data/            # Data handling tests
│   ├── test_strategy/        # Strategy tests
│   └── test_backtesting/     # Backtesting engine tests
│
├── config/                     # Configuration files
│   ├── config.example.yml     # Example configuration
│   └── config.yml            # Active configuration (gitignored)
│
├── logs/                      # Log files directory
│   └── .gitkeep
│
├── data/                      # Data storage directory
│   ├── historical/           # Historical data storage
│   └── .gitkeep
│
├── notebooks/                 # Jupyter notebooks for analysis
│   └── .gitkeep
│
├── requirements.txt           # Python dependencies
├── README.md                 # Project documentation
├── TODO.md                   # Project task list
├── STRUCTURE.md              # This file
└── .gitignore               # Git ignore rules
```

## Component Details

### src/exchanges/
Contains exchange-specific implementations and the base exchange interface. Each exchange connector inherits from the base class and implements exchange-specific functionality.

### src/data/
Handles all data-related operations including collection, storage, and validation. Implements both historical and real-time data collection.

### src/strategy/
Contains the trading strategy implementation. The funding arbitrage strategy is implemented here along with risk management rules.

### src/backtesting/
Houses the backtesting engine and related components for strategy testing and validation.

### src/analysis/
Contains tools for analyzing trading performance, market conditions, and creating visualizations.

### src/utils/
General utility functions, configuration handling, and logging setup.

### docs/
Contains detailed API documentation summaries and implementation guides.

### tests/
Contains all test files organized by component. Includes both unit and integration tests.

### config/
Configuration files for the application. The actual config file is gitignored to protect sensitive data.

### data/
Storage for historical and collected data. This directory is gitignored except for the .gitkeep file.

### notebooks/
Jupyter notebooks for analysis and strategy development. 