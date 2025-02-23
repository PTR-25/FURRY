# Binance USDⓈ-M Futures API Documentation

## Base URLs and Endpoints

- **Production REST API Base URL**: `https://fapi.binance.com`
- **Production WebSocket Base URL**: `wss://stream.binancefuture.com`
- **Testnet REST API Base URL**: `https://testnet.binancefuture.com`
- **Testnet WebSocket Base URL**: `wss://stream.binancefuture.com`

## General Information

### Rate Limits and IP Restrictions

- Rate limits are based on IP addresses, not API keys
- Response headers contain rate limit counters:
  - `X-MBX-USED-WEIGHT-(intervalNum)(intervalLetter)`: Current IP usage
  - `X-MBX-ORDER-COUNT-(intervalNum)(intervalLetter)`: Current order count
- HTTP 429 returned when rate limit violated
- Repeated violations lead to IP bans (HTTP 418)
- IP bans scale from 2 minutes to 3 days for repeat offenders

### HTTP Return Codes

- HTTP 4XX: Malformed requests (client-side issue)
- HTTP 403: WAF Limit violation
- HTTP 429: Rate limit breach
- HTTP 418: Auto-ban for repeated 429s
- HTTP 5XX: Internal errors (Binance-side issue)

### Authentication

- HMAC SHA256 or RSA signatures supported
- Supports PKCS#8 format for RSA keys
- Timing security: Server time synchronization required
- Request parameters must be sorted alphabetically

### Market Data Endpoints

All endpoints are documented in detail at [Binance Futures Documentation](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)

#### Key Endpoints:

1. **Server Time**
   - Endpoint: `/fapi/v1/time`
   - Method: GET
   - Weight: 1

2. **Exchange Information**
   - Endpoint: `/fapi/v1/exchangeInfo`
   - Method: GET
   - Weight: 1

3. **Kline/Candlestick Data**
   - Endpoint: `/fapi/v1/klines`
   - Method: GET
   - Weight: Based on parameters

4. **Mark Price**
   - Endpoint: `/fapi/v1/premiumIndex`
   - Method: GET
   - Weight: 1

5. **Funding Rate**
   - History Endpoint: `/fapi/v1/fundingRate`
   - Current Rate: `/fapi/v1/premiumIndex`
   - Weight: 1

6. **Price Ticker**
   - Endpoint: `/fapi/v2/ticker/price`
   - Method: GET
   - Weight: 2

7. **Order Book**
   - Endpoint: `/fapi/v1/ticker/bookTicker`
   - Method: GET
   - Weight: 2

### Best Practices

1. Use WebSocket streams for real-time data when possible
2. Implement proper rate limit handling
3. Keep server time synchronized
4. Handle errors appropriately
5. Use appropriate error handling and retries

### SDK Information

Official Python SDK:
```bash
pip install binance-futures-connector
```

Official Java SDK:
```bash
git clone https://github.com/binance/binance-futures-connector-java.git
```

For detailed endpoint specifications, parameters, and response formats, please refer to the [official documentation](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info). 