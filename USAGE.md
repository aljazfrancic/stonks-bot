# Usage Guide

## Run Locally
```bash
git clone https://github.com/aljazfrancic/stonks-bot.git
cd stonks-bot && ./scripts/setup.sh
# Edit .env with your API keys:
# DISCORD_TOKEN=your_token
# POLYGON=your_polygon_key
# COINGECKO=your_coingecko_key
python bot.py
```

## How to Use

### Basic Commands
```
!stonks                   # Default portfolio (BTC, ETH, XMR, AVAX)
!stonks 7                 # 7-day chart
!stonks 30 BTC ETH        # 30-day BTC/ETH chart
!stonks 365 X:AAPL X:MSFT # 1-year Apple/Microsoft chart
```

### Supported Tickers
- **Cryptocurrencies**: `BTC`, `ETH`, `SOL` (via CoinGecko)
- **Stocks**: `X:AAPL`, `X:MSFT`, `X:GOOG` (via Polygon.io)

## Requirements
- Python 3.12 or higher
- Discord Bot Token
- Polygon.io API Key
- CoinGecko API Key (optional)

## Testing

```bash
python test_stonks.py
```

## Features

- Multi-API support (Polygon.io + CoinGecko)
- Automatic provider selection
- Comprehensive error handling
- Rate limit protection
- Auto-updating demo charts (hourly)
