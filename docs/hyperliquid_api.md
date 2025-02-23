# Hyperliquid API Documentation Summary

## Base URLs
- REST API: `https://api.hyperliquid.xyz`
- WebSocket: `wss://api.hyperliquid.xyz/ws`

## Common Headers
```
Content-Type: application/json
```

## Endpoints Overview

### Info Endpoint (`/info`)
Primary endpoint for fetching exchange and user information.

#### Key Operations
1. **Funding Rates**
   - `fundingHistory`: Historical funding rates
   - `predictedFundings`: Current rates across venues
   - `metaAndAssetCtxs`: Current market state including funding

2. **Market Data**
   - `meta`: Get perpetuals metadata
   - `allMids`: Get mid prices for all coins
   - `L2Book`: L2 orderbook snapshot
   - `candles`: Get candlestick data

3. **User Data**
   - `clearinghouseState`: Account summary
   - `openOrders`: User's open orders
   - `userFills`: Trade history
   - `userFunding`: Funding payment history

### Exchange Endpoint (`/exchange`)
Endpoint for trading operations.

#### Key Operations
1. **Order Management**
   - Place orders
   - Cancel orders
   - Modify orders
   - Close positions

2. **Position Management**
   - Get positions
   - Adjust leverage
   - Transfer margin

## WebSocket API

### Subscriptions
1. **Market Data**
   ```json
   {
     "method": "subscribe",
     "subscription": {
       "type": "l2Book",
       "coin": "BTC"
     }
   }
   ```

2. **User Data**
   ```json
   {
     "method": "subscribe",
     "subscription": {
       "type": "userEvents",
       "user": "0x..."
     }
   }
   ```

### Important Concepts

#### Asset IDs
- Perpetuals: Use coin name (e.g., "BTC", "ETH")
- Spot: Use format "@{index}" or "TOKEN/USDC"

#### Tick and Lot Sizes
- Each asset has specific tick (price) and lot (size) size requirements
- Retrieved via `meta` endpoint

#### Rate Limits
- Info endpoint: Weight-based system
- Exchange endpoint: Stricter limits
- WebSocket: Connection and subscription limits

#### Error Handling
Common error codes:
- 429: Rate limit exceeded
- 400: Invalid request
- 401: Unauthorized
- 403: Forbidden

## Authentication
1. API Wallets required for trading
2. Nonce-based authentication system
3. Signature verification for secure operations

## Best Practices
1. Use WebSocket for real-time data
2. Implement rate limiting
3. Handle reconnection logic
4. Validate responses
5. Use appropriate error handling

## Example Responses

### Funding Rate Response
```json
{
    "coin": "ETH",
    "fundingRate": "-0.00022196",
    "premium": "-0.00052196",
    "time": 1683849600076
}
```

### Order Response
```json
{
    "coin": "BTC",
    "limitPx": "29792.0",
    "oid": 91490942,
    "side": "A",
    "sz": "0.0",
    "timestamp": 1681247412573
}
```

### Position Response
```json
{
    "position": {
        "coin": "ETH",
        "entryPx": "2986.3",
        "leverage": {
            "value": 20,
            "type": "isolated"
        },
        "liquidationPx": "2866.26936529",
        "marginUsed": "4.967826",
        "szi": "0.0335"
    }
}
```

## Implementation Notes
1. Always handle pagination for historical data
2. Implement proper error handling and retries
3. Use WebSocket for real-time data updates
4. Maintain connection heartbeats
5. Validate all responses before processing 