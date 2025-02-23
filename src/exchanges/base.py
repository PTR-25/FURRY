from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd

class BaseExchange(ABC):
    """Base class for exchange connectors."""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """Initialize the exchange connector.
        
        Args:
            api_key: API key for the exchange
            api_secret: API secret for the exchange
            testnet: Whether to use testnet
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
    
    @abstractmethod
    def get_funding_rate(self, symbol: str) -> float:
        """Get current funding rate for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current funding rate as a float
        """
        pass
    
    @abstractmethod
    def get_historical_funding_rates(
        self, 
        symbol: str, 
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> pd.DataFrame:
        """Get historical funding rates.
        
        Args:
            symbol: Trading pair symbol
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            
        Returns:
            DataFrame with historical funding rates
        """
        pass
    
    @abstractmethod
    def get_historical_prices(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> pd.DataFrame:
        """Get historical candlestick data.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            
        Returns:
            DataFrame with OHLCV data
        """
        pass
    
    @abstractmethod
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        leverage: Optional[float] = None
    ) -> Dict:
        """Place an order on the exchange.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market' or 'limit')
            quantity: Order quantity
            price: Order price (required for limit orders)
            leverage: Leverage to use
            
        Returns:
            Order details as a dictionary
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Dict:
        """Get current position for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Position details as a dictionary
        """
        pass
    
    @abstractmethod
    def close_position(self, symbol: str) -> Dict:
        """Close position for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Order details for the closing trade
        """
        pass 